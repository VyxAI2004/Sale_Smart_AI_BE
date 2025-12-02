from typing import Optional
from ..base import BaseSearchProvider


class ShopeeProvider(BaseSearchProvider):

    BASE_URL = "https://shopee.vn/search?keyword="
    
    @property
    def platform_name(self) -> str:
        return "Shopee"
    
    def build_search_url(self, keyword: str, budget: Optional[float] = None) -> str:
        url = f"{self.BASE_URL}{keyword.replace(' ', '%20')}"
        
        if budget:
            min_price = int(budget * 0.7)
            max_price = int(budget * 1.3)
            url += f"&minPrice={min_price}&maxPrice={max_price}"
        
        return url
    
    def format_title(self, keyword: str, brand: Optional[str] = None) -> str:
        if brand:
            return f"{brand} {keyword} (Shopee)"
        return f"{keyword} (Shopee)"
    
    def format_description(
        self, 
        keyword: str, 
        brand: Optional[str], 
        budget: Optional[float]
    ) -> str:
        base = f"Shopee: {brand + ' ' if brand else ''}{keyword}"
        
        if budget:
            return f"{base} ~ {budget*0.7:,.0f} - {budget*1.3:,.0f} VND"
        
        return base
