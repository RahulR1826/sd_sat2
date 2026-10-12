"""
Food & Grocery Quick-Commerce Platform
======================================
FastAPI application entry point.

Round 2 – Low-Level Design (LLD):
  REST APIs for Search Product, Check Nearby Inventory,
  Add Product to Cart, Place Order, and Get Delivery Status.

Round 3 – High-Level Design (HLD):
  See docs/HLD.md for system architecture documentation.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routers import products, inventory, cart, orders, delivery

# ──────────────────────────────────────────────
#  Application Setup
# ──────────────────────────────────────────────
app = FastAPI(
    title="🛒 Food & Grocery Quick-Commerce Platform",
    description="""
## Food & Grocery Quick-Commerce Platform API

A **Low-Level Design (LLD)** implementation of a quick-commerce backend
serving millions of customers with 10-30 minute deliveries.

### Round 2 – REST API Design

| # | API                     | Method | URI                                 |
|---|-------------------------|--------|-------------------------------------|
| 1 | Search Product          | GET    | `/api/v1/products/search?q=`        |
| 2 | Check Nearby Inventory  | GET    | `/api/v1/inventory/nearby`          |
| 3 | Add Product to Cart     | POST   | `/api/v1/cart/{user_id}/items`      |
| 4 | Place Order             | POST   | `/api/v1/orders/`                   |
| 5 | Get Delivery Status     | GET    | `/api/v1/delivery/{order_id}/status`|

### User Flow (Sequence)
```
User → Search Product → Check Nearby Inventory → Add to Cart
     → Place Order → Assign Delivery Partner → Track Delivery
```

### HTTP Status Codes
- `200 OK` – Request successful
- `201 Created` – Resource created (add to cart)
- `204 No Content` – Delete successful
- `400 Bad Request` – Invalid input
- `404 Not Found` – Resource not found
- `409 Conflict` – Conflict (out of stock / insufficient quantity)
- `500 Internal Server Error` – Unexpected server error

### Technology Stack (Production)
- **API Layer**: FastAPI (Python)
- **Product DB**: MongoDB
- **User/Order DB**: PostgreSQL
- **Cart/Session**: Redis
- **Inventory**: Cassandra
- **Cache**: Redis
- **Messaging**: Apache Kafka
- **Search**: Elasticsearch
    """,
    version="1.0.0",
    contact={
        "name": "Quick-Commerce Engineering",
        "email": "engineering@quickcommerce.example.com",
    },
    license_info={"name": "MIT"},
    docs_url="/docs",
    redoc_url="/redoc",
)

# ──────────────────────────────────────────────
#  CORS Middleware
# ──────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────
#  Routers
# ──────────────────────────────────────────────
API_PREFIX = "/api/v1"

app.include_router(products.router, prefix=API_PREFIX)
app.include_router(inventory.router, prefix=API_PREFIX)
app.include_router(cart.router, prefix=API_PREFIX)
app.include_router(orders.router, prefix=API_PREFIX)
app.include_router(delivery.router, prefix=API_PREFIX)


# ──────────────────────────────────────────────
#  Root & Health Endpoints
# ──────────────────────────────────────────────
@app.get("/", tags=["Health"], summary="Root")
def root():
    """Welcome endpoint."""
    return {
        "service": "Food & Grocery Quick-Commerce Platform",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["Health"], summary="Health Check")
def health_check():
    """Health check endpoint for load balancer / container orchestration."""
    return JSONResponse(
        status_code=200,
        content={"status": "healthy", "service": "quick-commerce-api"},
    )


# ──────────────────────────────────────────────
#  Run with: uvicorn main:app --reload
# ──────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
