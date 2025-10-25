from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session

from models.ai_model import AIModel
from schemas.ai_model import AIModelCreate, AIModelUpdate
from repositories.ai_model import AIModelRepository, AIModelFilters

from .base import BaseService


class AIModelService(
    BaseService[AIModel, AIModelCreate, AIModelUpdate, AIModelRepository]
):
    def __init__(self, db: Session):
        super().__init__(db, AIModel, AIModelRepository)

    def get_ai_model(self, *, model_id: UUID) -> Optional[AIModel]:
        """Get AI model by ID"""
        return self.get(model_id)

    def search(
        self,
        *,
        q: Optional[str] = None,
        user_id: Optional[UUID] = None,
        model_type: Optional[str] = None,
        provider: Optional[str] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[AIModel]:
        """Search AI models with filters"""
        filters: Optional[AIModelFilters] = None

        filter_dict = {}
        if q:
            filter_dict["q"] = q
        if user_id:
            filter_dict["user_id"] = user_id
        if model_type:
            filter_dict["model_type"] = model_type
        if provider:
            filter_dict["provider"] = provider
        if is_active is not None:
            filter_dict["is_active"] = is_active

        if filter_dict:
            filters = AIModelFilters(**filter_dict)

        return self.repository.search(filters=filters, skip=skip, limit=limit)

    def create_ai_model(self, payload: AIModelCreate, user_id: UUID) -> AIModel:
        """Create new AI model"""
        # Verify the payload user_id matches the authenticated user
        payload_dict = payload.model_dump() if hasattr(payload, 'model_dump') else payload.dict()
        payload_dict["user_id"] = user_id  # Ensure user_id is set to authenticated user
        
        # Check if model name already exists for this user
        existing_model = self.repository.get_by_name_and_user(
            name=payload_dict["name"],
            user_id=user_id
        )
        if existing_model:
            raise ValueError(f"AI model with name '{payload_dict['name']}' already exists for this user")
        
        return self.create(payload=AIModelCreate(**payload_dict))

    def update_ai_model(
        self,
        model_id: UUID,
        payload: AIModelUpdate,
        user_id: UUID
    ) -> Optional[AIModel]:
        """Update AI model"""
        db_model = self.get(model_id)
        if not db_model:
            return None
        
        # Check if user owns this model
        if db_model.user_id != user_id:
            raise ValueError("You don't have permission to update this AI model")
        
        # Check if new name conflicts with existing models
        if payload.name:
            existing_model = self.repository.get_by_name_and_user(
                name=payload.name,
                user_id=user_id
            )
            if existing_model and existing_model.id != model_id:
                raise ValueError(f"AI model with name '{payload.name}' already exists for this user")
        
        return self.update(db_obj=db_model, payload=payload)

    def delete_ai_model(self, model_id: UUID, user_id: UUID) -> None:
        """Delete AI model (hard delete)"""
        db_model = self.get(model_id)
        if not db_model:
            raise ValueError("AI model not found")
        
        # Check if user owns this model
        if db_model.user_id != user_id:
            raise ValueError("You don't have permission to delete this AI model")
        
        self.delete(id=model_id)

    def deactivate_ai_model(self, model_id: UUID, user_id: UUID) -> Optional[AIModel]:
        """Deactivate AI model (soft delete)"""
        db_model = self.get(model_id)
        if not db_model:
            return None
        
        # Check if user owns this model
        if db_model.user_id != user_id:
            raise ValueError("You don't have permission to deactivate this AI model")
        
        return self.repository.deactivate_model(model_id=model_id)

    def activate_ai_model(self, model_id: UUID, user_id: UUID) -> Optional[AIModel]:
        """Activate AI model"""
        db_model = self.get(model_id)
        if not db_model:
            return None
        
        # Check if user owns this model
        if db_model.user_id != user_id:
            raise ValueError("You don't have permission to activate this AI model")
        
        return self.repository.activate_model(model_id=model_id)

    def get_user_ai_models(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[AIModel]:
        """Get all AI models for a specific user"""
        return self.repository.get_by_user_id(user_id=user_id)

    def get_active_user_ai_models(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[AIModel]:
        """Get active AI models for a specific user"""
        return self.repository.get_active_by_user_id(user_id=user_id)

    def get_by_type(
        self,
        user_id: UUID,
        model_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[AIModel]:
        """Get AI models by user and model type"""
        return self.repository.get_by_user_and_type(
            user_id=user_id,
            model_type=model_type
        )

    def get_by_provider(
        self,
        user_id: UUID,
        provider: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[AIModel]:
        """Get AI models by user and provider"""
        return self.repository.get_by_user_and_provider(
            user_id=user_id,
            provider=provider
        )

    def increment_usage(self, model_id: UUID) -> Optional[AIModel]:
        """Increment usage count and update last_used_at timestamp"""
        return self.repository.increment_usage_count(model_id=model_id)

    def count_ai_models(self, *, filters: Optional[AIModelFilters] = None) -> int:
        """Count AI models with filters"""
        return self.repository.count_by_filters(filters=filters)

    def validate_model_access(self, model_id: UUID, user_id: UUID) -> bool:
        """Validate if user has access to the AI model"""
        db_model = self.get(model_id)
        if not db_model:
            return False
        return db_model.user_id == user_id

    def get_model_statistics(self, model_id: UUID, user_id: UUID) -> Optional[dict]:
        """Get statistics for an AI model"""
        db_model = self.get(model_id)
        if not db_model or db_model.user_id != user_id:
            return None
        
        return {
            "id": db_model.id,
            "name": db_model.name,
            "model_type": db_model.model_type,
            "provider": db_model.provider,
            "usage_count": db_model.usage_count or 0,
            "last_used_at": db_model.last_used_at,
            "is_active": db_model.is_active,
            "created_at": db_model.created_at,
        }
