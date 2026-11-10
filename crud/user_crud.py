from crud.base import BaseCRUD
from models.user import User
from schemas.user_schemas import UserCreate
from sqlmodel import Session, select


class UserCRUD(BaseCRUD[User, UserCreate]):

    def get_by_username(self, db: Session, username: str):
        return db.exec(select(User).where(User.username == username)).first()


user_crud = UserCRUD(User)