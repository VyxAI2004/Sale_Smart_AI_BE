import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from models.product import Product
from repositories.product import ProductFilters, ProductRepository
from schemas.product import ProductCreate, ProductUpdate
from .base import BaseService
from .permission import PermissionService

class ProductService(BaseService[Product, ProductCreate, ProductUpdate, ProductRepository]):
    def __init__(self, db: Session):
        super().__init__(db, Product, ProductRepository)

    def create_product(self, payload: ProductCreate, user_id: uuid.UUID) -> Product:
        """Create a new product"""
        # Check permission on project
        permission_service = PermissionService(self.db)
        if not permission_service.has_permission(user_id, "project:manage_products", payload.project_id):
            raise ValueError("You don't have permission to add products to this project")
        
        return self.create(payload)

    def update_product(self, product_id: uuid.UUID, payload: ProductUpdate, user_id: uuid.UUID) -> Optional[Product]:
        """Update product"""
        db_product = self.get(product_id)
        if not db_product:
            return None
        
        # Check permission
        permission_service = PermissionService(self.db)
        if not permission_service.has_permission(user_id, "project:manage_products", db_product.project_id):
            raise ValueError("You don't have permission to update products in this project")
        
        return self.update(db_obj=db_product, payload=payload)

    def delete_product(self, product_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """Delete product"""
        db_product = self.get(product_id)
        if not db_product:
            raise ValueError("Product not found")
        
        # Check permission
        permission_service = PermissionService(self.db)
        if not permission_service.has_permission(user_id, "project:manage_products", db_product.project_id):
            raise ValueError("You don't have permission to delete products in this project")
        
        self.delete(id=product_id)

    def get_project_products(self, project_id: uuid.UUID, user_id: uuid.UUID, skip: int = 0, limit: int = 100, filters: Optional[ProductFilters] = None) -> tuple[List[Product], int]:
        """Get products for a project with filters"""
        # Check permission (read access)
        permission_service = PermissionService(self.db)
        if not permission_service.has_permission(user_id, "project:view", project_id):
            raise ValueError("You don't have permission to view this project")

        if filters is None:
            filters = {}
        
        filters["project_id"] = project_id
        
        # Get products
        products = self.repository.get_multi(skip=skip, limit=limit, filters=filters)
        
        # Count total
        total = self.count(filters=filters)
        
        return products, total
