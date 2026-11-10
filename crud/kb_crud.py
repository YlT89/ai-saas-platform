from crud.base import BaseCRUD
from models.kb import KB
from schemas.kb_schemas import KBCreate
from sqlmodel import Session, select


# 继承 BaseCRUD，并把 [KB, KBCreate] 传进去
class KBCRUD(BaseCRUD[KB, KBCreate]):

    def get_by_name_and_user(self, db: Session, name: str, user_id: int):
        return db.exec(
            select(KB)
            .where(KB.name == name)
            .where(KB.user_id == user_id)
        ).first()


# 实例化，把具体的模型类传进去
kb_crud = KBCRUD(KB)