"""Tests for the Product Search API."""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestProductSearch:
    """Round 2 – Task 1 & 2: Search Product API Tests."""

    def test_search_products_success(self):
        """GET /api/v1/products/search?q=milk → 200 OK with results."""
        response = client.get("/api/v1/products/search?q=milk")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["total_results"] >= 1
        assert any("milk" in p["name"].lower() or "milk" in p["description"].lower()
                   for p in data["products"])

    def test_search_products_by_brand(self):
        """Search by brand name 'amul' should return dairy products."""
        response = client.get("/api/v1/products/search?q=amul")
        assert response.status_code == 200
        data = response.json()
        assert data["total_results"] >= 1
        assert data["products"][0]["brand"] == "Amul"

    def test_search_with_category_filter(self):
        """Filter by category=snacks should return only snack products."""
        response = client.get("/api/v1/products/search?q=chips&category=snacks")
        assert response.status_code == 200
        data = response.json()
        for product in data["products"]:
            assert product["category"] == "snacks"

    def test_search_no_results(self):
        """Search for non-existent product returns empty list."""
        response = client.get("/api/v1/products/search?q=nonexistentproduct12345")
        assert response.status_code == 200
        assert response.json()["total_results"] == 0

    def test_search_empty_query_fails(self):
        """Empty query string should return 422 validation error."""
        response = client.get("/api/v1/products/search?q=")
        assert response.status_code == 422

    def test_search_invalid_price_range(self):
        """min_price > max_price should return 400."""
        response = client.get("/api/v1/products/search?q=milk&min_price=200&max_price=50")
        assert response.status_code == 400

    def test_get_product_by_id_success(self):
        """GET /api/v1/products/PROD-001 → 200 OK."""
        response = client.get("/api/v1/products/PROD-001")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "PROD-001"
        assert data["name"] == "Amul Full Cream Milk"

    def test_get_product_by_id_not_found(self):
        """GET /api/v1/products/INVALID → 404 Not Found."""
        response = client.get("/api/v1/products/INVALID-999")
        assert response.status_code == 404

    def test_list_all_products(self):
        """GET /api/v1/products/ → 200 OK with all products."""
        response = client.get("/api/v1/products/")
        assert response.status_code == 200
        data = response.json()
        assert data["total_results"] >= 8  # We have 8 seed products

    def test_pagination(self):
        """Page 1 and Page 2 should return different items."""
        r1 = client.get("/api/v1/products/?page=1&page_size=3")
        r2 = client.get("/api/v1/products/?page=2&page_size=3")
        assert r1.status_code == 200
        assert r2.status_code == 200
        ids_p1 = [p["id"] for p in r1.json()["products"]]
        ids_p2 = [p["id"] for p in r2.json()["products"]]
        assert set(ids_p1).isdisjoint(set(ids_p2))
