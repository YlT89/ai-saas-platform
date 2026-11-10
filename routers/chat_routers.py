from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlmodel import Session ,select
import tiktoken
from langchain_openai import ChatOpenAI
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

# 导入项目内的依赖
from db.session import get_db
from dependencies.auth import get_active_user
from models.user import User
from models.chat import ChatMessage
from schemas.chat_schemas import ChatRequest
from core.config import settings
from core.Tookls.weather import get_weather



# 对了，记得前端输入的时候不要在JSON字符串里加“”
def truncate_messages(messages: list, max_tokens: int = 3000):
    """从最老的消息开始删，直到总 Token 数小于限制"""
    encoding = tiktoken.get_encoding("cl100k_base")
    total_tokens = sum(len(encoding.encode(msg["content"])) for msg in messages)

    # 只要超了，就从最早的开始剔除（保留第一条 System Prompt）
    while total_tokens > max_tokens and len(messages) > 1:
        removed_msg = messages.pop(1)  # 索引0通常是System人设，不能删，所以从1开始删
        total_tokens -= len(encoding.encode(removed_msg["content"]))
    return messages



# 1、初始化大模型客户端 (使用 DeepSeek)
api_key = settings.api_key
if not api_key:
    raise ValueError("请在 .env 中配置 API_KEY")      # 记得这个和.env7里面的要一致
client = ChatOpenAI(model='deepseek-flash', api_key=api_key, base_url="https://api.deepseek.com")


chat_router = APIRouter(prefix="/chat", tags=["AI 对话"])


@chat_router.post("/ask")
async def chat_with_ai(
        req: ChatRequest,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_active_user)  # 鉴权：只允许登录用户提问
):
    # 2、先查历史记录（此时数据库里还没有当前问题）
    history_records = db.exec(select(ChatMessage).where(ChatMessage.user_id == current_user.id).order_by(
        ChatMessage.create_time.desc()).limit(9)).all()     # .limit(9) 滑动窗口，只取最近 9 条消息。这是最常用的防破产策略
    history_records.reverse()

    # 3、绑定工具
    tools = [get_weather]

    # 4、定义提示词模板
    prompt = ChatPromptTemplate([
        ("system", "你是一个得力的助手。"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),  # 给工具留的位置
    ])

    # 3、创建 Agent
    agent = create_tool_calling_agent(client, tools, prompt)


    # 3、构造发给大模型的 messages
    messages = []
    for msg in history_records:
        messages.append({"role": msg.role_type, "content": msg.content, 'tool': agent})

    # 4、执行截断
    messages = truncate_messages(messages, max_tokens=3000)

    # 5、拼装当前问题
    messages.append({"role": "user", "content": req.question})

    # 如果ai判断需要工具
    agent_executor = AgentExecutor(agent=agent, tools=tools, prompt=prompt)

    # 6、现在再去把当前问题存入数据库
    user_msg = ChatMessage(
        user_id=current_user.id,
        role_type="user",
        content=req.question
    )
    db.add(user_msg)
    db.commit()

    # 7、定义异步生成器（负责流式返回，并在最后把 AI 回答存入数据库）
    async def stream_generator():
        full_ai_response = ""  # 用来收集 AI 完整回答的缓冲器

        try:
            # 遍历大模型返回的流式数据包(核心：使用 astream 替代 ainvoke）
            async for event in agent_executor.astream({'input': req.question}):
                # langchain 的 Agent 流式输出会返回不同的事件类型
                if 'actions' in event:
                    yield f'data: [用工具呢等会...]\n\n'
                elif 'steps' in event:
                    # 工具执行结果
                    for step in event['steps']:
                        yield f'data: [出结果了: {step.observation}\n\n'     # 注意别下标去访问

                elif 'output' in event:
                    # 大模型开始润色了
                    content = event['output']
                    full_ai_response += content
                    yield f'data: {content}\n\n'

            yield 'data: [DONE]\n\n'

        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"
            full_ai_response = "抱歉，生成回复时出错了。"

        finally:
            # 8、核心：无论流式是否报错，结束时都把 AI 的完整回答存入数据库
            if full_ai_response:
                ai_msg = ChatMessage(
                    user_id=current_user.id,
                    role_type="assistant",
                    content=full_ai_response
                )
                db.add(ai_msg)
                db.commit()

    # 9、返回流式响应
    return StreamingResponse(
        stream_generator(),
        media_type="text/event-stream"
    )




@chat_router.post("/weather")
async def chat_with_weather(req: ChatRequest):
    # 1、把工具绑到大模型上 (DeepSeek 支持工具调用)
    llm = ChatOpenAI(model='deepseek-flash', api_key=api_key, base_url="https://api.deepseek.com")
    tools = [get_weather]

    # 2、定义提示词模板
    prompt = ChatPromptTemplate([
        ("system", "你是一个得力的助手。"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),      # 给工具留的位置
    ])

    # 3、创建 Agent
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, prompt=prompt)

    # 执行
    result = await agent_executor.ainvoke({'input': req.question})
    return {'answer': result['output']}