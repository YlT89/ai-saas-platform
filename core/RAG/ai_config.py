from langchain_community.embeddings import DashScopeEmbeddings
from langchain.chat_models import init_chat_model
from langchain_core.prompts import PromptTemplate
from functools import lru_cache

from core.config import settings

# 1、全局 Prompt 模板没有网络连接，可以直接放在顶层
prompt_template = """
    你是一个专业的企业客服助手。请严格根据下面提供的参考内容回答用户问题。
    如果你不知道答案，请直接说“抱歉，提供的资料中没有相关信息”，千万不要自己编造。

    【参考内容】
    {context}

    【用户问题】
    {question}
    """
prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

# 使用 lru_cache 实现懒加载，且全局只实例化一次
@lru_cache()    # Embedding模型
def get_embeddings() -> DashScopeEmbeddings:
    return DashScopeEmbeddings(
    model="text-embedding-v3",
    dashscope_api_key=settings.dashscope_api_key
    )

@lru_cache()    # 语言模型
def get_llm():
    return init_chat_model(
    model="deepseek-flash",
    model_provider="openai",
    api_key=settings.api_key,
    base_url="https://api.deepseek.com"
)

