import requests
import re
import csv
import time
import random

# Header tối thiểu nhưng đủ "người thật"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://shopee.vn/",
    "Accept-Language": "vi-VN,vi;q=0.9",
}

def extract_ids(product_url: str):
    """Tách shopid và itemid từ URL Shopee"""
    match = re.search(r"-i\.(\d+)\.(\d+)", product_url) or re.search(r"/(\d+)/(\d+)", product_url)
    if not match:
        raise ValueError("URL không đúng định dạng Shopee!")
    return match.group(1), match.group(2)

def get_only_text_comments(shopid, itemid, max_count=10000):
    """Chỉ lấy text comment, cực nhanh"""
    url = "https://shopee.vn/api/v4/item/get_ratings"   # v4 vẫn ngon nhất 2025
    offset = 0
    limit = 59                                          # Tối đa cho phép
    comments = []
    
    print("Đang cào comment (chỉ text)...", end="")
    
    while len(comments) < max_count:
        params = {
            "itemid": itemid,
            "shopid": shopid,
            "offset": offset,
            "limit": limit,
            "flag": 1,
            "filter": 0,      # 0 = tất cả
            "type": 0,
        }
        
        try:
            r = requests.get(url, params=params, headers=HEADERS, timeout=10)
            data = r.json()
            ratings = data.get("data", {}).get("ratings", [])
            
            if not ratings:
                print("\nHết comment hoặc bị chặn tạm thời!")
                break
                
            for item in ratings:
                comment_text = item.get("comment", "").strip()
                # Bỏ qua comment rỗng hoặc chỉ có ảnh/video
                if not comment_text:
                    continue
                    
                comments.append({
                    "rating_star": item["rating_star"],
                    "username": item["author_username"],
                    "comment": comment_text,
                    "time": time.strftime("%Y-%m-%d %H:%M", time.localtime(item["ctime"]))
                })
                
                if len(comments) >= max_count:
                    print(f"\nĐã đủ {max_count} comment có nội dung text!")
                    return comments
            
            offset += limit
            print(f"\rĐã lấy {len(comments)} comment...", end="")
            time.sleep(random.uniform(0.2, 0.6))  # Siêu nhẹ nên delay ít hơn cũng ok
            
        except Exception as e:
            print(f"\nLỗi: {e} – Đang thử lại sau 5s...")
            time.sleep(5)
    
    return comments

def save_simple_csv(data, filename=None):
    if not data:
        print("Không có comment nào để lưu!")
        return
        
    if filename is None:
        filename = f"shopee_comments_only_text_{int(time.time())}.csv"
        
    keys = ["rating_star", "username", "comment", "time"]
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
        
    print(f"Đã lưu {len(data)} comment (chỉ text) vào: {filename}")

# ========================== CHẠY CHƯƠNG TRÌNH ==========================
if __name__ == "__main__":
    url = input("Nhập link sản phẩm Shopee: ").strip()
    try:
        shopid, itemid = extract_ids(url)
        print(f"Shop ID: {shopid} | Item ID: {itemid}")
        
        comments = get_only_text_comments(shopid, itemid, max_count=20000)  # Tăng thoải mái
        save_simple_csv(comments)
        
    except Exception as e:
        print("Lỗi:", e)