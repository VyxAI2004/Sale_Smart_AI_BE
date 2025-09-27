from typing import Generic, List, Optional, Type, TypeVar
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import and_, delete
from sqlalchemy.orm import Session

from models.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get(self, id: UUID) -> Optional[ModelType]:
        """Get a record by ID"""
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self, *, skip: int = 0, limit: int = 100, filters: Optional[dict] = None
    ) -> List[ModelType]:
        """Get multiple records with optional filters"""
        query = self.db.query(self.model)

        if filters:
            filter_conditions = []
            for key, value in filters.items():
                if hasattr(self.model, key) and value is not None:
                    filter_conditions.append(getattr(self.model, key) == value)
            if filter_conditions:
                query = query.filter(and_(*filter_conditions))

        return query.offset(skip).limit(limit).all()

    def create(self, *, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record"""
        db_obj = self.model(**obj_in.model_dump())
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, *, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        """Update an existing record"""
        obj_data = (
            obj_in.model_dump(exclude_unset=True)
            if hasattr(obj_in, "model_dump")
            else obj_in.__dict__
        )
        for field in obj_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, obj_data[field])
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, *, id: UUID) -> None:
        """Delete a record by ID"""
        stmt = delete(self.model).where(self.model.id == id)
        self.db.execute(stmt)
        self.db.commit()

    def count(self, filters: Optional[dict] = None) -> int:
        """Count records with optional filters"""
        query = self.db.query(self.model)

        if filters:
            filter_conditions = []
            if filter_conditions:
                query = query.filter(and_(*filter_conditions))

        
        return query.count()
