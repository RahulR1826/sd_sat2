"""Inventory Router – check nearby store inventory for a product."""
from fastapi import APIRouter, Query, Path

from app.models.inventory import NearbyInventoryResponse
from app.services import inventory_service

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get(
    "/nearby",
    response_model=NearbyInventoryResponse,
    summary="Check Nearby Inventory",
    description=(
        "Find all stores within a given radius (km) that have the specified product in stock. "
        "Results are sorted by distance from the user."
    ),
    responses={
        200: {"description": "Nearby inventory list returned"},
        400: {"description": "Invalid parameters"},
    },
)
def check_nearby_inventory(
    product_id: str = Query(..., description="Product ID to check inventory for"),
    lat: float = Query(..., ge=-90, le=90, description="User's current latitude"),
    lng: float = Query(..., ge=-180, le=180, description="User's current longitude"),
    radius_km: float = Query(5.0, ge=0.5, le=20.0, description="Search radius in km (default 5 km)"),
):
    """
    **GET /api/v1/inventory/nearby**

    HTTP Method: `GET`
    URI: `/api/v1/inventory/nearby?product_id={id}&lat={lat}&lng={lng}&radius_km={km}`

    Uses the **Haversine formula** to compute distances between the user's coordinates
    and each store's coordinates.

    **Status Codes:**
    - `200 OK` – Returns list of stores (empty list if none found within radius)
    - `400 Bad Request` – Invalid coordinate or radius values
    """
    return inventory_service.check_nearby_inventory(product_id, lat, lng, radius_km)
