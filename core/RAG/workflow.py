from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_redis import RedisVectorStore

from core.RAG.rerank_app import rerank_text
from core.config import settings

# 1. 定义真实状态（带上必要的参数）
class AgentState(TypedDict):
    question: str
    kb_id: int
    embeddings: any  # 把模型对象传进来
    history: list
    context: str
    answer: str

# 2. 真实的查库+重排节点
def retrieve_node(state: AgentState):
    print(f"--- 正在查库: kb_{state['kb_id']} ---")
    # 在这里实例化，闭环
    vector_store = RedisVectorStore(
        redis_url=settings.redis_url,
        index_name=f"kb_index_{state['kb_id']}",
        embeddings=state["embeddings"]
    )
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    docs = retriever.invoke(state["question"])


    # 提取文本
    doc_texts = [doc.page_content for doc in docs]

    # 调用 rerank 函数
    reranked_texts = rerank_text(state["question"], doc_texts)


    # 兼容处理：如果 reranked_texts 里面是元组就取第一个，是字符串就直接用
    valid_texts = []
    for t in reranked_texts[:2]:
        if isinstance(t, tuple):
            valid_texts.append(t[0])
        else:
            valid_texts.append(t)

    top_context = "\n".join(valid_texts)
    return {"context": top_context or "知识库中暂无相关内容"}

# 3. 定义直接回复节点
def direct_reply_node(state: AgentState):
    print("--- 正在直接回答 ---")
    return {"context": "无上下文，直接闲聊。"}

# 4. 路由判断
def route_question(state: AgentState):
    if "你好" in state["question"] or "在吗" in state["question"]:
        return "direct_reply"
    return "retrieve"

# 5. 组装图
workflow = StateGraph(AgentState)
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("direct_reply", direct_reply_node)

# 设定入口和条件边
workflow.set_conditional_entry_point(route_question)
workflow.add_edge("retrieve", END)
workflow.add_edge("direct_reply", END)

rag_graph = workflow.compile()