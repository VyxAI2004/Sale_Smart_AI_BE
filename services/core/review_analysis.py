"""
Service cho Review Analysis - Business Logic Layer.
Xử lý logic nghiệp vụ liên quan đến phân tích reviews.
"""
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from models.product import ReviewAnalysis
from repositories.review_analysis import ReviewAnalysisRepository
from schemas.review_analysis import ReviewAnalysisCreate, ReviewAnalysisUpdate

from .base import BaseService


class ReviewAnalysisService(BaseService[ReviewAnalysis, ReviewAnalysisCreate, ReviewAnalysisUpdate, ReviewAnalysisRepository]):
    """Service để quản lý ReviewAnalysis"""

    def __init__(self, db: Session):
        super().__init__(db, ReviewAnalysis, ReviewAnalysisRepository)

    def get_by_review(self, review_id: UUID) -> Optional[ReviewAnalysis]:
        """Lấy analysis của một review"""
        return self.repository.get_by_review(review_id)

    def get_by_product(
        self,
        product_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[ReviewAnalysis]:
        """Lấy tất cả analyses của reviews thuộc một product"""
        return self.repository.get_by_product(
            product_id=product_id,
            skip=skip,
            limit=limit
        )

    def create_analysis(self, payload: ReviewAnalysisCreate) -> ReviewAnalysis:
        """
        Tạo analysis mới.
        Nếu review đã có analysis, sẽ update thay vì tạo mới.
        """
        return self.repository.upsert(payload)

    def bulk_create_analyses(self, analyses: List[ReviewAnalysisCreate]) -> List[ReviewAnalysis]:
        """Tạo nhiều analyses cùng lúc (cho batch processing)"""
        return self.repository.bulk_create(analyses)

    def update_analysis(
        self,
        analysis_id: UUID,
        payload: ReviewAnalysisUpdate
    ) -> Optional[ReviewAnalysis]:
        """Cập nhật analysis"""
        db_analysis = self.get(analysis_id)
        if not db_analysis:
            return None
        return self.update(db_obj=db_analysis, payload=payload)

    def get_sentiment_distribution(self, product_id: UUID) -> dict:
        """
        Lấy phân bố sentiment cho một product.
        Returns: {"positive": x, "negative": y, "neutral": z}
        """
        counts = self.repository.count_by_sentiment(product_id)
        # Ensure all labels are present
        return {
            "positive": counts.get("positive", 0),
            "negative": counts.get("negative", 0),
            "neutral": counts.get("neutral", 0)
        }

    def get_spam_count(self, product_id: UUID) -> int:
        """Đếm số spam reviews cho một product"""
        return self.repository.count_spam(product_id)

    def get_statistics(self, product_id: UUID) -> dict:
        """
        Lấy thống kê tổng hợp analyses cho một product.
        Returns: {
            "total_analyzed": int,
            "sentiment_counts": {"positive": x, "negative": y, "neutral": z},
            "spam_count": int,
            "spam_percentage": float,
            "average_sentiment_score": float
        }
        """
        stats = self.repository.get_statistics(product_id)
        
        # Calculate spam percentage
        total = stats["total_analyzed"]
        spam_percentage = (stats["spam_count"] / total * 100) if total > 0 else 0.0
        
        return {
            **stats,
            "spam_percentage": round(spam_percentage, 2)
        }

    def has_analysis(self, review_id: UUID) -> bool:
        """Kiểm tra review đã có analysis chưa"""
        return self.repository.get_by_review(review_id) is not None
