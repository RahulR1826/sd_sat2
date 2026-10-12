# High-Level Design (HLD) – Food & Grocery Quick-Commerce Platform

## Round 3 – High-Level System Design Challenge (25 Marks)

Design goal: Support **millions of customers** and **high-volume orders** during peak periods.

---

## Task 1 – System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                        │
│   Mobile App (iOS/Android)     Web App (React)     Partner App              │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │ HTTPS / REST / WebSocket
┌──────────────────────────────▼──────────────────────────────────────────────┐
│                      API GATEWAY (Kong / AWS API Gateway)                   │
│    Rate Limiting   |   Auth (JWT)   |   SSL Termination   |   Load Balancing│
└──────┬────────┬────────┬───────┬────────┬─────────────────────────────────--┘
       │        │        │       │        │
┌──────▼──┐ ┌──▼───┐ ┌──▼──┐ ┌──▼──┐ ┌──▼──────┐
│  User   │ │Prod. │ │Inv. │ │Cart │ │  Order  │  ← Microservices
│ Service │ │ Svc  │ │ Svc │ │ Svc │ │  Svc    │
└────┬────┘ └──┬───┘ └──┬──┘ └──┬──┘ └──┬──────┘
     │         │         │       │        │
┌────▼─────────▼─────────▼───────▼────────▼──────┐
│             MESSAGE BROKER (Apache Kafka)        │
│  Topics: order-placed, inventory-update,         │
│          delivery-assigned, notifications        │
└──────────────────────────┬──────────────────────┘
                           │
              ┌────────────▼─────────────┐
              │     Delivery Service      │
              │  (Partner Assignment,     │
              │   Real-time Tracking)     │
              └──────────────────────────┘
```

### Microservices

| Service            | Responsibility                                                  |
|--------------------|------------------------------------------------------------------|
| **User Service**   | Registration, authentication (JWT), profile management          |
| **Product Service**| Catalog CRUD, category management, image handling               |
| **Inventory Svc**  | Stock levels per store, reservation, availability checks        |
| **Cart Service**   | Cart lifecycle, item management, pricing computation             |
| **Order Service**  | Order creation, payment processing, status management           |
| **Delivery Svc**   | Partner assignment, real-time GPS tracking, ETA computation     |
| **Notification Svc**| Push notifications, SMS, email via Twilio/Firebase             |
| **Search Service** | Elasticsearch-powered full-text product search                  |

---

## Task 2 – REST API Communication (Mobile ↔ Backend)

```
Mobile App
    │
    ├─ GET  /api/v1/products/search?q=milk         ──→  Product Service
    ├─ GET  /api/v1/inventory/nearby?product_id=…  ──→  Inventory Service
    ├─ POST /api/v1/cart/{user_id}/items           ──→  Cart Service
    │                                                         │
    │                                              ←── Inventory Service (stock check)
    │                                              ←── Product Service  (price fetch)
    ├─ POST /api/v1/orders/                        ──→  Order Service
    │                                                         │
    │                                              ──→  Payment Gateway (Razorpay)
    │                                              ──→  Kafka: "order-placed" event
    │                                                         │
    │                                              ←── Delivery Service (partner assign)
    │                                              ←── Notification: push + SMS
    │
    └─ GET  /api/v1/delivery/{order_id}/status     ──→  Delivery Service
                                                         (WebSocket for real-time GPS)
```

**Inter-service Communication:**
- **Synchronous**: REST (for latency-sensitive: cart, search)
- **Asynchronous**: Kafka events (for order flow, notifications, inventory deduction)
- **Real-time**: WebSockets (delivery GPS tracking)

---

## Task 3 – Database Selection

| Service          | Database            | Justification                                              |
|------------------|---------------------|------------------------------------------------------------|
| **Users**        | PostgreSQL          | ACID transactions, relational data, strong consistency     |
| **Products**     | MongoDB             | Flexible schema, nested attributes, horizontal scaling     |
| **Inventory**    | Cassandra           | High write throughput, partition by store_id + product_id  |
| **Cart**         | Redis (Hash)        | Sub-millisecond reads, TTL-based expiry, session storage   |
| **Orders**       | PostgreSQL          | ACID for financial transactions, complex joins             |
| **Delivery GPS** | Redis + TimescaleDB | Real-time location (Redis), historical analysis (Timescale)|
| **Search Index** | Elasticsearch       | Full-text search, faceted filtering, ranking               |
| **Audit Logs**   | Apache Cassandra    | Append-only, high-volume write, time-series data           |

### Inventory Cassandra Schema
```sql
CREATE TABLE inventory_by_store (
    store_id     TEXT,
    product_id   TEXT,
    quantity     INT,
    is_available BOOLEAN,
    updated_at   TIMESTAMP,
    PRIMARY KEY  ((store_id), product_id)
) WITH CLUSTERING ORDER BY (product_id ASC);
```

---

## Task 4 – Caching Strategy

### Cache Architecture (Redis Cluster)

```
Request Flow with Cache:
  Client → API Gateway → Service → [Cache HIT] → Return (< 5ms)
                                 → [Cache MISS] → DB → Update Cache → Return
