import requests
import logging
import re
from typing import List, Dict, Any

# Setup logger
logger = logging.getLogger(__name__)

def search_shopee_products(keyword: str, limit: int = 20, min_price: float = None, max_price: float = None) -> List[Dict[str, Any]]:
    url = "https://shopee.vn/api/v4/search/search_items"
    
    params = {
        "keyword": keyword,
        "by": "relevancy",
        "limit": min(limit, 60),
        "newest": 0,
        "order": "desc",
        "page_type": "search",
        "scenario": "PAGE_GLOBAL_SEARCH",
        "version": 2,
        "view_session_id": "",
    }
    
    if min_price is not None:
        params["price_min"] = int(min_price * 100000)
    if max_price is not None:
        params["price_max"] = int(max_price * 100000)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": f"https://shopee.vn/search?keyword={keyword.replace(' ', '%20')}",
        "Accept": "application/json",
        "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
        "X-Requested-With": "XMLHttpRequest",
        "X-API-Source": "pc",
    }
    
    try:
        logger.info(f"Searching Shopee for '{keyword}' (Price: {min_price}-{max_price})")
        response = requests.get(url, params=params, headers=headers, timeout=15)
        
        if response.status_code != 200:
            logger.error(f"Shopee API returned status {response.status_code}: {response.text[:200]}")
            return []
        
        data = response.json()
        items = data.get("items", [])
        
        if not items:
            logger.warning(f"No items found for keyword '{keyword}'")
            return []
        
        products = []
        
        for item in items[:limit]:
            item_basic = item.get("item_basic", {})
            
            # Price calculations (Shopee stores price * 100000)
            price = item_basic.get("price", 0) / 100000
            price_min = item_basic.get("price_min", 0) / 100000
            price_max = item_basic.get("price_max", 0) / 100000
            
            # Build product URL
            shop_id = item_basic.get("shopid")
            item_id = item_basic.get("itemid")
            name = item_basic.get("name", "")
            
            # Create slug
            name_slug = name.lower().replace(" ", "-").replace("/", "-")
            name_slug = re.sub(r'[^a-z0-9-]', '', name_slug)
            
            product_url = f"https://shopee.vn/{name_slug}-i.{shop_id}.{item_id}"
            
            product = {
                "name": name,
                "price": price if price > 0 else price_min,
                "price_min": price_min,
                "price_max": price_max,
                "currency": "VND",
                "url": product_url,
                "image": f"https://cf.shopee.vn/file/{item_basic.get('image', '')}",
                "rating": item_basic.get("item_rating", {}).get("rating_star", 0) if item_basic.get("item_rating") else 0,
                "sold": item_basic.get("sold", 0),
                "shop_name": item_basic.get("shop_name", ""),
                "shopid": shop_id,
                "itemid": item_id,
            }
            
            products.append(product)
        
        logger.info(f"Found {len(products)} products on Shopee")
        return products
        
    except requests.exceptions.Timeout:
        logger.error("Shopee API request timed out")
        return []
    except Exception as e:
        logger.error(f"Shopee search error: {str(e)}", exc_info=True)
        return []
