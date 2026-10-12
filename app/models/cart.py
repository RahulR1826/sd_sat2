from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class CartItem(BaseModel):
    """A single item in the shopping cart."""
    cart_item_id: str = Field(..., description="Unique cart item ID")
    product_id: str = Field(..., description="Product ID")
    product_name: str = Field(..., description="Product name")
    store_id: str = Field(..., description="Store from which item is sourced")
    quantity: int = Field(..., ge=1, description="Quantity of the product")
    unit_price: float = Field(..., gt=0, description="Price per unit in INR")
    total_price: float = Field(..., gt=0, description="Total price for this item")
    image_url: Optional[str] = Field(None, description="Product image URL")


class Cart(BaseModel):
    """Shopping cart for a user."""
    cart_id: str = Field(..., description="Unique cart ID")
    user_id: str = Field(..., description="User who owns this cart")
    store_id: str = Field(..., description="Store all items are from")
    items: List[CartItem] = Field(default=[], description="Items in the cart")
    subtotal: float = Field(0.0, description="Subtotal before fees")
    delivery_fee: float = Field(0.0, description="Delivery charge")
    taxes: float = Field(0.0, description="GST and applicable taxes")
    total_amount: float = Field(0.0, description="Grand total payable")
    item_count: int = Field(0, description="Total number of items")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AddToCartRequest(BaseModel):
    """
    Request body for POST /api/v1/cart/{user_id}/items
    Adds a product to the user's shopping cart.
    """
    product_id: str = Field(..., description="ID of the product to add")
    store_id: str = Field(..., description="Store ID from which to source the product")
    quantity: int = Field(..., ge=1, le=50, description="Quantity to add (1-50)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "product_id": "PROD-001",
                "store_id": "STORE-BLR-001",
                "quantity": 2
            }
        }
    }


class AddToCartResponse(BaseModel):
    """
    Response for POST /api/v1/cart/{user_id}/items
    Returns updated cart details after adding the item.
    """
    status: str = Field("success", description="Response status")
    message: str = Field(..., description="Human-readable status message")
    cart: Cart = Field(..., description="Updated cart state")

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "success",
                "message": "Item added to cart successfully",
                "cart": {
                    "cart_id": "CART-USR001-001",
                    "user_id": "USR-001",
                    "store_id": "STORE-BLR-001",
                    "items": [
                        {
                            "cart_item_id": "CI-001",
                            "product_id": "PROD-001",
                            "product_name": "Amul Full Cream Milk",
                            "store_id": "STORE-BLR-001",
                            "quantity": 2,
                            "unit_price": 68.0,
                            "total_price": 136.0,
                            "image_url": "https://cdn.example.com/amul-milk.jpg"
                        }
                    ],
                    "subtotal": 136.0,
                    "delivery_fee": 20.0,
                    "taxes": 6.12,
                    "total_amount": 162.12,
                    "item_count": 1
                }
            }
        }
    }
