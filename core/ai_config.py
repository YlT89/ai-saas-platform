from langchain_community.embeddings import DashScopeEmbeddings
from langchain.chat_models import init_chat_model
from langchain_core.prompts import PromptTemplate
from functools import lru_cache

from core.config import settings

# 1、全局 Prompt 模板没有网络连接，可以直接放在顶层
prompt_template = """
请使用以下提供的文本内容来回答问题。仅使用提供的文本信息。
如果文本中没有相关信息，请回答"抱歉，提供的文本中没有这个信息"。

文本内容:
{context}

问题: {question}

回答:
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

