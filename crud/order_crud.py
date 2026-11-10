
from crud.base import BaseCRUD
from models.order import Order
from schemas.order_schemas import OrderCreate

class OrderCRUD(BaseCRUD[Order, OrderCreate]):
    pass

order_crud = OrderCRUD(Order)