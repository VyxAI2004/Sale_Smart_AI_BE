from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from core.dependencies.auth import verify_token
from core.dependencies.services import (
    get_product_review_service,
    get_review_analysis_service,
    get_product_service,
)
from schemas.auth import TokenData
from schemas.product_review import (
    ProductReviewCreate,
    ProductReviewUpdate,
    ProductReviewResponse,
    ProductReviewListResponse,
)
from schemas.review_analysis import ReviewAnalysisResponse
from services.core.product_review import ProductReviewService
from services.core.review_analysis import ReviewAnalysisService
from services.core.product import ProductService

router = APIRouter(prefix="/products/{product_id}/reviews", tags=["Product Reviews"])


@router.get("/", response_model=ProductReviewListResponse)
def get_product_reviews(
    product_id: UUID,
    platform: Optional[str] = Query(None, description="Filter by platform: shopee, lazada, tiki"),
    include_analysis: bool = Query(False, description="Include AI analysis data"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    review_service: ProductReviewService = Depends(get_product_review_service),
    product_service: ProductService = Depends(get_product_service),
    token: TokenData = Depends(verify_token),
):

    product = product_service.get(product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    if platform:
        reviews = review_service.get_reviews_by_platform(
            product_id=product_id,
            platform=platform,
            skip=skip,
            limit=limit
        )
        total = len(reviews)  
    else:
        reviews, total = review_service.get_product_reviews(
            product_id=product_id,
            skip=skip,
            limit=limit,
            include_analysis=include_analysis
        )
    
    return {
        "items": reviews,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/statistics")
def get_review_statistics(
    product_id: UUID,
    review_service: ProductReviewService = Depends(get_product_review_service),
    analysis_service: ReviewAnalysisService = Depends(get_review_analysis_service),
    product_service: ProductService = Depends(get_product_service),
    token: TokenData = Depends(verify_token),
):
    product = product_service.get(product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    review_stats = review_service.get_review_statistics(product_id)

    analysis_stats = analysis_service.get_statistics(product_id)
    
    return {
        "product_id": product_id,
        "reviews": review_stats,
        "analysis": analysis_stats
    }


@router.get("/unanalyzed")
def get_unanalyzed_reviews(
    product_id: UUID,
    limit: int = Query(100, ge=1, le=500),
    review_service: ProductReviewService = Depends(get_product_review_service),
    product_service: ProductService = Depends(get_product_service),
    token: TokenData = Depends(verify_token),
):

    product = product_service.get(product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    reviews = review_service.get_unanalyzed_reviews(product_id=product_id, limit=limit)
    
    return {
        "product_id": product_id,
        "unanalyzed_count": len(reviews),
        "reviews": reviews
    }


@router.get("/{review_id}", response_model=ProductReviewResponse)
def get_review_detail(
    product_id: UUID,
    review_id: UUID,
    review_service: ProductReviewService = Depends(get_product_review_service),
    token: TokenData = Depends(verify_token),
):
    review = review_service.get_review_with_analysis(review_id)
    
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    
    if review.product_id != product_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Review does not belong to this product")
    
    return review


@router.post("/", response_model=ProductReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    product_id: UUID,
    payload: ProductReviewCreate,
    review_service: ProductReviewService = Depends(get_product_review_service),
    product_service: ProductService = Depends(get_product_service),
    token: TokenData = Depends(verify_token),
):
    product = product_service.get(product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    if payload.product_id != product_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Product ID in payload does not match URL"
        )
    
    return review_service.create_review(payload)


@router.put("/{review_id}", response_model=ProductReviewResponse)
def update_review(
    product_id: UUID,
    review_id: UUID,
    payload: ProductReviewUpdate,
    review_service: ProductReviewService = Depends(get_product_review_service),
    token: TokenData = Depends(verify_token),
):
    review = review_service.get(review_id)
    
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    
    if review.product_id != product_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Review does not belong to this product")
    
    updated = review_service.update_review(review_id, payload)
    return updated


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    product_id: UUID,
    review_id: UUID,
    review_service: ProductReviewService = Depends(get_product_review_service),
    token: TokenData = Depends(verify_token),
):
    review = review_service.get(review_id)
    
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    
    if review.product_id != product_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Review does not belong to this product")
    
    review_service.delete_review(review_id)


@router.get("/{review_id}/analysis", response_model=ReviewAnalysisResponse)
def get_review_analysis(
    product_id: UUID,
    review_id: UUID,
    review_service: ProductReviewService = Depends(get_product_review_service),
    analysis_service: ReviewAnalysisService = Depends(get_review_analysis_service),
    token: TokenData = Depends(verify_token),
):
    review = review_service.get(review_id)
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    
    if review.product_id != product_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Review does not belong to this product")
    
    analysis = analysis_service.get_by_review(review_id)
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found for this review")
    
    return analysis


@router.post("/analyze", status_code=status.HTTP_200_OK)
def analyze_product_reviews(
    product_id: UUID,
    analysis_service: ReviewAnalysisService = Depends(get_review_analysis_service),
    product_service: ProductService = Depends(get_product_service),
    token: TokenData = Depends(verify_token),
):
    product = product_service.get(product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    try:
        analyses = analysis_service.analyze_product_reviews(product_id)
        
        from services.core.product_trust_score import ProductTrustScoreService
        from core.dependencies.services import get_product_trust_score_service
        from core.dependencies.db import get_db
        
        db = next(get_db())
        trust_score_service = ProductTrustScoreService(db)
        trust_score = trust_score_service.calculate_trust_score(product_id)
        
        return {
            "product_id": str(product_id),
            "analyses_created": len(analyses),
            "trust_score": float(trust_score.trust_score) if trust_score else None,
            "message": f"Analyzed {len(analyses)} reviews and calculated trust score"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing reviews: {str(e)}"
        )