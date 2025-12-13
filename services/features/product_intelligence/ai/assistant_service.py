import json
import logging
from typing import List, Optional, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session

from core.llm.factory import AgentFactory
from services.core.base import BaseService
from services.features.product_intelligence.agents.llm_provider_selector import LLMProviderSelector

from models.product import Product
from models.product_chat import ProductChatSession, ProductChatMessage
from repositories.product import ProductRepository
from repositories.product_market import ProductMarketAnalysisRepository
from repositories.product_chat import ProductChatSessionRepository, ProductChatMessageRepository
# Assuming ProjectRepository exists, we'll import dynamic or general repo if needed
# If repositories/project.py doesn't contain a specific class, we might use generic BaseRepository
# But usually it does. Let's assume repositories.project exists.
from repositories.project import ProjectRepository

from schemas.product_chat import (
    ProductChatSessionCreate,
    ProductChatMessageCreate,
    ProductChatSessionResponse
)
from schemas.product_market import ConsultantChatResponse, ChatMessage

logger = logging.getLogger(__name__)

class AssistantService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db)
        self.session_repo = ProductChatSessionRepository(db)
        self.message_repo = ProductChatMessageRepository(db)
        self.product_repo = ProductRepository(db)
        self.market_repo = ProductMarketAnalysisRepository(db)
        self.project_repo = ProjectRepository(db)
        self.llm_selector = LLMProviderSelector(db)

    def get_chat_session(self, session_id: UUID, user_id: UUID) -> Optional[ProductChatSession]:
        session = self.session_repo.get(session_id)
        if session and session.user_id == user_id:
            return session
        return None

    def get_user_chat_sessions(self, user_id: UUID, skip: int = 0, limit: int = 20):
        """List ALL chat sessions for a user with Pagination"""
        filters = {"user_id": user_id}
        # Assuming BaseRepository.get_multi supports skip/limit
        return self.session_repo.get_multi(filters=filters, skip=skip, limit=limit, order_by=["-updated_at"])

    def get_product_chat_sessions(self, product_id: UUID, user_id: UUID, skip: int = 0, limit: int = 20):
        filters = {"product_id": product_id, "user_id": user_id}
        return self.session_repo.get_multi(filters=filters, skip=skip, limit=limit, order_by=["-updated_at"])

    def _prepare_consult_session(self, user_query, user_id, product_id, project_id, session_id):
        session = None

        # 0. Get/Create Chat Session
        if session_id:
            session = self.session_repo.get(session_id)
            if session and session.user_id != user_id:
                 raise ValueError("Access denied to this chat session")
        
        if not session:
            # Determine logic
            session_type = "global"
            if product_id:
                session_type = "product_consult"
            elif project_id:
                session_type = "project_consult"
            
            # Create New Session
            session = self.session_repo.create(obj_in=ProductChatSessionCreate(
                user_id=user_id,
                product_id=product_id,
                project_id=project_id,
                session_type=session_type,
                title=f"{user_query[:50]}"
            ))

        # 1. Save User Message to DB
        self.message_repo.create(obj_in=ProductChatMessageCreate(
            session_id=session.id,
            role="user",
            content=user_query
        ))

        # 2. Build Context
        context_parts = []
        
        target_product_id = product_id or session.product_id
        if target_product_id:
            product = self.product_repo.get(target_product_id)
            if product:
                analysis = self.market_repo.get_by_product_id(target_product_id)
                analysis_txt = ""
                if analysis:
                    analysis_txt = f"""
                    PHÂN TÍCH THỊ TRƯỜNG (AI):
                    - Ưu điểm: {', '.join(analysis.pros)}
                    - Nhược điểm: {', '.join(analysis.cons)}
                    - Giá cả: {analysis.price_evaluation}
                    - Khách hàng: {analysis.target_audience}
                    """
                context_parts.append(f"""
                --- CONTEXT SẢN PHẨM ---
                Tên: {product.name}
                Giá: {product.current_price}
                Mô tả: {str(product.features or '')[:500]}...
                Trust Score: {product.trust_score}/100
                {analysis_txt}
                """)
                if not project_id and product.project_id:
                     project_id = product.project_id

        target_project_id = project_id or session.project_id
        if target_project_id:
            project = self.project_repo.get(target_project_id)
            if project:
                context_parts.append(f"""
                --- CONTEXT DỰ ÁN ---
                Tên dự án: {project.name}
                Mục tiêu: {project.description or 'N/A'}
                Sản phẩm target: {project.target_product_name}
                Ngân sách: {project.target_budget_range} {project.currency}
                """)

        # 3. Construct Prompt
        final_context = "\n".join(context_parts)
        system_prompt = f"""
        Bạn là "Sale Smart AI Consultant" - trợ lý kinh doanh thông minh.
        {final_context}
        NHIỆM VỤ:
        Trả lời câu hỏi của người dùng dựa trên Context (nếu có).
        """
        
        # 4. History
        self.db.refresh(session)
        db_messages = session.messages
        full_prompt = system_prompt + "\n\n--- HISTORY ---\n"
        for msg in db_messages[-10:]:
            role_label = "User" if msg.role == "user" else "AI"
            full_prompt += f"{role_label}: {msg.content}\n"
        full_prompt += "\nAI:"
        
        return session, full_prompt

    def consult(
        self, 
        user_query: str, 
        user_id: UUID,
        product_id: Optional[UUID] = None,
        project_id: Optional[UUID] = None,
        session_id: Optional[UUID] = None,
        history: List[ChatMessage] = []
    ) -> ConsultantChatResponse:
        """
        Chat Standard (Block response).
        """
        session, full_prompt = self._prepare_consult_session(user_query, user_id, product_id, project_id, session_id)
        
        llm_agent = self.llm_selector.select_agent(user_id=user_id)
        response = llm_agent.generate(full_prompt)
        ai_reply = response.text
        
        self.message_repo.create(obj_in=ProductChatMessageCreate(
            session_id=session.id, role="ai", content=ai_reply
        ))
        session.updated_at = datetime.now()
        self.db.add(session)
        self.db.commit()

        return ConsultantChatResponse(
            answer=ai_reply, sources=["AI", "History"], session_id=session.id
        )

    def consult_stream(
        self, 
        user_query: str, 
        user_id: UUID,
        product_id: Optional[UUID] = None,
        project_id: Optional[UUID] = None,
        session_id: Optional[UUID] = None
    ):
        """
        Chat Streaming generator.
        """
        session, full_prompt = self._prepare_consult_session(user_query, user_id, product_id, project_id, session_id)
        
        llm_agent = self.llm_selector.select_agent(user_id=user_id)
        
        # Yield Session ID first
        yield json.dumps({"session_id": str(session.id), "text": ""}) + "\n"
        
        full_text = ""
        for chunk in llm_agent.generate_stream(full_prompt):
            full_text += chunk
            yield json.dumps({"session_id": str(session.id), "text": chunk}) + "\n"
            
        self.message_repo.create(obj_in=ProductChatMessageCreate(
            session_id=session.id, role="ai", content=full_text
        ))
        session.updated_at = datetime.now()
        self.db.add(session)
        self.db.commit()
