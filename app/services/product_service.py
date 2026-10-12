"""Product Service – business logic for searching the product catalog."""
from typing import List, Optional
from app.models.product import Product, ProductSearchResponse
from app.database.in_memory_db import products_db


def search_products(
    query: str,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    page: int = 1,
    page_size: int = 10,
) -> ProductSearchResponse:
    """
    Search products by name / brand / description with optional filters.
    Simulates a full-text search + filter pipeline (Elasticsearch in prod).
    """
    query_lower = query.lower()

    results: List[Product] = [
        p for p in products_db.values()
        if (
            query_lower in p.name.lower()
            or query_lower in p.brand.lower()
            or query_lower in p.description.lower()
            or query_lower in p.category.value.lower()
        )
        and p.in_stock
        and (category is None or p.category.value == category)
        and (min_price is None or p.price >= min_price)
        and (max_price is None or p.price <= max_price)
    ]

    # Simulate relevance ranking: exact name match first
    results.sort(key=lambda p: (0 if query_lower in p.name.lower() else 1, p.name))

    total = len(results)
    start = (page - 1) * page_size
    paginated = results[start: start + page_size]

    return ProductSearchResponse(
        query=query,
        total_results=total,
        page=page,
        page_size=page_size,
        products=paginated,
    )


def get_product_by_id(product_id: str) -> Optional[Product]:
    """Fetch a single product by ID."""
    return products_db.get(product_id)


def get_all_products(
    category: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> ProductSearchResponse:
    """Return all in-stock products, optionally filtered by category."""
    results = [
        p for p in products_db.values()
        if p.in_stock and (category is None or p.category.value == category)
    ]
    total = len(results)
    start = (page - 1) * page_size
    paginated = results[start: start + page_size]

    return ProductSearchResponse(
        query="",
        total_results=total,
        page=page,
        page_size=page_size,
        products=paginated,
    )
