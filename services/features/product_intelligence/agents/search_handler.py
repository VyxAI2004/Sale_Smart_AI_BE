from typing import Dict, Any
from core.llm.base import BaseAgent
from core.llm.utils import safe_json_parse
from prompts.product_ai import SEARCH_PRODUCT_PROMPT
from ..integrations.ecommerce.shopee import search_shopee_products
from .grounding_handler import GroundingHandler


class SearchHandler:
    def __init__(self, llm_agent: BaseAgent):
        self.llm = llm_agent
        self.grounding_handler = GroundingHandler()
    
    def search(
        self, 
        search_keyword: str, 
        description: str,
        budget: float,
        limit: int = 10
    ) -> Dict[str, Any]:
        budget_text = f"{budget:,.0f} VND" if budget else "không giới hạn"
        
        # 1. Get AI analysis & products via Grounding
        ai_result, grounding_metadata = self._get_ai_analysis(
            search_keyword, description, budget_text, limit
        )
        
        # 2. Extract products directly from AI result
        # Since we use Grounding, these should be real products found via Google Search
        shopee_products = ai_result.get("products", [])
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"AI found {len(shopee_products)} products via Grounding")
        
        return {
            "ai_result": ai_result,
            "shopee_products": shopee_products,
            "grounding_metadata": grounding_metadata
        }
    
    def _get_ai_analysis(
        self, 
        search_keyword: str, 
        description: str, 
        budget_text: str, 
        limit: int
    ) -> tuple:
        provider = self.llm.model_name().split("-")[0]
        search_tools = self.grounding_handler.create_search_tools(provider)
        
        prompt = SEARCH_PRODUCT_PROMPT.format(
            search_keyword=search_keyword,
            description=description,
            budget_text=budget_text,
            limit=limit
        )
        
        try:
            response = self.llm.generate(
                prompt=prompt,
                tools=search_tools,
                timeout=60.0
            )
            
            ai_result = safe_json_parse(response.text)
            grounding_metadata = self.grounding_handler.extract_grounding_metadata(response)
            
        except Exception as e:
            import logging
            import traceback
            logger = logging.getLogger(__name__)
            error_details = traceback.format_exc()
            logger.error(f"LLM search analysis failed: {str(e)}\n{error_details}")
            # Include error in result for debugging
            ai_result = {
                "error": str(e),
                "error_type": type(e).__name__,
                "analysis": f"Lỗi khi gọi AI: {str(e)}"
            }
            grounding_metadata = None
        
        return ai_result, grounding_metadata
    
    def _search_shopee(
        self, 
        search_keyword: str, 
        budget: float, 
        limit: int
    ) -> list:
        """Search Shopee API with price filters, retry without filters if empty"""
        min_price = budget * 0.7 if budget else None
        max_price = budget * 1.3 if budget else None
        
        # 1. Try with strict price filter
        products = search_shopee_products(
            keyword=search_keyword,
            limit=limit,
            min_price=min_price,
            max_price=max_price
        )
        
        # 2. If no products, try without price filter (if budget was set)
        if not products and budget:
            import logging
            logging.getLogger(__name__).info(f"No products found with price filter for '{search_keyword}'. Retrying without filters.")
            products = search_shopee_products(
                keyword=search_keyword,
                limit=limit,
                min_price=None,
                max_price=None
            )
            
        return products
