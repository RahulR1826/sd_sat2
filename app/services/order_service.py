"""Order Service – places an order and triggers delivery assignment."""
import uuid
import random
from datetime import datetime, timedelta
from fastapi import HTTPException, status

from app.models.order import Order, PlaceOrderRequest, PlaceOrderResponse, OrderStatus
from app.models.delivery import Delivery, DeliveryStatus, DeliveryPartner, TrackingEvent
from app.database.in_memory_db import (
    carts_db, orders_db, deliveries_db, inventory_db, delivery_partners_pool
)
from app.services.cart_service import clear_cart


def place_order(request: PlaceOrderRequest) -> PlaceOrderResponse:
    """
    Converts a cart into a confirmed order and assigns a delivery partner.
    Steps:
      1. Validate cart exists and belongs to the user
      2. Create order record
      3. Deduct inventory
      4. Assign delivery partner
      5. Clear cart
    """
    # 1. Validate cart
    cart = carts_db.get(request.user_id)
    if not cart or cart.cart_id != request.cart_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cart '{request.cart_id}' not found for user '{request.user_id}'.",
        )
    if not cart.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot place an order with an empty cart.",
        )

    now = datetime.utcnow()
    order_id = f"ORD-{now.strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    # 2. Create order
    order = Order(
        order_id=order_id,
        user_id=request.user_id,
        cart_id=request.cart_id,
        store_id=cart.store_id,
        items=cart.items,
        delivery_address=request.delivery_address,
        payment_method=request.payment_method,
        payment_transaction_id=request.payment_transaction_id,
        subtotal=cart.subtotal,
        delivery_fee=cart.delivery_fee,
        taxes=cart.taxes,
        total_amount=cart.total_amount,
        status=OrderStatus.CONFIRMED,
        special_instructions=request.special_instructions,
        estimated_delivery_time=15,
        created_at=now,
        updated_at=now,
    )

    # 3. Deduct inventory (optimistic – in production, use DB transactions)
    for item in cart.items:
        store_inventories = inventory_db.get(item.product_id, [])
        for inv in store_inventories:
            if inv.store.store_id == cart.store_id:
                inv.available_quantity = max(0, inv.available_quantity - item.quantity)
                inv.is_available = inv.available_quantity > 0

    # 4. Assign delivery partner (random pick from pool)
    partner_data = random.choice(delivery_partners_pool)
    partner = DeliveryPartner(**partner_data)
    order.delivery_partner_id = partner.partner_id
    orders_db[order_id] = order

    # 5. Create delivery record
    eta = now + timedelta(minutes=order.estimated_delivery_time)
    delivery = Delivery(
        delivery_id=f"DEL-{uuid.uuid4().hex[:8].upper()}",
        order_id=order_id,
        partner=partner,
        status=DeliveryStatus.PARTNER_ASSIGNED,
        estimated_delivery_time=order.estimated_delivery_time,
        estimated_arrival_at=eta,
        distance_remaining_km=1.5,
        tracking_events=[
            TrackingEvent(event="Order placed and confirmed", timestamp=now),
            TrackingEvent(event=f"Delivery partner {partner.name} assigned", timestamp=now),
        ],
        assigned_at=now,
    )
    deliveries_db[order_id] = delivery

    # 6. Clear cart
    clear_cart(request.user_id)

    return PlaceOrderResponse(
        message=f"Order placed successfully! Estimated delivery in {order.estimated_delivery_time} minutes.",
        order=order,
    )


def get_order(order_id: str) -> Order:
    order = orders_db.get(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order '{order_id}' not found.",
        )
    return order
