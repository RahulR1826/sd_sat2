# Low-Level Design (LLD) – Food & Grocery Quick-Commerce Platform

## Round 2 – Low-Level Design Challenge (30 Marks)

---

## Task 1 & 2 – REST API Design with HTTP Methods & URIs

| # | Feature                | Method   | URI                                      | Description                              |
|---|------------------------|----------|------------------------------------------|------------------------------------------|
| 1 | Search Product         | `GET`    | `/api/v1/products/search?q={query}`      | Full-text search with filters            |
| 2 | Check Nearby Inventory | `GET`    | `/api/v1/inventory/nearby?product_id=&lat=&lng=` | Geo-proximity stock check    |
| 3 | Add Product to Cart    | `POST`   | `/api/v1/cart/{user_id}/items`           | Add item to user's shopping cart         |
| 4 | Place Order            | `POST`   | `/api/v1/orders/`                        | Convert cart to confirmed order          |
| 5 | Get Delivery Status    | `GET`    | `/api/v1/delivery/{order_id}/status`     | Real-time delivery tracking (Task 6)     |

**Additional endpoints:**
| Feature                | Method   | URI                                |
|------------------------|----------|------------------------------------|
| Get Product by ID      | `GET`    | `/api/v1/products/{product_id}`    |
| List All Products      | `GET`    | `/api/v1/products/`                |
| Get Cart               | `GET`    | `/api/v1/cart/{user_id}`           |
| Clear Cart             | `DELETE` | `/api/v1/cart/{user_id}`           |
| Get Order Details      | `GET`    | `/api/v1/orders/{order_id}`        |
| Health Check           | `GET`    | `/health`                          |

---

## Task 3 – Add Product to Cart: Request & Response

### Request
**`POST /api/v1/cart/{user_id}/items`**

**Path Parameter:**
```
user_id: "USR-001"
```

**Request Body (JSON):**
```json
{
  "product_id": "PROD-001",
  "store_id":   "STORE-BLR-001",
  "quantity":   2
}
```

### Success Response – `201 Created`
```json
{
  "status": "success",
  "message": "Item added to cart successfully.",
  "cart": {
    "cart_id":   "CART-USR001-A1B2C3",
    "user_id":   "USR-001",
    "store_id":  "STORE-BLR-001",
    "items": [
      {
        "cart_item_id":  "CI-1A2B3C4D",
        "product_id":    "PROD-001",
        "product_name":  "Amul Full Cream Milk",
        "store_id":      "STORE-BLR-001",
        "quantity":      2,
        "unit_price":    68.0,
        "total_price":   136.0,
        "image_url":     "https://cdn.example.com/amul-milk.jpg"
      }
    ],
    "subtotal":      136.0,
    "delivery_fee":  20.0,
    "taxes":         6.12,
    "total_amount":  162.12,
    "item_count":    1,
    "created_at":    "2024-10-12T09:00:00Z",
    "updated_at":    "2024-10-12T09:00:05Z"
  }
}
```

### Error Responses
```json
// 404 – Product not found
{ "detail": "Product 'PROD-999' not found." }

// 404 – Not at store
{ "detail": "Product not available at store 'STORE-XYZ'." }

// 409 – Out of stock
{ "detail": "Insufficient stock. Available: 3, Requested: 10." }

// 400 – Mixed stores
{ "detail": "Cannot mix items from different stores. Your cart is from store 'STORE-BLR-001'." }
```

---

## Task 4 – HTTP Status Codes

| Status Code            | Scenario                                                              |
|------------------------|-----------------------------------------------------------------------|
| `200 OK`               | Successful GET (search, inventory, order, delivery)                   |
| `201 Created`          | Item successfully added to cart                                       |
| `204 No Content`       | Cart cleared (DELETE)                                                 |
| `400 Bad Request`      | Invalid input (mixing stores, empty cart, bad price range)            |
| `404 Not Found`        | Product, store, cart, order, or delivery record does not exist        |
| `409 Conflict`         | Out of stock, insufficient quantity, product unavailable              |
| `422 Unprocessable`    | Pydantic validation failure (missing fields, wrong type)              |
| `500 Internal Error`   | Unexpected server-side failure                                        |

---

## Task 5 – Sequence Diagram

