from abc import ABC, abstractmethod
from typing import Optional


class BaseSearchProvider(ABC):
    @property
    @abstractmethod
    def platform_name(self) -> str:
        pass
    
    @abstractmethod
    def build_search_url(self, keyword: str, budget: Optional[float] = None) -> str:
        pass
    
    @abstractmethod
    def format_title(self, keyword: str, brand: Optional[str] = None) -> str:
        pass
    
    @abstractmethod
    def format_description(
        self, 
        keyword: str, 
        brand: Optional[str], 
        budget: Optional[float]
    ) -> str:
        pass
