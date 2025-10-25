import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from core.dependencies.auth import verify_token
from schemas.auth import TokenData

from core.dependencies.services import get_ai_model_service
from schemas.ai_model import (
    ListAIModelsResponse,
    AIModelResponse,
    AIModelCreate,
    AIModelUpdate,
)
from services.sale_smart_ai_app.ai_model import AIModelService
from repositories.ai_model import AIModelFilters
from middlewares.permissions import check_global_permissions
from shared.enums import GlobalPermissionEnum, RoleEnum

router = APIRouter(prefix="/ai-models", tags=["ai-models"])


@router.post("/", response_model=AIModelResponse, status_code=status.HTTP_201_CREATED)
def create_ai_model(
    *,
    payload: AIModelCreate,
    ai_model_service: AIModelService = Depends(get_ai_model_service),
    user_from_token: TokenData = Depends(verify_token),
):
    """
    Create new AI model.
    
    Requires authentication. Users can only create AI models for themselves.
    """
    try:
        ai_model = ai_model_service.create_ai_model(
            payload=payload,
            user_id=user_from_token.user_id
        )
        return ai_model
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/", response_model=ListAIModelsResponse)
def get_list_ai_models(
    *,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    q: Optional[str] = Query(None, description="Search in name, model_name, provider"),
    model_type: Optional[str] = Query(None, description="Filter by model type (llm, crawler, analyzer)"),
    provider: Optional[str] = Query(None, description="Filter by provider (openai, anthropic, gemini, custom)"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    user_id: Optional[uuid.UUID] = Query(None, description="Filter by user (admin only)"),
    ai_model_service: AIModelService = Depends(get_ai_model_service),
    user_from_token: TokenData = Depends(verify_token),
):
    """
    List AI models with filters and pagination.
    
    Regular users can only see their own AI models.
    Admins can see all AI models and filter by user_id.
    """
    try:
        # Check if user is admin
        is_admin = any(role in [RoleEnum.SUPER_ADMIN.value, RoleEnum.ADMIN.value] 
                      for role in user_from_token.roles)
        
        # If not admin, force filter by their own user_id
        filter_user_id = user_id if is_admin else user_from_token.user_id
        
        ai_models = ai_model_service.search(
            q=q,
            user_id=filter_user_id,
            model_type=model_type,
            provider=provider,
            is_active=is_active,
            skip=skip,
            limit=limit,
        )
        
        filters_dict = {}
        if q:
            filters_dict["q"] = q
        if filter_user_id:
            filters_dict["user_id"] = filter_user_id
        if model_type:
            filters_dict["model_type"] = model_type
        if provider:
            filters_dict["provider"] = provider
        if is_active is not None:
            filters_dict["is_active"] = is_active
        
        filters = AIModelFilters(**filters_dict) if filters_dict else None
        total = ai_model_service.count_ai_models(filters=filters)
        
        return ListAIModelsResponse(
            total=total,
            items=[AIModelResponse.model_validate(ai_model) for ai_model in ai_models]
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/my", response_model=ListAIModelsResponse)
def get_my_ai_models(
    *,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    model_type: Optional[str] = Query(None, description="Filter by model type"),
    provider: Optional[str] = Query(None, description="Filter by provider"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    ai_model_service: AIModelService = Depends(get_ai_model_service),
    user_from_token: TokenData = Depends(verify_token),
):
    """
    Get current user's AI models.
    
    Convenient endpoint to get only the authenticated user's AI models.
    """
    try:
        ai_models = ai_model_service.search(
            user_id=user_from_token.user_id,
            model_type=model_type,
            provider=provider,
            is_active=is_active,
            skip=skip,
            limit=limit,
        )
        
        filters = AIModelFilters(
            user_id=user_from_token.user_id,
            model_type=model_type,
            provider=provider,
            is_active=is_active
        )
        total = ai_model_service.count_ai_models(filters=filters)
        
        return ListAIModelsResponse(
            total=total,
            items=[AIModelResponse.model_validate(ai_model) for ai_model in ai_models]
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/my/active", response_model=ListAIModelsResponse)
def get_my_active_ai_models(
    *,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    model_type: Optional[str] = Query(None, description="Filter by model type"),
    provider: Optional[str] = Query(None, description="Filter by provider"),
    ai_model_service: AIModelService = Depends(get_ai_model_service),
    user_from_token: TokenData = Depends(verify_token),
):
    """
    Get current user's active AI models.
    
    Returns only active AI models belonging to the authenticated user.
    """
    try:
        ai_models = ai_model_service.get_active_user_ai_models(
            user_id=user_from_token.user_id,
            skip=skip,
            limit=limit,
        )
        
        # Apply additional filters if provided
        if model_type:
            ai_models = [m for m in ai_models if m.model_type == model_type]
        if provider:
            ai_models = [m for m in ai_models if m.provider == provider]
        
        return ListAIModelsResponse(
            total=len(ai_models),
            items=[AIModelResponse.model_validate(ai_model) for ai_model in ai_models]
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/types/{model_type}", response_model=ListAIModelsResponse)
def get_ai_models_by_type(
    *,
    model_type: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    ai_model_service: AIModelService = Depends(get_ai_model_service),
    user_from_token: TokenData = Depends(verify_token),
):
    """
    Get current user's AI models by type.
    
    Valid types: llm, crawler, analyzer
    """
    try:
        ai_models = ai_model_service.get_by_type(
            user_id=user_from_token.user_id,
            model_type=model_type,
            skip=skip,
            limit=limit,
        )
        
        return ListAIModelsResponse(
            total=len(ai_models),
            items=[AIModelResponse.model_validate(ai_model) for ai_model in ai_models]
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/providers/{provider}", response_model=ListAIModelsResponse)
def get_ai_models_by_provider(
    *,
    provider: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    ai_model_service: AIModelService = Depends(get_ai_model_service),
    user_from_token: TokenData = Depends(verify_token),
):
    """
    Get current user's AI models by provider.
    
    Valid providers: openai, anthropic, gemini, custom
    """
    try:
        ai_models = ai_model_service.get_by_provider(
            user_id=user_from_token.user_id,
            provider=provider,
            skip=skip,
            limit=limit,
        )
        
        return ListAIModelsResponse(
            total=len(ai_models),
            items=[AIModelResponse.model_validate(ai_model) for ai_model in ai_models]
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{ai_model_id}", response_model=AIModelResponse)
def get_ai_model(
    *,
    ai_model_id: uuid.UUID,
    ai_model_service: AIModelService = Depends(get_ai_model_service),
    user_from_token: TokenData = Depends(verify_token),
):
    """
    Get AI model by ID.
    
    Users can only access their own AI models.
    Admins can access any AI model.
    """
    ai_model = ai_model_service.get_ai_model(model_id=ai_model_id)
    if not ai_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AI model not found")
    
    # Check if user is admin
    is_admin = any(role in [RoleEnum.SUPER_ADMIN.value, RoleEnum.ADMIN.value] 
                  for role in user_from_token.roles)
    
    # Check ownership if not admin
    if not is_admin and ai_model.user_id != user_from_token.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this AI model"
        )
    
    return ai_model


@router.get("/{ai_model_id}/statistics")
def get_ai_model_statistics(
    *,
    ai_model_id: uuid.UUID,
    ai_model_service: AIModelService = Depends(get_ai_model_service),
    user_from_token: TokenData = Depends(verify_token),
):
    """
    Get AI model statistics.
    
    Returns usage statistics for the AI model.
    """
    try:
        statistics = ai_model_service.get_model_statistics(
            model_id=ai_model_id,
            user_id=user_from_token.user_id
        )
        if not statistics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="AI model not found or you don't have permission to access it"
            )
        return statistics
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/{ai_model_id}", response_model=AIModelResponse)
def update_ai_model(
    *,
    ai_model_id: uuid.UUID,
    payload: AIModelUpdate,
    ai_model_service: AIModelService = Depends(get_ai_model_service),
    user_from_token: TokenData = Depends(verify_token),
):
    """
    Update AI model.
    
    Users can only update their own AI models.
    """
    try:
        ai_model = ai_model_service.update_ai_model(
            model_id=ai_model_id,
            payload=payload,
            user_id=user_from_token.user_id
        )
        if not ai_model:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AI model not found")
        return ai_model
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{ai_model_id}/deactivate", response_model=AIModelResponse)
def deactivate_ai_model(
    *,
    ai_model_id: uuid.UUID,
    ai_model_service: AIModelService = Depends(get_ai_model_service),
    user_from_token: TokenData = Depends(verify_token),
):
    """
    Deactivate AI model (soft delete).
    
    Users can only deactivate their own AI models.
    """
    try:
        ai_model = ai_model_service.deactivate_ai_model(
            model_id=ai_model_id,
            user_id=user_from_token.user_id
        )
        if not ai_model:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AI model not found")
        return ai_model
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{ai_model_id}/activate", response_model=AIModelResponse)
def activate_ai_model(
    *,
    ai_model_id: uuid.UUID,
    ai_model_service: AIModelService = Depends(get_ai_model_service),
    user_from_token: TokenData = Depends(verify_token),
):
    """
    Activate AI model.
    
    Users can only activate their own AI models.
    """
    try:
        ai_model = ai_model_service.activate_ai_model(
            model_id=ai_model_id,
            user_id=user_from_token.user_id
        )
        if not ai_model:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AI model not found")
        return ai_model
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{ai_model_id}/increment-usage", response_model=AIModelResponse)
def increment_ai_model_usage(
    *,
    ai_model_id: uuid.UUID,
    ai_model_service: AIModelService = Depends(get_ai_model_service),
    user_from_token: TokenData = Depends(verify_token),
):
    """
    Increment AI model usage count.
    
    This endpoint should be called whenever the AI model is used.
    Users can only increment usage for their own AI models.
    """
    try:
        # Validate access first
        if not ai_model_service.validate_model_access(
            model_id=ai_model_id,
            user_id=user_from_token.user_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to use this AI model"
            )
        
        ai_model = ai_model_service.increment_usage(model_id=ai_model_id)
        if not ai_model:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AI model not found")
        return ai_model
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{ai_model_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ai_model(
    *,
    ai_model_id: uuid.UUID,
    ai_model_service: AIModelService = Depends(get_ai_model_service),
    user_from_token: TokenData = Depends(verify_token),
):
    """
    Delete AI model (hard delete).
    
    Users can only delete their own AI models.
    Admins can delete any AI model.
    """
    try:
        # Check if user is admin
        is_admin = any(role in [RoleEnum.SUPER_ADMIN.value, RoleEnum.ADMIN.value] 
                      for role in user_from_token.roles)
        
        if is_admin:
            # Admin can delete any model
            ai_model_service.delete(id=ai_model_id)
        else:
            # Regular user can only delete their own models
            ai_model_service.delete_ai_model(
                model_id=ai_model_id,
                user_id=user_from_token.user_id
            )
        return None
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# Admin-only endpoints
@router.get("/admin/all", response_model=ListAIModelsResponse)
@check_global_permissions(GlobalPermissionEnum.VIEW_ALL_AI_MODELS)
async def admin_get_all_ai_models(
    *,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    q: Optional[str] = Query(None),
    model_type: Optional[str] = Query(None),
    provider: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    ai_model_service: AIModelService = Depends(get_ai_model_service),
    token: TokenData = Depends(verify_token),
):
    """
    Admin: Get all AI models across all users.
    
    Requires: VIEW_ALL_AI_MODELS permission (Admin or Super Admin only)
    """
    try:
        ai_models = ai_model_service.search(
            q=q,
            model_type=model_type,
            provider=provider,
            is_active=is_active,
            skip=skip,
            limit=limit,
        )
        
        filters_dict = {}
        if q:
            filters_dict["q"] = q
        if model_type:
            filters_dict["model_type"] = model_type
        if provider:
            filters_dict["provider"] = provider
        if is_active is not None:
            filters_dict["is_active"] = is_active
        
        filters = AIModelFilters(**filters_dict) if filters_dict else None
        total = ai_model_service.count_ai_models(filters=filters)
        
        return ListAIModelsResponse(
            total=total,
            items=[AIModelResponse.model_validate(ai_model) for ai_model in ai_models]
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
