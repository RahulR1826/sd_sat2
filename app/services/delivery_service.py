"""Delivery Service – tracks the delivery status of an order."""
from fastapi import HTTPException, status
from app.models.delivery import Delivery, DeliveryStatusResponse
from app.database.in_memory_db import deliveries_db


def get_delivery_status(order_id: str) -> DeliveryStatusResponse:
    """
    Fetch real-time delivery status for a given order ID.
    In production, this would query a location-tracking service (e.g., Redis Streams).
    """
    delivery: Delivery | None = deliveries_db.get(order_id)
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No delivery record found for order '{order_id}'.",
        )
    return DeliveryStatusResponse(order_id=order_id, delivery=delivery)
