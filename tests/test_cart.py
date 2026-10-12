"""Tests for the Add to Cart API."""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestCartAPI:
    """Round 2 – Task 3: Add Product to Cart API Tests."""

    USER_ID = "TEST-USR-001"
    PRODUCT_ID = "PROD-001"
    STORE_ID = "STORE-BLR-001"

    def _clear_cart(self):
        """Helper to clean up cart before each test."""
        client.delete(f"/api/v1/cart/{self.USER_ID}")

    def test_add_to_cart_success(self):
        """
        POST /api/v1/cart/{user_id}/items → 201 Created.
        Round 2 Task 3: Add Product to Cart request/response.
        """
        self._clear_cart()
        payload = {
            "product_id": self.PRODUCT_ID,
            "store_id": self.STORE_ID,
            "quantity": 2,
        }
        response = client.post(f"/api/v1/cart/{self.USER_ID}/items", json=payload)
        assert response.status_code == 201

        data = response.json()
        assert data["status"] == "success"
        assert data["message"] == "Item added to cart successfully."

        cart = data["cart"]
        assert cart["user_id"] == self.USER_ID
        assert cart["item_count"] == 1
        assert cart["items"][0]["product_id"] == self.PRODUCT_ID
        assert cart["items"][0]["quantity"] == 2
        assert cart["items"][0]["unit_price"] == 68.0
        assert cart["items"][0]["total_price"] == 136.0

        # Verify totals are computed
        assert cart["subtotal"] == 136.0
        assert cart["total_amount"] > 0

    def test_add_to_cart_quantity_increments(self):
        """Adding same product twice should increment quantity."""
        self._clear_cart()
        payload = {"product_id": self.PRODUCT_ID, "store_id": self.STORE_ID, "quantity": 1}
        client.post(f"/api/v1/cart/{self.USER_ID}/items", json=payload)
        client.post(f"/api/v1/cart/{self.USER_ID}/items", json=payload)

        response = client.get(f"/api/v1/cart/{self.USER_ID}")
        assert response.status_code == 200
        cart = response.json()
        assert cart["items"][0]["quantity"] == 2

    def test_add_to_cart_invalid_product(self):
        """Adding non-existent product → 404 Not Found."""
        self._clear_cart()
        payload = {"product_id": "PROD-INVALID", "store_id": self.STORE_ID, "quantity": 1}
        response = client.post(f"/api/v1/cart/{self.USER_ID}/items", json=payload)
        assert response.status_code == 404

    def test_add_to_cart_invalid_store(self):
        """Product not at specified store → 404 Not Found."""
        self._clear_cart()
        payload = {"product_id": self.PRODUCT_ID, "store_id": "STORE-INVALID", "quantity": 1}
        response = client.post(f"/api/v1/cart/{self.USER_ID}/items", json=payload)
        assert response.status_code == 404

    def test_add_to_cart_zero_quantity_fails(self):
        """Quantity 0 should fail validation → 422 Unprocessable Entity."""
        self._clear_cart()
        payload = {"product_id": self.PRODUCT_ID, "store_id": self.STORE_ID, "quantity": 0}
        response = client.post(f"/api/v1/cart/{self.USER_ID}/items", json=payload)
        assert response.status_code == 422

    def test_get_cart_not_found(self):
        """GET cart for user with no cart → 404."""
        client.delete("/api/v1/cart/NO-CART-USER")
        response = client.get("/api/v1/cart/NO-CART-USER")
        assert response.status_code == 404

    def test_free_delivery_above_threshold(self):
        """Cart subtotal ≥ ₹199 should have ₹0 delivery fee."""
        # Use a separate user to avoid store conflict with previous tests
        free_delivery_user = "FREE-DELIVERY-TEST-USR"
        client.delete(f"/api/v1/cart/{free_delivery_user}")
        # Nescafe costs ₹225 > ₹199 threshold; available at STORE-BLR-002
        payload = {"product_id": "PROD-008", "store_id": "STORE-BLR-002", "quantity": 1}
        response = client.post(f"/api/v1/cart/{free_delivery_user}/items", json=payload)
        assert response.status_code == 201
        cart = response.json()["cart"]
        assert cart["delivery_fee"] == 0.0
