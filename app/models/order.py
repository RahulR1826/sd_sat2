from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
from app.models.cart import CartItem


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    PREPARING = "PREPARING"
    READY_FOR_PICKUP = "READY_FOR_PICKUP"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"


class PaymentMethod(str, Enum):
    UPI = "UPI"
    CARD = "CARD"
    NET_BANKING = "NET_BANKING"
    WALLET = "WALLET"
    CASH_ON_DELIVERY = "CASH_ON_DELIVERY"


class DeliveryAddress(BaseModel):
    """Delivery address for an order."""
    full_name: str = Field(..., description="Recipient full name")
    phone: str = Field(..., description="Contact phone number")
    address_line1: str = Field(..., description="Address line 1")
    address_line2: Optional[str] = Field(None, description="Address line 2")
    city: str = Field(..., description="City")
    state: str = Field(..., description="State")
    pincode: str = Field(..., description="PIN code")
    latitude: float = Field(..., description="Delivery latitude")
    longitude: float = Field(..., description="Delivery longitude")


class PlaceOrderRequest(BaseModel):
    """Request body for POST /api/v1/orders"""
    cart_id: str = Field(..., description="Cart ID to convert to order")
    user_id: str = Field(..., description="User placing the order")
    delivery_address: DeliveryAddress = Field(..., description="Delivery address details")
    payment_method: PaymentMethod = Field(..., description="Payment method")
    payment_transaction_id: Optional[str] = Field(None, description="Payment transaction ID")
    special_instructions: Optional[str] = Field(None, description="Delivery instructions")

    model_config = {
        "json_schema_extra": {
            "example": {
                "cart_id": "CART-USR001-001",
                "user_id": "USR-001",
                "delivery_address": {
                    "full_name": "Rahul Sharma",
                    "phone": "9876543210",
                    "address_line1": "Flat 4B, Green Park Apartments",
                    "address_line2": "80 Feet Road",
                    "city": "Bengaluru",
                    "state": "Karnataka",
                    "pincode": "560034",
                    "latitude": 12.9280,
                    "longitude": 77.6271
                },
                "payment_method": "UPI",
                "payment_transaction_id": "TXN-20241012-00123",
                "special_instructions": "Leave at the door"
            }
        }
    }


class Order(BaseModel):
    """Represents a placed order."""
    order_id: str = Field(..., description="Unique order ID")
    user_id: str = Field(..., description="User ID")
    cart_id: str = Field(..., description="Source cart ID")
    store_id: str = Field(..., description="Fulfilling store ID")
    items: List[CartItem] = Field(..., description="Ordered items")
    delivery_address: DeliveryAddress = Field(..., description="Delivery address")
    payment_method: PaymentMethod = Field(..., description="Payment method")
    payment_transaction_id: Optional[str] = Field(None)
    subtotal: float = Field(..., description="Subtotal amount")
    delivery_fee: float = Field(..., description="Delivery fee")
    taxes: float = Field(..., description="Tax amount")
    total_amount: float = Field(..., description="Total amount paid")
    status: OrderStatus = Field(OrderStatus.PENDING, description="Current order status")
    delivery_partner_id: Optional[str] = Field(None, description="Assigned delivery partner")
    estimated_delivery_time: Optional[int] = Field(None, description="ETA in minutes")
    special_instructions: Optional[str] = Field(None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PlaceOrderResponse(BaseModel):
    """Response for POST /api/v1/orders"""
    status: str = Field("success", description="Response status")
    message: str = Field(..., description="Status message")
    order: Order = Field(..., description="Created order details")
