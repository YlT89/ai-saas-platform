# pip install dashscope -i https://pypi.tuna.tsinghua.edu.cn/simple
import dashscope
from http import HTTPStatus
from core.config import settings


def rerank_text(query: str, documents: list[str]) -> list[str]:
    """调用 API 对文档进行重排，返回重排后的文档列表"""
    if not documents:
        return []

    resp = dashscope.TextReRank.call(
        model='gte-rerank-v2',
        api_key=settings.dashscope_api_key,
        query=query,
        documents=documents,
        top_n=3,  # 只返回得分最高的三个
    )

    if resp.status_code == HTTPStatus.OK:
        # resp.output.results 里面按得分高低排好了
        results = resp.output.results
        return [documents[item.index] for item in results]
    else:
        print(f"❌ Rerank 调用失败！状态码：{resp.status_code}，报错详情：{resp}")
        # 失败时兜底，为了防止系统崩溃，按原样返回
        return documents

