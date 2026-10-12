from pydantic import BaseModel, Field
from typing import List, Optional


class StoreLocation(BaseModel):
    """Represents a physical store's geo-location."""
    store_id: str = Field(..., description="Unique store ID")
    store_name: str = Field(..., description="Name of the store/dark store")
    latitude: float = Field(..., description="Store latitude")
    longitude: float = Field(..., description="Store longitude")
    address: str = Field(..., description="Store address")
    distance_km: float = Field(..., description="Distance from user in km")
    delivery_time_minutes: int = Field(..., description="Estimated delivery time in minutes")


class Inventory(BaseModel):
    """Inventory record for a product at a specific store."""
    inventory_id: str = Field(..., description="Unique inventory record ID")
    product_id: str = Field(..., description="Product ID")
    store: StoreLocation = Field(..., description="Store details")
    available_quantity: int = Field(..., ge=0, description="Available stock quantity")
    reserved_quantity: int = Field(0, ge=0, description="Reserved/in-cart quantity")
    is_available: bool = Field(..., description="Whether product is currently available")
    price_at_store: float = Field(..., gt=0, description="Price at this specific store")

    model_config = {
        "json_schema_extra": {
            "example": {
                "inventory_id": "INV-001",
                "product_id": "PROD-001",
                "store": {
                    "store_id": "STORE-BLR-001",
                    "store_name": "Blinkit Dark Store - Koramangala",
                    "latitude": 12.9352,
                    "longitude": 77.6245,
                    "address": "100 Feet Road, Koramangala, Bengaluru",
                    "distance_km": 1.2,
                    "delivery_time_minutes": 12
                },
                "available_quantity": 45,
                "reserved_quantity": 3,
                "is_available": True,
                "price_at_store": 68.0
            }
        }
    }


class NearbyInventoryResponse(BaseModel):
    """Response for nearby inventory check."""
    status: str = Field("success", description="Response status")
    product_id: str = Field(..., description="Product ID queried")
    user_latitude: float = Field(..., description="User's latitude")
    user_longitude: float = Field(..., description="User's longitude")
    radius_km: float = Field(..., description="Search radius in km")
    total_stores_found: int = Field(..., description="Total stores with inventory")
    inventory_list: List[Inventory] = Field(..., description="Sorted by distance")
