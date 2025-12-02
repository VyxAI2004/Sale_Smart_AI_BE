
SEARCH_PRODUCT_PROMPT = """
Bạn là trợ lý mua sắm AI thông minh. Hãy sử dụng Google Search để tìm kiếm các sản phẩm THẬT trên Shopee Việt Nam.

Thông tin yêu cầu:
- Sản phẩm: {search_keyword}
- Mô tả: {description}
- Ngân sách: {budget_text}

Nhiệm vụ:
1. Tìm kiếm thông tin thực tế về các sản phẩm đang bán trên Shopee phù hợp với yêu cầu.
2. Trả về danh sách 5-10 sản phẩm TỐT NHẤT kèm LINK MUA HÀNG THẬT.

QUAN TRỌNG - VỀ LINK SẢN PHẨM (URL):
- TUYỆT ĐỐI KHÔNG tự bịa ra link (ví dụ: không dùng id 123456789).
- Link phải chứa ID thật của shop và sản phẩm (ví dụ: ...-i.12345.67890).
- Nếu không tìm thấy link thật, HÃY BỎ QUA sản phẩm đó.
- Chỉ trả về các sản phẩm có link truy cập được.

Format JSON trả về:
{{
    "analysis": "Phân tích thị trường và lý do chọn các sản phẩm này",
    "products": [
        {{
            "name": "Tên đầy đủ của sản phẩm",
            "price": 120000,
            "url": "https://shopee.vn/ten-san-pham-that-i.shopid.itemid",
            "rating": 4.9,
            "sold": 1000,
            "shop_name": "Tên Shop (nếu có)",
            "reason": "Lý do đề xuất"
        }}
    ]
}}
"""

RANKING_PRODUCT_PROMPT = """
Dựa trên danh sách {count} sản phẩm thật từ Shopee:

{products_summary}

Phân tích và chọn TOP {limit} sản phẩm TỐT NHẤT dựa trên:
- Giá phù hợp với ngân sách {budget_text}
- Rating cao
- Đã bán được nhiều
- Uy tín

Trả về JSON:
{{
    "analysis": "Phân tích ngắn gọn về các sản phẩm",
    "top_products": [
        {{
            "name": "tên sản phẩm",
            "price": giá,
            "url": "url_thật_từ_danh_sách",
            "rating": rating,
            "sold": số_bán,
            "reason": "Lý do chọn"
        }}
    ]
}}
"""
