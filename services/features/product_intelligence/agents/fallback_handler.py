from typing import Dict, Any, List, Optional
from ..integrations.ecommerce import ShopeeProvider, LazadaProvider, TikiProvider


class FallbackHandler:

    PROVIDERS = [
        ShopeeProvider(),
        LazadaProvider(),
        TikiProvider(),
    ]
    
    @staticmethod
    def generate_search_links(
        search_keyword: str,
        budget: Optional[float] = None,
        ai_result: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, str]]:
        brands = FallbackHandler._extract_brands_from_ai_result(ai_result)
        links = []
        
        for provider in FallbackHandler.PROVIDERS:
            links.append({
                "title": provider.format_title(search_keyword),
                "url": provider.build_search_url(search_keyword, budget),
                "description": provider.format_description(search_keyword, None, budget),
                "platform": provider.platform_name
            })
            
            for brand in brands[:3]:
                links.append({
                    "title": provider.format_title(search_keyword, brand),
                    "url": provider.build_search_url(f"{brand} {search_keyword}", budget),
                    "description": provider.format_description(search_keyword, brand, budget),
                    "platform": provider.platform_name,
                    "brand": brand
                })
        
        return links
    
    @staticmethod
    def create_failure_response(
        search_keyword: str,
        budget: Optional[float],
        ai_result: Dict[str, Any],
        project_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        search_links = FallbackHandler.generate_search_links(
            search_keyword, 
            budget,
            ai_result
        )
        
        platforms = {}
        for link in search_links:
            platform = link.get("platform", "Other")
            if platform not in platforms:
                platforms[platform] = []
            platforms[platform].append(link)
        
        return {
            "project_info": {
                "id": str(project_info.get("id")),
                "name": project_info.get("name"),
                "description": project_info.get("description"),
                "target_product": search_keyword,
                "budget": budget
            },
            "ai_analysis": ai_result.get(
                "analysis", 
                "API không khả dụng. Đây là các link tìm kiếm được AI đề xuất trên nhiều sàn."
            ),
            "search_links_by_platform": platforms,
            "total_links": len(search_links),
            "total_platforms": len(platforms),
            "note": "Vui lòng click vào các links để tìm kiếm trực tiếp trên từng sàn.",
            "instruction": "Chọn sàn → Click link → Xem kết quả"
        }
    
    @staticmethod
    def _extract_brands_from_ai_result(ai_result: Optional[Dict[str, Any]]) -> List[str]:
        if not ai_result:
            return []
        
        brands = []
        
        products = ai_result.get("products", [])
        for product in products[:5]:
            name = product.get("name", "")
            shop_type = product.get("shop_type", "")
            
            if "Mall" in shop_type or "Thích" in shop_type:
                words = name.split()
                if words and len(words[0]) > 2:
                    potential_brand = words[0]
                    if potential_brand not in brands:
                        brands.append(potential_brand)
        
        analysis = ai_result.get("analysis", "")
        if analysis and not brands:
            import re
            capitalized_words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', analysis)
            for word in capitalized_words[:3]:
                if len(word) > 2 and word not in brands:
                    brands.append(word)
        
        return brands[:5]
