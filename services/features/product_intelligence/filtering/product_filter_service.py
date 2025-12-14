from typing import List, Tuple, Dict, Any
import logging

from schemas.product_crawler import CrawledProductItemExtended
from schemas.product_filter import ProductFilterCriteria

logger = logging.getLogger(__name__)


class ProductFilterService:
    """Filter products based on criteria"""
    
    def filter_products(
        self,
        products: List[CrawledProductItemExtended],
        criteria: ProductFilterCriteria
    ) -> List[CrawledProductItemExtended]:
        """Filter products based on criteria"""
        
        filtered = []
        
        for product in products:
            if self._matches_criteria(product, criteria):
                filtered.append(product)
        
        return filtered
    
    def filter_products_with_reasons(
        self,
        products: List[CrawledProductItemExtended],
        criteria: ProductFilterCriteria
    ) -> Tuple[List[CrawledProductItemExtended], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Filter products and return both passed and rejected products with reasons
        Returns: (filtered_products, rejected_products_with_reasons, passed_products_with_reasons)
        """
        filtered = []
        rejected = []
        passed = []
        
        for product in products:
            match_result, reason = self._matches_criteria_with_reason(product, criteria)
            if match_result:
                filtered.append(product)
                # Generate reason why product passed
                passed_reason = self._generate_passed_reason(product, criteria)
                passed.append({
                    "product_name": product.product_name,
                    "product_url": product.product_url,
                    "platform": product.platform,
                    "price": product.price_current,
                    "rating": product.rating_score,
                    "review_count": product.review_count,
                    "sales_count": product.sales_count,
                    "is_mall": product.is_mall,
                    "brand": product.brand,
                    "reason": passed_reason
                })
            else:
                rejected.append({
                    "product_name": product.product_name,
                    "product_url": product.product_url,
                    "platform": product.platform,
                    "price": product.price_current,
                    "rating": product.rating_score,
                    "review_count": product.review_count,
                    "sales_count": product.sales_count,
                    "is_mall": product.is_mall,
                    "brand": product.brand,
                    "reason": reason
                })
        
        return filtered, rejected, passed
    
    def _generate_passed_reason(
        self,
        product: CrawledProductItemExtended,
        criteria: ProductFilterCriteria
    ) -> str:
        """Generate reason why product passed all criteria"""
        reasons = []
        
        # Rating
        if criteria.min_rating is not None:
            if product.rating_score is not None:
                reasons.append(f"Rating: {product.rating_score:.1f} (≥ {criteria.min_rating})")
        if criteria.max_rating is not None:
            if product.rating_score is not None:
                reasons.append(f"Rating: {product.rating_score:.1f} (≤ {criteria.max_rating})")
        
        # Review count
        if criteria.min_review_count is not None:
            if product.review_count is not None:
                reasons.append(f"Reviews: {product.review_count} (≥ {criteria.min_review_count})")
        if criteria.max_review_count is not None:
            if product.review_count is not None:
                reasons.append(f"Reviews: {product.review_count} (≤ {criteria.max_review_count})")
        
        # Price
        if criteria.min_price is not None:
            reasons.append(f"Giá: {product.price_current:,.0f} VND (≥ {criteria.min_price:,.0f} VND)")
        if criteria.max_price is not None:
            reasons.append(f"Giá: {product.price_current:,.0f} VND (≤ {criteria.max_price:,.0f} VND)")
        
        # Platform
        if criteria.platforms is not None:
            reasons.append(f"Platform: {product.platform} (trong {', '.join(criteria.platforms)})")
        
        # Mall
        if criteria.is_mall is not None:
            mall_text = "Mall" if product.is_mall else "Không phải Mall"
            reasons.append(f"Loại seller: {mall_text}")
        
        # Verified seller
        if criteria.is_verified_seller is not None:
            verified_text = "Đã xác thực" if product.is_verified_seller else "Chưa xác thực"
            reasons.append(f"Xác thực: {verified_text}")
        
        # Required keywords
        if criteria.required_keywords is not None:
            reasons.append(f"Có từ khóa: {', '.join(criteria.required_keywords)}")
        
        # Sales count
        if criteria.min_sales_count is not None:
            if product.sales_count is not None:
                reasons.append(f"Đã bán: {product.sales_count} (≥ {criteria.min_sales_count})")
        
        # Trust score
        if criteria.min_trust_score is not None:
            if product.trust_score is not None:
                reasons.append(f"Trust score: {product.trust_score} (≥ {criteria.min_trust_score})")
        
        # Trust badge
        if criteria.trust_badge_types is not None:
            if product.trust_badge_type is not None:
                reasons.append(f"Trust badge: {product.trust_badge_type}")
        
        # Required brands
        if criteria.required_brands is not None:
            if product.brand is not None:
                reasons.append(f"Thương hiệu: {product.brand} (trong {', '.join(criteria.required_brands)})")
        
        # Seller location
        if criteria.seller_locations is not None:
            if product.seller_location is not None:
                reasons.append(f"Vị trí seller: {product.seller_location} (trong {', '.join(criteria.seller_locations)})")
        
        if reasons:
            return "Đạt tất cả tiêu chí: " + "; ".join(reasons)
        return "Đạt tất cả tiêu chí (không có tiêu chí lọc cụ thể)"
    
    def _matches_criteria(
        self,
        product: CrawledProductItemExtended,
        criteria: ProductFilterCriteria
    ) -> bool:
        """Check if product matches all criteria"""
        match_result, _ = self._matches_criteria_with_reason(product, criteria)
        return match_result
    
    def _matches_criteria_with_reason(
        self,
        product: CrawledProductItemExtended,
        criteria: ProductFilterCriteria
    ) -> Tuple[bool, str]:
        """
        Check if product matches all criteria and return reason if not
        Returns: (matches, reason)
        """
        
        reasons = []
        
        # Rating filter
        if criteria.min_rating is not None:
            if product.rating_score is None:
                reasons.append(f"Không có rating (yêu cầu: ≥ {criteria.min_rating})")
            elif product.rating_score < criteria.min_rating:
                reasons.append(f"Rating quá thấp: {product.rating_score:.1f} (yêu cầu: ≥ {criteria.min_rating})")
        
        if criteria.max_rating is not None:
            if product.rating_score is not None and product.rating_score > criteria.max_rating:
                reasons.append(f"Rating quá cao: {product.rating_score:.1f} (yêu cầu: ≤ {criteria.max_rating})")
        
        if criteria.min_review_count is not None:
            if product.review_count is None:
                reasons.append(f"Không có review (yêu cầu: ≥ {criteria.min_review_count})")
            elif product.review_count < criteria.min_review_count:
                reasons.append(f"Số review quá ít: {product.review_count} (yêu cầu: ≥ {criteria.min_review_count})")
        
        if criteria.max_review_count is not None:
            if product.review_count is not None and product.review_count > criteria.max_review_count:
                reasons.append(f"Số review quá nhiều: {product.review_count} (yêu cầu: ≤ {criteria.max_review_count})")
        
        # Price filter
        if criteria.min_price is not None:
            if product.price_current < criteria.min_price:
                reasons.append(f"Giá quá thấp: {product.price_current:,.0f} VND (yêu cầu: ≥ {criteria.min_price:,.0f} VND)")
        
        if criteria.max_price is not None:
            if product.price_current > criteria.max_price:
                reasons.append(f"Giá quá cao: {product.price_current:,.0f} VND (yêu cầu: ≤ {criteria.max_price:,.0f} VND)")
        
        # Platform filter
        if criteria.platforms is not None:
            if product.platform not in criteria.platforms:
                reasons.append(f"Platform không phù hợp: {product.platform} (yêu cầu: {', '.join(criteria.platforms)})")
        
        # Mall filter
        if criteria.is_mall is not None:
            if product.is_mall != criteria.is_mall:
                expected = "Mall" if criteria.is_mall else "Không phải Mall"
                actual = "Mall" if product.is_mall else "Không phải Mall"
                reasons.append(f"Loại seller không phù hợp: {actual} (yêu cầu: {expected})")
        
        # Verified seller filter
        if criteria.is_verified_seller is not None:
            if product.is_verified_seller != criteria.is_verified_seller:
                expected = "Đã xác thực" if criteria.is_verified_seller else "Chưa xác thực"
                actual = "Đã xác thực" if product.is_verified_seller else "Chưa xác thực"
                reasons.append(f"Trạng thái xác thực không phù hợp: {actual} (yêu cầu: {expected})")
        
        # Required keywords filter
        if criteria.required_keywords is not None:
            product_name_lower = product.product_name.lower()
            missing_keywords = [kw for kw in criteria.required_keywords if kw.lower() not in product_name_lower]
            if missing_keywords:
                reasons.append(f"Thiếu từ khóa bắt buộc: {', '.join(missing_keywords)}")
        
        # Excluded keywords filter
        if criteria.excluded_keywords is not None:
            product_name_lower = product.product_name.lower()
            found_keywords = [kw for kw in criteria.excluded_keywords if kw.lower() in product_name_lower]
            if found_keywords:
                reasons.append(f"Có từ khóa loại trừ: {', '.join(found_keywords)}")
        
        # Sales count filter
        if criteria.min_sales_count is not None:
            if product.sales_count is None:
                reasons.append(f"Không có thông tin số lượng bán (yêu cầu: ≥ {criteria.min_sales_count})")
            elif product.sales_count < criteria.min_sales_count:
                reasons.append(f"Số lượng bán quá ít: {product.sales_count} (yêu cầu: ≥ {criteria.min_sales_count})")
        
        # Trust score filter
        if criteria.min_trust_score is not None:
            if product.trust_score is None:
                reasons.append(f"Không có trust score (yêu cầu: ≥ {criteria.min_trust_score})")
            elif product.trust_score < criteria.min_trust_score:
                reasons.append(f"Trust score quá thấp: {product.trust_score} (yêu cầu: ≥ {criteria.min_trust_score})")
        
        # Trust badge filter
        if criteria.trust_badge_types is not None:
            if product.trust_badge_type is None:
                reasons.append(f"Không có trust badge (yêu cầu: {', '.join(criteria.trust_badge_types)})")
            elif product.trust_badge_type not in criteria.trust_badge_types:
                reasons.append(f"Trust badge không phù hợp: {product.trust_badge_type} (yêu cầu: {', '.join(criteria.trust_badge_types)})")
        
        # Required brands filter
        if criteria.required_brands is not None:
            if product.brand is None:
                reasons.append(f"Không có thương hiệu (yêu cầu: {', '.join(criteria.required_brands)})")
            elif product.brand not in criteria.required_brands:
                reasons.append(f"Thương hiệu không phù hợp: {product.brand} (yêu cầu: {', '.join(criteria.required_brands)})")
        
        # Excluded brands filter
        if criteria.excluded_brands is not None:
            if product.brand is not None and product.brand in criteria.excluded_brands:
                reasons.append(f"Thương hiệu bị loại trừ: {product.brand}")
        
        # Seller location filter
        if criteria.seller_locations is not None:
            if product.seller_location is None:
                reasons.append(f"Không có thông tin vị trí seller (yêu cầu: {', '.join(criteria.seller_locations)})")
            elif product.seller_location not in criteria.seller_locations:
                reasons.append(f"Vị trí seller không phù hợp: {product.seller_location} (yêu cầu: {', '.join(criteria.seller_locations)})")
        
        if reasons:
            return False, "; ".join(reasons)
        return True, ""

