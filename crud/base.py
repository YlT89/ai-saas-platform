from typing import Type, TypeVar, Generic, Optional
from sqlmodel import SQLModel, Session, select, func

ModelT =TypeVar('ModelT', bound=SQLModel)
CreateT = TypeVar('CreateT', bound=SQLModel)

class BaseCRUD(Generic[ModelT, CreateT]):


    def __init__(self, model: Type[ModelT]):
        self.model = model

    def get_by_id(self, db: Session, obj_id: int) -> Optional[ModelT]:
        return db.get(self.model, obj_id)


    def page_list(self, db: Session, page: int, page_size: int):


        offset = (page -1) * page_size

        stmt = select(self.model).offset(offset).limit(page_size)     # limit：只取多少条
        items = db.exec(stmt).all()


        total = db.exec(select(func.count(self.model.id))).scalar()

        return {'page': page, 'page_size': page_size, 'total': total, 'items': items}



    def create(self, db: Session, obj_in: CreateT) -> ModelT:
        db_obj = self.model.model_validate(obj_in)
        db.add(db_obj)
        try:
            db.commit()
            db.refresh(db_obj)
        except Exception as e:
            db.rollback()
            raise e
        return db_obj


    def update(self, db: Session, db_obj: ModelT, update_dict: dict) -> ModelT:

        for k, v in update_dict.items():
            setattr(db_obj, k, v)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

   
    def delete(self, db: Session, obj_id: int):
        obj = self.get_by_id(db, obj_id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj
