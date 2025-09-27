import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from models.user import User
from core.security import hash_password
from repositories.user import UserFilters, UserRepository
from schemas.user import UserCreate, UserUpdate
from .base import BaseService

class UserService(BaseService[User, UserCreate, UserUpdate, UserRepository]):
    def __init__(self, db: Session):
        super().__init__(db, User, UserRepository)

    def get_by_email(self, *, email: str) -> Optional[User]:
        return self.repository.get_by_email(email=email)

    def get_user(self, *, user_id: uuid.UUID) -> Optional[User]:
        return self.get(user_id)

    def search(
        self,
        *,
        q: Optional[str] = None,
        username: Optional[str] = None,
        email: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[User]:
        """Search users with filters"""
        filters: Optional[UserFilters] = None

        filter_dict = {}
        if q:
            filter_dict["q"] = q
        if username:
            filter_dict["username"] = username
        if email:
            filter_dict["email"] = email

        if filter_dict:
            filters = UserFilters(**filter_dict)

        return self.repository.search(filters=filters, skip=skip, limit=limit)
    

    def create_user(self, payload: UserCreate) -> User:
        hashed = hash_password(payload.password_hash)
        payload_dict = payload.model_dump() if hasattr(payload, 'model_dump') else payload.dict()
        payload_dict["password_hash"] = hashed
        payload_dict.pop("password", None)
        return self.create(payload=UserCreate(**payload_dict))

    def update_user(self, user_id: uuid.UUID, payload: UserUpdate) -> Optional[User]:
        db_user = self.get(user_id)
        if not db_user:
            return None
        payload_dict = payload.model_dump(exclude_unset=True)
        if payload_dict.get("password"):
            payload_dict["password_hash"] = hash_password(payload_dict.pop("password"))
        payload_update = UserUpdate(**payload_dict)
        return self.update(db_obj=db_user, payload=payload_update)

    def delete_user(self, user_id: uuid.UUID) -> None:
        self.delete(id=user_id)

    def count_users(self, *, filters: Optional[UserFilters] = None) -> int:
        filters_dict = dict(filters) if filters else None
        return self.repository.count(filters=filters_dict)