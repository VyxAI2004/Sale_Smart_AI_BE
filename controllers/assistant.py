from uuid import UUID
from typing import List
from core.dependencies.auth import verify_token
from schemas.auth import TokenData
from core.dependencies.services import get_assistant_service
from services.features.product_intelligence.ai.assistant_service import AssistantService
from schemas.product_market import ConsultantChatResponse, ConsultantChatRequest
from schemas.product_chat import ProductChatSessionResponse
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/assistant", tags=["AI Assistant (Global)"])

@router.post("/chat", response_model=ConsultantChatResponse)
def chat_with_assistant(
    request: ConsultantChatRequest,
    service: AssistantService = Depends(get_assistant_service),
    token: TokenData = Depends(verify_token)
):
    """
    Chat với AI Assistant (Global, Project-based).
    """
    try:
        return service.consult(
            user_query=request.query, 
            user_id=token.user_id,
            session_id=request.session_id,
            project_id=request.project_id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi.responses import StreamingResponse

@router.post("/chat/stream")
def chat_assistant_stream(
    request: ConsultantChatRequest,
    service: AssistantService = Depends(get_assistant_service),
    token: TokenData = Depends(verify_token)
):
    """
    Chat Streaming với AI (SSE / NDJSON).
    Trả về từng chunk dữ liệu JSON trên mỗi dòng.
    """
    try:
        return StreamingResponse(
            service.consult_stream(
                user_query=request.query, 
                user_id=token.user_id,
                session_id=request.session_id,
                project_id=request.project_id
            ),
            media_type="application/x-ndjson"
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # Note: Exception in stream might crash connection, harder to handle gracefully via HTTP status
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions", response_model=List[ProductChatSessionResponse])
def list_my_sessions(
    skip: int = 0,
    limit: int = 20,
    service: AssistantService = Depends(get_assistant_service),
    token: TokenData = Depends(verify_token)
):
    """
    Lấy danh sách TOÀN BỘ cuộc hội thoại của User (Global + Project + Product).
    Hỗ trợ phân trang: skip, limit.
    """
    return service.get_user_chat_sessions(token.user_id, skip=skip, limit=limit)

@router.get("/sessions/{session_id}", response_model=ProductChatSessionResponse)
def get_session_detail(
    session_id: UUID, 
    service: AssistantService = Depends(get_assistant_service),
    token: TokenData = Depends(verify_token)
):
    """
    Xem chi tiết nội dung cuộc hội thoại.
    """
    session = service.get_chat_session(session_id, token.user_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
