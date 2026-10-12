"""Tests for Place Order and Get Delivery Status APIs."""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

DELIVERY_ADDRESS = {
    "full_name": "Rahul Sharma",
    "phone": "9876543210",
    "address_line1": "Flat 4B, Green Park Apartments",
    "address_line2": "80 Feet Road",
    "city": "Bengaluru",
    "state": "Karnataka",
    "pincode": "560034",
    "latitude": 12.9280,
    "longitude": 77.6271,
}


class TestOrdersAPI:
    """Round 2 – Task 4 & 5: Place Order and Delivery Status Tests."""

    USER_ID = "ORDER-TEST-USR"

    def _setup_cart(self, user_id: str = None) -> dict:
        """Add an item to cart and return cart data."""
        uid = user_id or self.USER_ID
        client.delete(f"/api/v1/cart/{uid}")
        payload = {"product_id": "PROD-003", "store_id": "STORE-BLR-001", "quantity": 1}
        r = client.post(f"/api/v1/cart/{uid}/items", json=payload)
        assert r.status_code == 201
        return r.json()["cart"]

    def test_place_order_success(self):
        """
        POST /api/v1/orders/ → 200 OK.
        Full sequence: Cart → Place Order → Assign Partner.
        """
        cart = self._setup_cart()

        order_payload = {
            "cart_id": cart["cart_id"],
            "user_id": self.USER_ID,
            "delivery_address": DELIVERY_ADDRESS,
            "payment_method": "UPI",
            "payment_transaction_id": "TXN-TEST-001",
            "special_instructions": "Ring the bell",
        }
        response = client.post("/api/v1/orders/", json=order_payload)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "success"

        order = data["order"]
        assert order["user_id"] == self.USER_ID
        assert order["status"] == "CONFIRMED"
        assert order["delivery_partner_id"] is not None   # Partner assigned
        assert order["estimated_delivery_time"] == 15
        assert order["total_amount"] > 0

    def test_place_order_cart_not_found(self):
        """Place order with invalid cart ID → 404."""
        order_payload = {
            "cart_id": "CART-DOES-NOT-EXIST",
            "user_id": self.USER_ID,
            "delivery_address": DELIVERY_ADDRESS,
            "payment_method": "CARD",
        }
        response = client.post("/api/v1/orders/", json=order_payload)
        assert response.status_code == 404

    def test_get_delivery_status_after_order(self):
        """
        GET /api/v1/delivery/{order_id}/status → 200 OK.
        Round 2 – Task 6: Additional API for Get Delivery Status.
        """
        cart = self._setup_cart(user_id="DELIVERY-TEST-USR")

        order_payload = {
            "cart_id": cart["cart_id"],
            "user_id": "DELIVERY-TEST-USR",
            "delivery_address": DELIVERY_ADDRESS,
            "payment_method": "CASH_ON_DELIVERY",
        }
        order_response = client.post("/api/v1/orders/", json=order_payload)
        assert order_response.status_code == 200
        order_id = order_response.json()["order"]["order_id"]

        # Now check delivery status
        delivery_response = client.get(f"/api/v1/delivery/{order_id}/status")
        assert delivery_response.status_code == 200

        delivery_data = delivery_response.json()
        assert delivery_data["status"] == "success"
        assert delivery_data["order_id"] == order_id

        delivery = delivery_data["delivery"]
        assert delivery["status"] == "PARTNER_ASSIGNED"
        assert delivery["partner"] is not None
        assert delivery["estimated_delivery_time"] == 15
        assert len(delivery["tracking_events"]) >= 2

    def test_get_delivery_status_not_found(self):
        """GET delivery for unknown order → 404."""
        response = client.get("/api/v1/delivery/ORD-INVALID-999/status")
        assert response.status_code == 404

    def test_cart_cleared_after_order(self):
        """Cart should be deleted after a successful order."""
        uid = "CART-CLEAR-TEST-USR"
        cart = self._setup_cart(user_id=uid)

        order_payload = {
            "cart_id": cart["cart_id"],
            "user_id": uid,
            "delivery_address": DELIVERY_ADDRESS,
            "payment_method": "WALLET",
        }
        client.post("/api/v1/orders/", json=order_payload)

        # Cart should now be gone
        get_cart = client.get(f"/api/v1/cart/{uid}")
        assert get_cart.status_code == 404
