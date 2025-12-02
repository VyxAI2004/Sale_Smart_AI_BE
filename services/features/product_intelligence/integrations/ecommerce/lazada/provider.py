from typing import Optional
from ..base import BaseSearchProvider


class LazadaProvider(BaseSearchProvider):

    BASE_URL = "https://www.lazada.vn/catalog/?q="
    
    @property
    def platform_name(self) -> str:
        return "Lazada"
    
    def build_search_url(self, keyword: str, budget: Optional[float] = None) -> str:
        url = f"{self.BASE_URL}{keyword.replace(' ', '%20')}"
        return url
    
    def format_title(self, keyword: str, brand: Optional[str] = None) -> str:
        if brand:
            return f"{brand} {keyword} (Lazada)"
        return f"{keyword} (Lazada)"
    
    def format_description(
        self, 
        keyword: str, 
        brand: Optional[str], 
        budget: Optional[float]
    ) -> str:
        base = f"Lazada: {brand + ' ' if brand else ''}{keyword}"
        
        if budget:
            return f"{base} (Ngân sách: ~{budget:,.0f} VND)"
        
        return base
