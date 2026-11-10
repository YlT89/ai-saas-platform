from .user import User
from .address import Address
from .order import Order
from .chat import ChatMessage
from .kb import KB

# 统一在这里重建，确保所有类都已加载完毕
User.model_rebuild()
Address.model_rebuild()
Order.model_rebuild()
ChatMessage.model_rebuild()
KB.model_rebuild()