from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class ProductCategory(str, Enum):
    FRUITS = "fruits"
    VEGETABLES = "vegetables"
    DAIRY = "dairy"
    BEVERAGES = "beverages"
    SNACKS = "snacks"
    BAKERY = "bakery"
    MEAT = "meat"
    FROZEN = "frozen"
    PERSONAL_CARE = "personal_care"
    HOUSEHOLD = "household"


class Product(BaseModel):
    """Represents a product in the quick-commerce catalog."""
    id: str = Field(..., description="Unique product ID")
    name: str = Field(..., description="Product name")
    description: str = Field(..., description="Product description")
    price: float = Field(..., gt=0, description="Price in INR")
    category: ProductCategory = Field(..., description="Product category")
    brand: str = Field(..., description="Brand name")
    unit: str = Field(..., description="Unit of measurement (e.g., 500g, 1L)")
    image_url: Optional[str] = Field(None, description="Product image URL")
    rating: Optional[float] = Field(None, ge=0, le=5, description="Average rating")
    in_stock: bool = Field(True, description="Whether product is in stock")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "PROD-001",
                "name": "Amul Full Cream Milk",
                "description": "Fresh full cream milk packed hygienically",
                "price": 68.0,
                "category": "dairy",
                "brand": "Amul",
                "unit": "1L",
                "image_url": "https://cdn.example.com/amul-milk.jpg",
                "rating": 4.5,
                "in_stock": True
            }
        }
    }


class ProductSearchResponse(BaseModel):
    """Response model for product search results."""
    status: str = Field("success", description="Response status")
    query: str = Field(..., description="Search query used")
    total_results: int = Field(..., description="Total number of results found")
    page: int = Field(1, description="Current page number")
    page_size: int = Field(10, description="Number of results per page")
    products: List[Product] = Field(..., description="List of matching products")

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "success",
                "query": "milk",
                "total_results": 3,
                "page": 1,
                "page_size": 10,
                "products": []
            }
        }
    }
