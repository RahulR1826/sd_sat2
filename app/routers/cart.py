"""Cart Router – manage user shopping cart."""
from fastapi import APIRouter, Path, HTTPException, status

from app.models.cart import AddToCartRequest, AddToCartResponse, Cart
from app.services import cart_service

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.post(
    "/{user_id}/items",
    response_model=AddToCartResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add Product to Cart",
    description=(
        "Add a product from a specific store to the user's shopping cart. "
        "If the item already exists, its quantity is incremented. "
        "All items in a cart must belong to the same store."
    ),
    responses={
        201: {"description": "Item added to cart successfully"},
        400: {"description": "Validation error (e.g., mixing stores)"},
        404: {"description": "Product or store not found"},
        409: {"description": "Insufficient stock or product out of stock"},
    },
)
def add_to_cart(
    user_id: str = Path(..., description="User ID"),
    request: AddToCartRequest = ...,
):
    """
    **POST /api/v1/cart/{user_id}/items**

    HTTP Method: `POST`
    URI: `/api/v1/cart/{user_id}/items`

    **Request Body:**
    ```json
    {
      "product_id": "PROD-001",
      "store_id": "STORE-BLR-001",
      "quantity": 2
    }
    ```

    **Success Response (201):**
    Returns the updated cart with totals recalculated.

    **Error Status Codes:**
    - `400 Bad Request` – Items from different stores
    - `404 Not Found` – Product/store not found
    - `409 Conflict` – Product out of stock or insufficient quantity
    """
    return cart_service.add_item_to_cart(user_id, request)


@router.get(
    "/{user_id}",
    response_model=Cart,
    summary="Get User Cart",
    description="Retrieve the current cart contents for a user.",
    responses={
        200: {"description": "Cart retrieved"},
        404: {"description": "Cart not found"},
    },
)
def get_cart(user_id: str = Path(..., description="User ID")):
    """
    **GET /api/v1/cart/{user_id}**

    HTTP Method: `GET`
    URI: `/api/v1/cart/{user_id}`

    **Status Codes:**
    - `200 OK` – Cart found
    - `404 Not Found` – No active cart for this user
    """
    cart = cart_service.get_cart(user_id)
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active cart found for user '{user_id}'.",
        )
    return cart


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Clear Cart",
    description="Remove all items from the user's cart.",
)
def clear_cart(user_id: str = Path(..., description="User ID")):
    """
    **DELETE /api/v1/cart/{user_id}**

    HTTP Method: `DELETE`
    URI: `/api/v1/cart/{user_id}`

    **Status Codes:**
    - `204 No Content` – Cart cleared
    """
    cart_service.clear_cart(user_id)
