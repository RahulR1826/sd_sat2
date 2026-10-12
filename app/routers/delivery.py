"""Delivery Router – track delivery status of an order."""
from fastapi import APIRouter, Path

from app.models.delivery import DeliveryStatusResponse
from app.services import delivery_service

router = APIRouter(prefix="/delivery", tags=["Delivery"])


@router.get(
    "/{order_id}/status",
    response_model=DeliveryStatusResponse,
    summary="Get Delivery Status",
    description=(
        "Track the real-time delivery status of an order. "
        "Returns delivery partner info, current location, ETA, and event timeline."
    ),
    responses={
        200: {"description": "Delivery status retrieved"},
        404: {"description": "Order or delivery record not found"},
    },
)
def get_delivery_status(order_id: str = Path(..., description="Order ID to track")):
    """
    **GET /api/v1/delivery/{order_id}/status**

    HTTP Method: `GET`
    URI: `/api/v1/delivery/{order_id}/status`

    **Additional API (Round 2 – Task 6)**

    Returns:
    - Delivery partner details (name, phone, vehicle, rating)
    - Partner's real-time GPS coordinates
    - Current delivery status from the `DeliveryStatus` enum
    - Estimated arrival time
    - Full event tracking timeline

    **Status Codes:**
    - `200 OK` – Delivery status found
    - `404 Not Found` – No delivery record for this order
    """
    return delivery_service.get_delivery_status(order_id)
