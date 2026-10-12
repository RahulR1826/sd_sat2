"""Orders Router – place and retrieve orders."""
from fastapi import APIRouter, Path

from app.models.order import PlaceOrderRequest, PlaceOrderResponse, Order
from app.services import order_service

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post(
    "/",
    response_model=PlaceOrderResponse,
    summary="Place Order",
    description=(
        "Convert the user's cart into a confirmed order. "
        "Validates cart, deducts inventory, assigns a delivery partner, and clears the cart."
    ),
    responses={
        200: {"description": "Order placed successfully"},
        400: {"description": "Empty cart or validation error"},
        404: {"description": "Cart not found"},
    },
)
def place_order(request: PlaceOrderRequest):
    """
    **POST /api/v1/orders/**

    HTTP Method: `POST`
    URI: `/api/v1/orders/`

    **Workflow triggered:**
    User → Search Product → Check Nearby Inventory → Add to Cart → **Place Order** → Assign Delivery Partner

    **Status Codes:**
    - `200 OK` – Order placed and delivery partner assigned
    - `400 Bad Request` – Cart is empty or validation failed
    - `404 Not Found` – Cart not found
    """
    return order_service.place_order(request)


@router.get(
    "/{order_id}",
    response_model=Order,
    summary="Get Order Details",
    description="Retrieve full details of a specific order by its ID.",
    responses={
        200: {"description": "Order found"},
        404: {"description": "Order not found"},
    },
)
def get_order(order_id: str = Path(..., description="Order ID")):
    """
    **GET /api/v1/orders/{order_id}**

    HTTP Method: `GET`
    URI: `/api/v1/orders/{order_id}`

    **Status Codes:**
    - `200 OK` – Order found
    - `404 Not Found` – Order does not exist
    """
    return order_service.get_order(order_id)
