from langchain_community.embeddings import DashScopeEmbeddings
from langchain.chat_models import init_chat_model
from langchain_core.prompts import PromptTemplate
from functools import lru_cache

from core.config import settings

# 1、全局 Prompt 模板没有网络连接，可以直接放在顶层
prompt_template = """你是一个聪明且严谨的AI助手。请严格根据下面提供的【参考资料】来回答【用户问题】。

【参考资料】
{context}

【用户问题】
{question}

【回答规则】
1. 请逐条分析用户的问题，并分点回答。
2. 如果参考资料中有对应答案，请直接提取内容作答。
3. 如果参考资料中明确提到了“没有某个事物的信息”，请照实转述。
4. 只要参考资料里包含相关的信息，就绝不可以说“都不知道”或“没有相关信息”。
5. 只有参考资料完全是一篇无关的废话时，才回答：“抱歉，资料中未提供该信息。”
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

