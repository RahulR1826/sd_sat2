"""Inventory Service – checks nearby store stock for a given product."""
import math
from typing import Optional
from app.models.inventory import Inventory, NearbyInventoryResponse
from app.database.in_memory_db import inventory_db


def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on Earth (km).
    Uses the Haversine formula.
    """
    R = 6371.0  # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def check_nearby_inventory(
    product_id: str,
    user_lat: float,
    user_lng: float,
    radius_km: float = 5.0,
) -> NearbyInventoryResponse:
    """
    Return all stores within `radius_km` that have the product available,
    sorted by distance (nearest first).
    """
    raw_inventory: list[Inventory] = inventory_db.get(product_id, [])

    nearby: list[Inventory] = []
    for inv in raw_inventory:
        dist = _haversine_distance(
            user_lat, user_lng,
            inv.store.latitude, inv.store.longitude,
        )
        if dist <= radius_km and inv.is_available and inv.available_quantity > 0:
            # Patch distance dynamically
            updated_store = inv.store.model_copy(update={
                "distance_km": round(dist, 2),
                "delivery_time_minutes": max(10, int(dist * 6)),  # ~6 min/km
            })
            nearby.append(inv.model_copy(update={"store": updated_store}))

    nearby.sort(key=lambda i: i.store.distance_km)

    return NearbyInventoryResponse(
        product_id=product_id,
        user_latitude=user_lat,
        user_longitude=user_lng,
        radius_km=radius_km,
        total_stores_found=len(nearby),
        inventory_list=nearby,
    )
