# 🛒 Food & Grocery Quick-Commerce Platform

> **System Design Assignment** – Round 2 (LLD) + Round 3 (HLD)  
> Built with **Python + FastAPI** | Auto-generated Swagger UI | In-memory data store

---

## 📋 Table of Contents
- [Overview](#overview)
- [Project Structure](#project-structure)
- [REST API Reference](#rest-api-reference)
- [Quick Start](#quick-start)
- [Running Tests](#running-tests)
- [Documentation](#documentation)
- [Tech Stack](#tech-stack)

---

## Overview

A complete **Low-Level Design (LLD)** implementation of a quick-commerce backend that supports:

- 🔍 **Product Search** – Full-text search with category & price filters
- 📍 **Nearby Inventory Check** – Haversine geo-distance calculation to nearest stores
- 🛒 **Cart Management** – Add/remove items, auto-compute totals & delivery fees
- 📦 **Order Placement** – Convert cart to order, deduct inventory, assign delivery partner
- 🚴 **Delivery Tracking** – Real-time delivery status with partner info & event timeline

---

## Project Structure

```
sd-sat2/
├── main.py                         # FastAPI application entry point
├── requirements.txt                # Python dependencies
│
├── app/
│   ├── models/                     # Pydantic data models
│   │   ├── product.py              # Product, ProductSearchResponse
│   │   ├── inventory.py            # Inventory, NearbyInventoryResponse
│   │   ├── cart.py                 # Cart, CartItem, AddToCartRequest/Response
│   │   ├── order.py                # Order, PlaceOrderRequest/Response, OrderStatus
│   │   └── delivery.py             # Delivery, DeliveryStatus, DeliveryStatusResponse
│   │
│   ├── routers/                    # FastAPI route handlers
│   │   ├── products.py             # GET /products/search, GET /products/{id}
│   │   ├── inventory.py            # GET /inventory/nearby
│   │   ├── cart.py                 # POST /cart/{user_id}/items
│   │   ├── orders.py               # POST /orders/
│   │   └── delivery.py             # GET /delivery/{order_id}/status
│   │
│   ├── services/                   # Business logic layer
│   │   ├── product_service.py      # Search, filter, paginate
│   │   ├── inventory_service.py    # Haversine geo-search
│   │   ├── cart_service.py         # Cart CRUD, totals computation
│   │   ├── order_service.py        # Order creation, inventory deduction
│   │   └── delivery_service.py     # Delivery status retrieval
│   │
│   └── database/
│       └── in_memory_db.py         # Seed data (replaces DB for demo)
│
├── docs/
│   ├── LLD.md                      # Round 2 – Full LLD documentation
│   └── HLD.md                      # Round 3 – Full HLD documentation
│
└── tests/
    ├── test_products.py            # Product search & get tests
    ├── test_cart.py                # Add to cart tests
    └── test_orders.py              # Place order & delivery status tests
```

---

## REST API Reference

### Round 2 – LLD APIs

| # | Feature                | Method   | URI                                       |
|---|------------------------|----------|-------------------------------------------|
| 1 | Search Product         | `GET`    | `/api/v1/products/search?q={query}`       |
| 2 | Check Nearby Inventory | `GET`    | `/api/v1/inventory/nearby?product_id=&lat=&lng=` |
| 3 | Add Product to Cart    | `POST`   | `/api/v1/cart/{user_id}/items`            |
| 4 | Place Order            | `POST`   | `/api/v1/orders/`                         |
| 5 | Get Delivery Status 🆕 | `GET`    | `/api/v1/delivery/{order_id}/status`      |

### HTTP Status Codes

| Code  | Meaning                                    |
|-------|--------------------------------------------|
| `200` | OK – Successful GET                        |
| `201` | Created – Item added to cart               |
| `204` | No Content – Cart cleared                  |
| `400` | Bad Request – Validation / logic error     |
| `404` | Not Found – Resource does not exist        |
| `409` | Conflict – Out of stock / insufficient qty |
| `422` | Unprocessable – Schema validation failed   |
| `500` | Internal Server Error                      |

---

## Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/sd-sat2.git
cd sd-sat2
```

### 2. Create and activate virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the server
```bash
uvicorn main:app --reload
```

The API will be available at **http://127.0.0.1:8000**

### 5. Explore the API (Swagger UI)
Open → **http://127.0.0.1:8000/docs**

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

Expected output:
```
tests/test_products.py::TestProductSearch::test_search_products_success       PASSED
tests/test_products.py::TestProductSearch::test_search_by_brand               PASSED
tests/test_products.py::TestProductSearch::test_search_with_category_filter   PASSED
...
tests/test_cart.py::TestCartAPI::test_add_to_cart_success                     PASSED
tests/test_cart.py::TestCartAPI::test_add_to_cart_invalid_product             PASSED
...
tests/test_orders.py::TestOrdersAPI::test_place_order_success                 PASSED
tests/test_orders.py::TestOrdersAPI::test_get_delivery_status_after_order     PASSED
...
15 passed in X.XXs
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [📄 LLD.md](docs/LLD.md) | Full Low-Level Design – APIs, request/response, sequence diagram, status codes |
| [📐 HLD.md](docs/HLD.md) | Full High-Level Design – Architecture, databases, caching, Kafka, scalability |

---

## User Flow (Sequence)

```
User
 │
 ├─1─ Search Product       → GET /api/v1/products/search?q=milk
 │
 ├─2─ Check Nearby Stock   → GET /api/v1/inventory/nearby?product_id=PROD-001&lat=12.93&lng=77.62
 │
 ├─3─ Add to Cart          → POST /api/v1/cart/USR-001/items
 │         { "product_id": "PROD-001", "store_id": "STORE-BLR-001", "quantity": 2 }
 │
 ├─4─ Place Order          → POST /api/v1/orders/
 │         { "cart_id": "...", "delivery_address": {...}, "payment_method": "UPI" }
 │
 └─5─ Track Delivery       → GET /api/v1/delivery/ORD-20241012-XXXXX/status
```

---

## Tech Stack

### Implementation (LLD Demo)
| Layer     | Technology                          |
|-----------|-------------------------------------|
| API       | FastAPI (Python 3.11)               |
| Validation| Pydantic v2                         |
| Server    | Uvicorn (ASGI)                      |
| Testing   | Pytest + FastAPI TestClient         |
| Data      | In-memory dict (seed data)          |

### Production Stack (HLD)
| Layer        | Technology                                   |
|--------------|----------------------------------------------|
| API Gateway  | Kong / AWS API Gateway                       |
| Services     | FastAPI microservices (Kubernetes)            |
| Product DB   | MongoDB (Atlas)                              |
| User/Order   | PostgreSQL (RDS Multi-AZ)                   |
| Inventory    | Apache Cassandra                            |
| Cart/Cache   | Redis Cluster                               |
| Search       | Elasticsearch                               |
| Messaging    | Apache Kafka                                |
| Real-time    | WebSockets + Redis Pub/Sub                  |
| Notifications| Firebase FCM + Twilio SMS                  |
| CDN          | AWS CloudFront                              |
| Containers   | Docker + Kubernetes (EKS)                   |

---

## 📝 License
MIT License – Free to use for educational purposes.