```
User          API Gateway       Product Svc      Inventory Svc    Cart Svc        Order Svc       Delivery Svc
 |                |                  |                 |              |                |                |
 |--Search "milk"→|                  |                 |              |                |                |
 |                |--GET /products/search?q=milk----→|              |                |                |
 |                |←--200 [Product list]-----------  |              |                |                |
 |←--Products-----|                  |                 |              |                |                |
 |                |                  |                 |              |                |                |
 |--Check stock--→|                  |                 |              |                |                |
 |                |--GET /inventory/nearby?product_id=&lat=&lng=--→|              |                |
 |                |←--200 [Nearby stores with stock]------------   |              |                |
 |←--Stores-------|                  |                 |              |                |                |
 |                |                  |                 |              |                |                |
 |--Add to Cart--→|                  |                 |              |                |                |
 |                |--POST /cart/{user_id}/items----------------------→|              |                |
 |                |                  |                 |  [Validate stock]            |                |
 |                |←--201 [Updated Cart]----------------------------  |              |                |
 |←--Cart---------|                  |                 |              |                |                |
 |                |                  |                 |              |                |                |
 |--Place Order--→|                  |                 |              |                |                |
 |                |--POST /orders/--------------------------------------------→|                |
 |                |                  |                 |  [Deduct stock] [Assign Partner]             |
 |                |←--200 [Order Confirmed + Partner Assigned]----------------  |                |
 |←--Order ID-----|                  |                 |              |                |                |
 |                |                  |                 |              |                |                |
 |--Track Order--→|                  |                 |              |                |                |
 |                |--GET /delivery/{order_id}/status-----------------------------------→|
 |                |←--200 [DeliveryStatus: OUT_FOR_DELIVERY, ETA: 8 min]----------  |
 |←--ETA / GPS----|                  |                 |              |                |                |
```

---

## Task 6 – Get Delivery Status API (Additional API)

**`GET /api/v1/delivery/{order_id}/status`**

**Path Parameter:** `order_id: "ORD-20241012-A1B2C3"`

**Success Response – `200 OK`:**
```json
{
  "status":   "success",
  "order_id": "ORD-20241012-A1B2C3",
  "delivery": {
    "delivery_id":               "DEL-9F8E7D6C",
    "order_id":                  "ORD-20241012-A1B2C3",
    "status":                    "OUT_FOR_DELIVERY",
    "estimated_delivery_time":   8,
    "estimated_arrival_at":      "2024-10-12T09:23:00Z",
    "distance_remaining_km":     0.9,
    "partner": {
      "partner_id":      "DP-001",
      "name":            "Ravi Kumar",
      "phone":           "9876500001",
      "vehicle_type":    "Bike",
      "vehicle_number":  "KA01AB1234",
      "rating":          4.8,
      "current_latitude":  12.9300,
      "current_longitude": 77.6260
    },
    "tracking_events": [
      { "event": "Order placed and confirmed",       "timestamp": "2024-10-12T09:00:00Z" },
      { "event": "Delivery partner Ravi Kumar assigned", "timestamp": "2024-10-12T09:02:00Z" },
      { "event": "Partner heading to store",          "timestamp": "2024-10-12T09:05:00Z" },
      { "event": "Order picked up from store",        "timestamp": "2024-10-12T09:12:00Z" }
    ]
  }
}
```

**Error – `404 Not Found`:**
```json
{ "detail": "No delivery record found for order 'ORD-INVALID-999'." }
```

---

## Class Diagram

```
Product ──────────────── Inventory
  - id                     - inventory_id
  - name                   - product_id (FK)
  - price                  - store: StoreLocation
  - category               - available_quantity
  - brand                  - is_available
  - unit                   - price_at_store

Cart ─────────────────── CartItem
  - cart_id                - cart_item_id
  - user_id                - product_id (FK)
  - store_id               - quantity
  - items: [CartItem]      - unit_price
  - total_amount           - total_price

Order ────────────────── DeliveryAddress
  - order_id               - full_name
  - user_id (FK)           - latitude/longitude
  - cart_id (FK)           - city, state, pincode
  - items: [CartItem]
  - status: OrderStatus    Delivery
  - delivery_partner_id    - delivery_id
                           - order_id (FK)
                           - partner: DeliveryPartner
                           - status: DeliveryStatus
                           - tracking_events: [TrackingEvent]
```
