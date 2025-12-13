from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from core.dependencies.auth import verify_token
from core.dependencies.services import get_product_market_service, get_assistant_service
from schemas.auth import TokenData
from schemas.product_market import (
    ProductMarketAnalysisResponse, 
    ConsultantChatRequest, 
    ConsultantChatResponse
)
from services.features.product_intelligence.ai.product_market_service import ProductMarketAnalysisService
from services.features.product_intelligence.ai.assistant_service import AssistantService
from schemas.product_chat import ProductChatSessionResponse

router = APIRouter(prefix="/products/{product_id}/market", tags=["Product Market Consultant"])

@router.get("/chat-sessions", response_model=List[ProductChatSessionResponse])
def get_chat_sessions(
    product_id: UUID,
    service: AssistantService = Depends(get_assistant_service),
    token: TokenData = Depends(verify_token)
):
    """
    Lấy danh sách các cuộc hội thoại (sessions) của user với sản phẩm này.
    """
    return service.get_product_chat_sessions(product_id, token.user_id)

@router.get("/chat-sessions/{session_id}", response_model=ProductChatSessionResponse)
def get_chat_session_detail(
    product_id: UUID,
    session_id: UUID,
    service: AssistantService = Depends(get_assistant_service),
    token: TokenData = Depends(verify_token)
):
    """
    Lấy chi tiết nội dung cuộc hội thoại (lịch sử chat).
    """
    session = service.get_chat_session(session_id, token.user_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

# Deprecated legacy endpoint
@router.get("/chat-history", response_model=ProductChatSessionResponse)
def get_chat_history(
    product_id: UUID,
    service: AssistantService = Depends(get_assistant_service),
    token: TokenData = Depends(verify_token)
):
    """
    [Legacy] Lấy cuộc hội thoại gần nhất.
    """
    sessions = service.get_product_chat_sessions(product_id, token.user_id)
    if not sessions:
        raise HTTPException(status_code=404, detail="No chat history found")
    return sessions[0] # Return latest session

@router.post("/analyze", response_model=ProductMarketAnalysisResponse)
def analyze_product_market(
    product_id: UUID,
    service: ProductMarketAnalysisService = Depends(get_product_market_service),
    token: TokenData = Depends(verify_token)
):
    """
    Trigger AI phân tích thị trường cho sản phẩm (Pros/Cons, Target Audience...).
    """
    try:
        return service.analyze_product_market(product_id, user_id=token.user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/consult", response_model=ConsultantChatResponse)
def consult_product(
    product_id: UUID,
    request: ConsultantChatRequest,
    service: AssistantService = Depends(get_assistant_service),
    token: TokenData = Depends(verify_token)
):
    """
    Chat với AI Consultant về sản phẩm này (Chiến lược giá, Marketing...).
    """
    try:
        return service.consult(
            user_query=request.query, 
            user_id=token.user_id,
            session_id=request.session_id,
            product_id=product_id, # Must pass explicitly
            # history ignored
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
