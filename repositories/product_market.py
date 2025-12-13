from sqlalchemy.orm import Session
from repositories.base import BaseRepository
from models.product_market import ProductMarketAnalysis

from schemas.product_market import ProductMarketAnalysisCreate, ProductMarketAnalysisUpdate

class ProductMarketAnalysisRepository(BaseRepository[ProductMarketAnalysis, ProductMarketAnalysisCreate, ProductMarketAnalysisUpdate]):
    def __init__(self, db: Session):
        super().__init__(ProductMarketAnalysis, db)
    
    def get_by_product_id(self, product_id: str) -> ProductMarketAnalysis | None:
        return self.db.query(self.model).filter(self.model.product_id == product_id).first()
