from typing import Dict, Any, List

from core.llm.base import BaseAgent
from core.llm.utils import safe_json_parse
from prompts.product_ai import RANKING_PRODUCT_PROMPT
from schemas.product_ai import RankingResponse


class RankingHandler:
    
    def __init__(self, llm_agent: BaseAgent):
        self.llm = llm_agent
    
    def rank_products(
        self,
        shopee_products: List[Dict],
        budget_text: str,
        limit: int
    ) -> Dict[str, Any]:
        if not shopee_products:
            return {
                "analysis": "No products to rank",
                "top_products": []
            }
        
        products_summary = self._create_products_summary(shopee_products[:20])
        
        prompt = RANKING_PRODUCT_PROMPT.format(
            count=len(shopee_products),
            products_summary=products_summary,
            limit=min(limit, len(shopee_products)),
            budget_text=budget_text
        )
        
        try:
            response = self.llm.generate(
                prompt=prompt,
                response_schema=RankingResponse,
                json_mode=True
            )
            
            ranking_result = safe_json_parse(response.text)
            
            return {
                "analysis": ranking_result.get("analysis", "Ranked products successfully"),
                "top_products": ranking_result.get("top_products", [])
            }
        
        except Exception as e:
            return {
                "analysis": f"Ranking failed: {str(e)}. Showing original order.",
                "top_products": shopee_products[:limit]
            }
    
    @staticmethod
    def _create_products_summary(products: List[Dict]) -> str:
        return "\n".join([
            f"- {p['name']}: {p['price']:,.0f} VND, Rating: {p['rating']}, Sold: {p['sold']}, URL: {p['url']}"
            for p in products
        ])
