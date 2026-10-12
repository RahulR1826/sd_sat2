"""Cart Service – add/remove items, compute totals."""
import uuid
from datetime import datetime
from typing import Optional
from fastapi import HTTPException, status

from app.models.cart import Cart, CartItem, AddToCartRequest, AddToCartResponse
from app.models.product import Product
from app.database.in_memory_db import carts_db, products_db, inventory_db, stores_db


DELIVERY_FEE = 20.0
TAX_RATE = 0.045          # 4.5 % GST on grocery
FREE_DELIVERY_THRESHOLD = 199.0


def _compute_totals(cart: Cart) -> Cart:
    """Recalculate cart subtotal, delivery fee, taxes, and grand total."""
    subtotal = sum(item.total_price for item in cart.items)
    delivery_fee = 0.0 if subtotal >= FREE_DELIVERY_THRESHOLD else DELIVERY_FEE
    taxes = round(subtotal * TAX_RATE, 2)
    total = round(subtotal + delivery_fee + taxes, 2)
    return cart.model_copy(update={
        "subtotal": round(subtotal, 2),
        "delivery_fee": delivery_fee,
        "taxes": taxes,
        "total_amount": total,
        "item_count": len(cart.items),
        "updated_at": datetime.utcnow(),
    })


def get_or_create_cart(user_id: str, store_id: str) -> Cart:
    """Retrieve existing cart or create a new empty one."""
    if user_id not in carts_db:
        carts_db[user_id] = Cart(
            cart_id=f"CART-{user_id}-{uuid.uuid4().hex[:6].upper()}",
            user_id=user_id,
            store_id=store_id,
            items=[],
        )
    return carts_db[user_id]


def add_item_to_cart(user_id: str, request: AddToCartRequest) -> AddToCartResponse:
    """
    Add a product to the user's cart.
    Validates product existence, store inventory, and quantity limits.
    """
    # 1. Validate product
    product: Optional[Product] = products_db.get(request.product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product '{request.product_id}' not found.",
        )
    if not product.in_stock:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Product '{product.name}' is currently out of stock.",
        )

    # 2. Validate store inventory
    store_inventories = inventory_db.get(request.product_id, [])
    inv_record = next(
        (inv for inv in store_inventories if inv.store.store_id == request.store_id), None
    )
    if not inv_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product not available at store '{request.store_id}'.",
        )
    if not inv_record.is_available or inv_record.available_quantity < request.quantity:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Insufficient stock. Available: {inv_record.available_quantity}, "
                f"Requested: {request.quantity}."
            ),
        )

    # 3. Get or create cart
    cart = get_or_create_cart(user_id, request.store_id)

    # 4. Check store consistency (all cart items must be from same store)
    if cart.items and cart.store_id != request.store_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Cannot mix items from different stores. "
                f"Your cart is from store '{cart.store_id}'."
            ),
        )

    # 5. Update existing item or add new
    existing = next((i for i in cart.items if i.product_id == request.product_id), None)
    if existing:
        new_qty = existing.quantity + request.quantity
        updated_item = existing.model_copy(update={
            "quantity": new_qty,
            "total_price": round(new_qty * inv_record.price_at_store, 2),
        })
        cart.items[cart.items.index(existing)] = updated_item
    else:
        new_item = CartItem(
            cart_item_id=f"CI-{uuid.uuid4().hex[:8].upper()}",
            product_id=product.id,
            product_name=product.name,
            store_id=request.store_id,
            quantity=request.quantity,
            unit_price=inv_record.price_at_store,
            total_price=round(request.quantity * inv_record.price_at_store, 2),
            image_url=product.image_url,
        )
        cart.items.append(new_item)

    # 6. Recompute totals and persist
    cart = _compute_totals(cart)
    carts_db[user_id] = cart

    return AddToCartResponse(
        message="Item added to cart successfully.",
        cart=cart,
    )


def get_cart(user_id: str) -> Optional[Cart]:
    return carts_db.get(user_id)


def clear_cart(user_id: str) -> None:
    if user_id in carts_db:
        del carts_db[user_id]
