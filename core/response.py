from typing import TypeVar, Generic, Optional, List
from sqlmodel import SQLModel

T = TypeVar('T')

class PageData(SQLModel, Generic[T]):
    page: int
    page_size: int
    total: int
    items: List[T]

class ApiResp(SQLModel, Generic[T]):
    code: int = 200
    msg: str = 'success'
    data: Optional[T] = None

def success_resp(data=None, msg: str = "success") -> ApiResp:
    return ApiResp(msg=msg, data=data)

def fail_resp(msg: str, code: int = 400) -> ApiResp:
    return ApiResp(code=code, msg=msg)