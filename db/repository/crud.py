"""
Repostory pattern implementation for SQLAlchemy ORM.
"""
from typing import Any, Dict, Type
from sqlalchemy import desc
from sqlalchemy.orm import Session, aliased
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    id: Any
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class Crud:
    def __init__(self, db: Session):
        self.db = db

    def create(self, model: Type[Base], obj_in: Dict[str, Any]):
        try:
            db_obj = model(**obj_in)
            self.db.add(db_obj)
            return db_obj
        except Exception as e:
            raise e

    def update(self, db_obj: Base, obj_in: Dict[str, Any]):
        try:
            for key, value in obj_in.items():
                setattr(db_obj, key, value)
            return db_obj
        except Exception as e:
            raise e

    def remove(self, db_obj: Base):
        try:
            self.db.delete(db_obj)
            return
        except Exception as e:
            raise e

    def get(self, model: Type[Base], id: Any, **kwargs):
        try:
            query = self.db.query(model).filter(model.id == id)
            joins = {}
            for key, value in kwargs.items():
                if '__' in key:
                    rel_name, rel_attr = key.split('__', 1)
                    related_model = getattr(model, rel_name).property.mapper.class_

                    if rel_name not in joins:
                        alias = aliased(related_model)
                        query = query.join(alias, getattr(model, rel_name))
                        joins[rel_name] = alias
                    query = query.filter(getattr(joins[rel_name], rel_attr) == value)
                elif hasattr(model, key):
                    query = query.filter(getattr(model, key) == value)
            return query.first()
        except Exception as e:
            raise e

    def get_multi(self, model: Type[Base], skip: int = 0, limit: int = 100):
        try:
            query = self.db.query(model).filter().order_by(desc(model.date_created)).offset(skip).limit(limit).all()
            return query
        except Exception as e:
            raise e

    def get_by(self, model: Type[Base], **kwargs):
        try:
            query = self.db.query(model).filter_by(**kwargs)
            return query.first()
        except Exception as e:
            raise e
