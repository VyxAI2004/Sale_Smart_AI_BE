from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.dependencies.db import get_db
from core.dependencies.auth import verify_token
from core.dependencies.services import get_product_service
from schemas.auth import TokenData
from schemas.product import ProductCreate, ProductResponse, ProductUpdate, ProductListResponse
from services.core.product import ProductService
from repositories.product import ProductFilters

router = APIRouter(prefix="/products", tags=["Products"])

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreate,
    service: ProductService = Depends(get_product_service),
    token: TokenData = Depends(verify_token),
):
    """Create a new product"""
    try:
        return service.create_product(payload, token.user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: UUID,
    service: ProductService = Depends(get_product_service),
    token: TokenData = Depends(verify_token),
):
    """Get product by ID"""
    product = service.get(product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    # Optional: Check if user has access to the project this product belongs to
    # This might be strict, but good for security.
    # For MVP, assuming if they have the ID they can view, or we can add check.
    return product

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: UUID,
    payload: ProductUpdate,
    service: ProductService = Depends(get_product_service),
    token: TokenData = Depends(verify_token),
):
    """Update product"""
    try:
        product = service.update_product(product_id, payload, token.user_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return product
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: UUID,
    service: ProductService = Depends(get_product_service),
    token: TokenData = Depends(verify_token),
):
    """Delete product"""
    try:
        service.delete_product(product_id, token.user_id)
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

@router.get("/project/{project_id}", response_model=ProductListResponse)
def get_project_products(
    project_id: UUID,
    q: Optional[str] = Query(None, description="Search query"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, description="Min price"),
    max_price: Optional[float] = Query(None, description="Max price"),
    skip: int = 0,
    limit: int = 100,
    service: ProductService = Depends(get_product_service),
    token: TokenData = Depends(verify_token),
):
    """Get all products in a project"""
    filters = ProductFilters(
        q=q,
        platform=platform,
        category=category,
        min_price=min_price,
        max_price=max_price
    )
    try:
        products, total = service.get_project_products(project_id, token.user_id, skip, limit, filters)
        return {
            "items": products,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
