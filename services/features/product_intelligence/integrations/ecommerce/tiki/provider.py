from typing import Optional
from ..base import BaseSearchProvider


class TikiProvider(BaseSearchProvider):

    BASE_URL = "https://tiki.vn/search?q="
    
    @property
    def platform_name(self) -> str:
        return "Tiki"
    
    def build_search_url(self, keyword: str, budget: Optional[float] = None) -> str:
        url = f"{self.BASE_URL}{keyword.replace(' ', '+')}"
        
        if budget:
            min_price = int(budget * 0.7)
            max_price = int(budget * 1.3)
            url += f"&price_from={min_price}&price_to={max_price}"
        
        return url
    
    def format_title(self, keyword: str, brand: Optional[str] = None) -> str:
        if brand:
            return f"{brand} {keyword} (Tiki)"
        return f"{keyword} (Tiki)"
    
    def format_description(
        self, 
        keyword: str, 
        brand: Optional[str], 
        budget: Optional[float]
    ) -> str:
        base = f"Tiki: {brand + ' ' if brand else ''}{keyword}"
        
        if budget:
            return f"{base} ~ {budget*0.7:,.0f} - {budget*1.3:,.0f} VND"
        
        return base
