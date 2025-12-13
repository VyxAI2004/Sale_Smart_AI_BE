from uuid import UUID
from typing import Optional
from sqlalchemy.orm import Session

from repositories.base import BaseRepository
from models.product_chat import ProductChatSession, ProductChatMessage
from schemas.product_chat import ProductChatSessionCreate, ProductChatSessionUpdate, ProductChatMessageCreate, ProductChatMessageUpdate

class ProductChatSessionRepository(BaseRepository[ProductChatSession, ProductChatSessionCreate, ProductChatSessionUpdate]):
    def __init__(self, db: Session):
        super().__init__(ProductChatSession, db)

    def get_by_product_and_user(self, product_id: UUID, user_id: UUID) -> Optional[ProductChatSession]:
        return self.db.query(self.model).filter(
            self.model.product_id == product_id,
            self.model.user_id == user_id
        ).first()

class ProductChatMessageRepository(BaseRepository[ProductChatMessage, ProductChatMessageCreate, ProductChatMessageUpdate]):
    def __init__(self, db: Session):
        super().__init__(ProductChatMessage, db)
