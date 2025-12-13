import json
import logging
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session

from core.llm.factory import AgentFactory

from models.product import Product, ProductReview
from models.product_market import ProductMarketAnalysis
from repositories.product import ProductRepository
from repositories.product_review import ProductReviewRepository
from repositories.product_market import ProductMarketAnalysisRepository

from schemas.product_market import (
    ProductMarketAnalysisResponse, 
    ProductMarketAnalysisCreate,
    ProductMarketAnalysisUpdate
)

from services.features.product_intelligence.agents.llm_provider_selector import LLMProviderSelector

logger = logging.getLogger(__name__)

class ProductMarketAnalysisService:
    def __init__(self, db: Session):
        self.db = db
        self.market_repo = ProductMarketAnalysisRepository(db)
        self.product_repo = ProductRepository(db)
        self.review_repo = ProductReviewRepository(db)
        self.llm_selector = LLMProviderSelector(db)

    def analyze_product_market(self, product_id: UUID, user_id: UUID) -> ProductMarketAnalysis:
        """
        Phân tích thị trường cho sản phẩm dựa trên detail và reviews.
        Tạo hoặc update bản ghi ProductMarketAnalysis.
        """
        # 1. Get Product Data
        product = self.product_repo.get(product_id)
        if not product:
            raise ValueError("Product not found")
        
        # Select LLM Agent
        llm_agent = self.llm_selector.select_agent(user_id=user_id)

        # 2. Get Reviews (Limit 50 relevant ones)
        # Fix: dùng query manual nếu repo chưa support tốt
        product_reviews = self.db.query(ProductReview).filter(
            ProductReview.product_id == product_id,
            ProductReview.content != None
        ).limit(50).all()
        
        reviews_text = "\n".join([f"- {r.content} (Rating: {r.rating}/5)" for r in product_reviews])
        
        if not reviews_text:
            reviews_text = "Chưa có reviews nào."

        # 3. Build Prompt
        prompt = f"""
        Bạn là chuyên gia phân tích thị trường và tư vấn chiến lược sản phẩm (Product Consultant).
        
        Hãy phân tích sản phẩm sau đây:
        
        --- THÔNG TIN SẢN PHẨM ---
        Tên: {product.name}
        Giá: {product.current_price} {product.currency or 'VND'}
        Mô tả: {str(product.features or product.specifications or '')[:1000]}
        
        --- Ý KIẾN KHÁCH HÀNG (REVIEWS) ---
        {reviews_text}
        
        --- YÊU CẦU ---
        Hãy phân tích sâu sắc các khía cạnh sau và trả về kết quả dưới dạng JSON VALID:
        1. "pros": 3-5 điểm mạnh vượt trội của sản phẩm.
        2. "cons": 3-5 điểm yếu hoặc vấn đề khách hàng hay phàn nàn.
        3. "target_audience": Mô tả chân dung khách hàng mục tiêu (Họ là ai? Nhu cầu gì?).
        4. "price_evaluation": Đánh giá mức giá này so với thị trường và chất lượng (Rẻ/Đắt/Hợp lý? Tại sao?).
        5. "marketing_suggestions": 3-5 gợi ý để bán sản phẩm này tốt hơn (USP, Content angle).

        OUTPUT FORMAT (JSON ONLY):
        {{
            "pros": ["..."],
            "cons": ["..."],
            "target_audience": "...",
            "price_evaluation": "...",
            "marketing_suggestions": ["..."]
        }}
        """
        
        # 4. Call LLM
        try:
            response = llm_agent.generate(prompt)
            response_text = response.text
            
            # Clean JSON string (remove markdown ```json ... ```)
            cleaned_text = response_text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            elif cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:] 
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
            cleaned_text = cleaned_text.strip()
            
            # Parse JSON
            analysis_data = json.loads(cleaned_text)
            
        except Exception as e:
            logger.error(f"LLM Analysis failed: {e}")
            # Fallback data
            analysis_data = {
                "pros": ["Lỗi phân tích"],
                "cons": ["Lỗi phân tích"],
                "target_audience": "Không xác định",
                "price_evaluation": "Không xác định",
                "marketing_suggestions": []
            }


        # 5. Save to DB
        existing_analysis = self.market_repo.get_by_product_id(product_id)
        
        if existing_analysis:
            # Update
            update_dto = ProductMarketAnalysisUpdate(**analysis_data)
            self.market_repo.update(db_obj=existing_analysis, obj_in=update_dto)
            return existing_analysis
        else:
            # Create
            create_dto = ProductMarketAnalysisCreate(
                product_id=product_id,
                **analysis_data
            )
            created = self.market_repo.create(obj_in=create_dto)
            return created
