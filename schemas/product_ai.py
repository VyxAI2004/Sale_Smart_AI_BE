from typing import List
from pydantic import BaseModel, Field
# Define Pydantic models for Structured Output
class ProductItem(BaseModel):
    name: str = Field(description="Full name of the product")
    price: float = Field(description="Price in VND")
    url: str = Field(description="Direct URL to the product")
    rating: float = Field(description="Product rating (0-5)")
    sold: int = Field(description="Number of items sold")
    shop_type: str = Field(description="Shop type (e.g., Shopee Mall, Shop Yêu Thích+)")
    reason: str = Field(description="Reason for recommending this product")

class PriceRange(BaseModel):
    min: float
    average: float
    max: float

class SearchResponse(BaseModel):
    analysis: str = Field(description="Market analysis and price trends")
    products: List[ProductItem]
    price_range: PriceRange

class RankedProduct(BaseModel):
    name: str
    price: float
    url: str
    rating: float
    sold: int
    reason: str

class RankingResponse(BaseModel):
    analysis: str
    top_products: List[RankedProduct]