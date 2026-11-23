from slowapi import Limiter
from slowapi.util import get_remote_address

# 创建全局唯一的限流器
limiter = Limiter(key_func=get_remote_address)