```

| Cache Key Pattern               | Data Cached                     | TTL      | Strategy      |
|---------------------------------|---------------------------------|----------|---------------|
| `product:{product_id}`          | Product details                 | 1 hour   | Write-through |
| `search:{query_hash}`           | Search results                  | 5 min    | Lazy loading  |
| `inventory:{store}:{product}`   | Stock count                     | 30 sec   | Write-around  |
| `cart:{user_id}`                | Full cart state                 | 24 hours | Write-through |
| `trending:products`             | Top-selling products            | 15 min   | Background job|
| `store:nearby:{geo_hash}`       | Nearby stores list              | 5 min    | Lazy loading  |

**Cache Invalidation:**
- Product update → Evict `product:{id}` and `search:*`
- Inventory change → Evict `inventory:{store}:{product}` immediately
- Order placed → Evict `cart:{user_id}`

---

## Task 5 – Messaging / Event-Driven Architecture (Kafka)

```
                     ┌─────────────────────────────────┐
                     │         Apache Kafka             │
                     │                                  │
  Order Service ───→ │ Topic: order.placed              │ ──→ Inventory Service (deduct)
                     │                                  │ ──→ Notification Service (confirm SMS)
                     │                                  │ ──→ Analytics Service
                     │                                  │
  Inventory Svc ───→ │ Topic: inventory.updated         │ ──→ Product Service (update cache)
                     │                                  │ ──→ Alert Service (low stock)
                     │                                  │
  Delivery Svc ────→ │ Topic: delivery.assigned         │ ──→ Notification (partner SMS)
                     │                                  │ ──→ Order Service (status update)
                     │                                  │
  Delivery Svc ────→ │ Topic: delivery.status.changed   │ ──→ Notification (customer push)
                     │                                  │ ──→ Analytics (delivery metrics)
                     └─────────────────────────────────┘
```

### Kafka Topic Design

| Topic                    | Producer         | Consumers                             | Partition Key  |
|--------------------------|------------------|---------------------------------------|----------------|
| `order.placed`           | Order Service    | Inventory, Notification, Analytics    | `user_id`      |
| `order.status.changed`   | Order Service    | Notification Service                  | `order_id`     |
| `inventory.updated`      | Inventory Svc    | Product Service, Alert Service        | `store_id`     |
| `delivery.assigned`      | Delivery Svc     | Notification, Order Service           | `order_id`     |
| `delivery.gps.update`    | Partner App      | Delivery Service, WebSocket Server    | `partner_id`   |
| `notification.send`      | All Services     | Notification Service                  | `user_id`      |

---

## Task 6 – Scalability Strategy

### Peak-Hour Order Handling

```
Normal Load:    1,000 orders/hour
Peak Load:     50,000 orders/hour  (Diwali sale, morning rush 7-9 AM)
```

#### 1. Horizontal Auto-Scaling
```yaml
# Kubernetes HPA for Order Service
minReplicas: 3
maxReplicas: 50
targetCPUUtilizationPercentage: 70
targetMemoryUtilizationPercentage: 75
```

#### 2. Database Scaling

| Strategy             | Applied To                          | Detail                                     |
|----------------------|-------------------------------------|--------------------------------------------|
| Read Replicas        | PostgreSQL (Users, Orders)          | Route reads to replicas, writes to primary |
| Sharding             | MongoDB (Products)                  | Shard by `category` or `region`            |
| Partitioning         | Cassandra (Inventory)               | Partition by `store_id`                    |
| Redis Cluster        | Cart, Cache                         | 6-node cluster with replication            |

#### 3. Inventory Management Under Peak Load

- **Optimistic Locking**: Version-based updates prevent overselling
- **Inventory Reservation**: Reserve stock when added to cart (30-min TTL)
- **Eventual Consistency**: Kafka async deduction after payment confirmation
- **Circuit Breaker**: If Inventory Service is overloaded, return cached availability

```python
# Optimistic locking pseudocode
UPDATE inventory
SET quantity = quantity - requested,
    version  = version + 1
WHERE product_id = ? AND store_id = ?
  AND version    = expected_version
  AND quantity  >= requested;
```

#### 4. Rapidly Changing Inventory

- **Short TTL Cache** (30 sec) for inventory data
- **Write-through cache**: Every inventory write updates Redis immediately
- **Kafka Streams**: Real-time inventory aggregation with windowed computations
- **Stock Alerts**: Automated restock notifications via Kafka when threshold reached

#### 5. CDN for Product Assets

- Product images served via **CloudFront CDN**
- API responses with `Cache-Control` headers for browser caching
- Edge caching for search results at geographic POPs

#### 6. Load Balancer & Rate Limiting

```
Users → CloudFront → ALB → API Gateway (Kong)
                              │
                      Rate Limit: 100 req/min per user
                      DDoS Protection: AWS Shield
                      Circuit Breaker: Resilience4j
```

---

## Architecture Summary Diagram

```
┌────────────────────────────────────────────────────────────────────────┐
│  CLIENTS: Mobile Apps | Web | Partner App                              │
└─────────────────────────────┬──────────────────────────────────────────┘
                              │ HTTPS
                    ┌─────────▼─────────┐
                    │   CloudFront CDN  │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │   API Gateway     │  JWT Auth, Rate Limit, SSL
                    └────┬──────────────┘
          ┌──────────────┼─────────────────────────┐
          │              │                          │
   ┌──────▼──┐    ┌──────▼──┐    ┌──────▼──┐  ┌───▼──────┐
   │ Product │    │Inventory│    │  Cart   │  │  Order   │
   │  Svc   │    │   Svc   │    │   Svc   │  │   Svc    │
   │(MongoDB)│    │(Cassand)│    │ (Redis) │  │(Postgres)│
   └────┬────┘    └────┬────┘    └────┬────┘  └───┬──────┘
        │              │               │            │
        └──────────────┴───────────────┴────────────┘
                              │
                    ┌─────────▼─────────┐
                    │   Apache Kafka    │  Event Bus
                    └─────┬───────┬─────┘
                          │       │
               ┌──────────▼──┐ ┌──▼──────────┐
               │  Delivery   │ │Notification │
               │   Service   │ │   Service   │
               │  (Redis GPS)│ │(Firebase/   │
               └─────────────┘ │  Twilio)    │
                               └─────────────┘
```
