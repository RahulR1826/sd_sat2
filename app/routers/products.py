"""Products Router – REST endpoints for product catalog."""
from typing import Optional
from fastapi import APIRouter, Query, Path, HTTPException, status

from app.models.product import Product, ProductSearchResponse
from app.services import product_service

router = APIRouter(prefix="/products", tags=["Products"])


@router.get(
    "/search",
    response_model=ProductSearchResponse,
    summary="Search Products",
    description=(
        "Search the product catalog by name, brand, or description. "
        "Supports category filtering, price range, and pagination."
    ),
    responses={
        200: {"description": "Search results returned successfully"},
        400: {"description": "Invalid query parameters"},
    },
)
def search_products(
    q: str = Query(..., min_length=1, description="Search keyword (name, brand, category)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=50, description="Items per page"),
):
    """
    **GET /api/v1/products/search**

    HTTP Method: `GET`
    URI: `/api/v1/products/search?q={query}&category={category}&min_price=&max_price=`

    Returns a paginated list of products matching the search query.

    **Status Codes:**
    - `200 OK` – Products found
    - `400 Bad Request` – Invalid query parameters
    """
    if min_price and max_price and min_price > max_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_price cannot be greater than max_price.",
        )
    return product_service.search_products(q, category, min_price, max_price, page, page_size)


@router.get(
    "/",
    response_model=ProductSearchResponse,
    summary="List All Products",
    description="Retrieve all available products, optionally filtered by category.",
)
def list_products(
    category: Optional[str] = Query(None, description="Filter by product category"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
):
    """
    **GET /api/v1/products/**

    HTTP Method: `GET`
    """
    return product_service.get_all_products(category, page, page_size)


@router.get(
    "/{product_id}",
    response_model=Product,
    summary="Get Product by ID",
    description="Retrieve a single product by its unique ID.",
    responses={
        200: {"description": "Product found"},
        404: {"description": "Product not found"},
    },
)
def get_product(
    product_id: str = Path(..., description="Unique product ID"),
):
    """
    **GET /api/v1/products/{product_id}**

    HTTP Method: `GET`
    URI: `/api/v1/products/{product_id}`

    **Status Codes:**
    - `200 OK` – Product found
    - `404 Not Found` – Product does not exist
    """
    product = product_service.get_product_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product '{product_id}' not found.",
        )
    return product
