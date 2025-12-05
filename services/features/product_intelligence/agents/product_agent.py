from typing import Dict, Any
from uuid import UUID
import logging
import re
from sqlalchemy.orm import Session

from .llm_provider_selector import LLMProviderSelector
from .search_handler import SearchHandler
from .ranking_handler import RankingHandler
from .fallback_handler import FallbackHandler

logger = logging.getLogger(__name__)


class ProductAIAgent:
    def __init__(self, db: Session):
        self.db = db
        self.llm_selector = LLMProviderSelector(db)
    
    def search_products(
        self, 
        project_info: Dict[str, Any], 
        user_id: UUID, 
        limit: int = 10
    ) -> Dict[str, Any]:
        search_keyword, budget, description = self._extract_project_data(project_info)
        
        logger.info(f"Starting product search for user {user_id}. Keyword: '{search_keyword}', Budget: {budget}")
        
        llm_agent = self.llm_selector.select_agent(
            user_id=user_id,
            project_assigned_model_id=project_info.get("assigned_model_id")
        )
        
        # Search
        search_handler = SearchHandler(llm_agent)
        search_result = search_handler.search(
            search_keyword=search_keyword,
            description=description,
            budget=budget,
            limit=limit
        )
        
        # Handle failures
        if not search_result["shopee_products"]:
            logger.warning(f"No products found on Shopee for '{search_keyword}'. Triggering fallback.")
            return FallbackHandler.create_failure_response(
                search_keyword=search_keyword,
                budget=budget,
                ai_result=search_result["ai_result"],
                project_info=project_info
            )
        
        # Rank products
        logger.info(f"Found {len(search_result['shopee_products'])} products. Starting ranking...")
        ranking_handler = RankingHandler(llm_agent)
        ranking_result = ranking_handler.rank_products(
            shopee_products=search_result["shopee_products"],
            budget_text=f"{budget:,.0f} VND" if budget else "không giới hạn",
            limit=limit
        )
        
        # Build final response
        return self._build_response(
            project_info=project_info,
            search_keyword=search_keyword,
            budget=budget,
            ranking_result=ranking_result,
            shopee_products=search_result["shopee_products"],
            grounding_metadata=search_result["grounding_metadata"]
        )
    
    @staticmethod
    def _extract_project_data(project_info: Dict[str, Any]) -> tuple:
        """Extract relevant data from project info with safe parsing"""
        search_keyword = project_info.get("target_product_name") or project_info.get("name")
        
        # Safe budget parsing
        budget = None
        raw_budget = project_info.get("target_budget_range")
        if raw_budget:
            try:
                # Remove non-numeric chars except dot (simple cleanup)
                clean_budget = re.sub(r'[^\d.]', '', str(raw_budget))
                if clean_budget:
                    budget = float(clean_budget)
            except (ValueError, TypeError):
                logger.warning(f"Failed to parse budget: {raw_budget}. Using None.")
                budget = None
                
        description = project_info.get("description") or ""
        return search_keyword, budget, description
    
    @staticmethod
    def _build_response(
        project_info: Dict[str, Any],
        search_keyword: str,
        budget: float,
        ranking_result: Dict[str, Any],
        shopee_products: list,
        grounding_metadata: Any
    ) -> Dict[str, Any]:
        """Build final response object"""
        return {
            "project_info": {
                "id": str(project_info.get("id")),
                "name": project_info.get("name"),
                "description": project_info.get("description"),
                "target_product": search_keyword,
                "budget": budget
            },
            "ai_analysis": ranking_result.get("analysis", "Products analyzed successfully"),
            "recommended_products": ranking_result.get("top_products", []),
            "all_shopee_products": shopee_products[:20],
            "total_found": len(shopee_products),
            "grounding_metadata": grounding_metadata,
            "note": "Sản phẩm được tìm kiếm thông qua Google Search Grounding và được AI phân tích."
        }
