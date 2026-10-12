"""
In-Memory Database with seed data for the Quick-Commerce Platform.
In a production system this would be replaced by:
  - PostgreSQL / MySQL  → Users, Orders
  - MongoDB            → Product Catalog
  - Redis              → Cart, Sessions, Cache
  - Cassandra          → Inventory (high write throughput)
"""
from datetime import datetime
from app.models.product import Product, ProductCategory
from app.models.inventory import Inventory, StoreLocation
from app.models.cart import Cart
from app.models.order import Order
from app.models.delivery import Delivery


# ──────────────────────────────────────────────
#  PRODUCTS
# ──────────────────────────────────────────────
products_db: dict[str, Product] = {
    "PROD-001": Product(
        id="PROD-001", name="Amul Full Cream Milk", brand="Amul",
        description="Fresh pasteurised full-cream milk", price=68.0,
        category=ProductCategory.DAIRY, unit="1 L",
        image_url="https://cdn.example.com/amul-milk.jpg", rating=4.5, in_stock=True,
    ),
    "PROD-002": Product(
        id="PROD-002", name="Farm Fresh Tomatoes", brand="FarmFresh",
        description="Organically grown juicy red tomatoes", price=35.0,
        category=ProductCategory.VEGETABLES, unit="500 g",
        image_url="https://cdn.example.com/tomatoes.jpg", rating=4.2, in_stock=True,
    ),
    "PROD-003": Product(
        id="PROD-003", name="Britannia Digestive Biscuits", brand="Britannia",
        description="Wholesome wheat digestive biscuits", price=55.0,
        category=ProductCategory.SNACKS, unit="400 g",
        image_url="https://cdn.example.com/britannia-digestive.jpg", rating=4.6, in_stock=True,
    ),
    "PROD-004": Product(
        id="PROD-004", name="Tropicana Orange Juice", brand="Tropicana",
        description="100% pure squeezed orange juice", price=99.0,
        category=ProductCategory.BEVERAGES, unit="1 L",
        image_url="https://cdn.example.com/tropicana.jpg", rating=4.3, in_stock=True,
    ),
    "PROD-005": Product(
        id="PROD-005", name="Sunlight Dish Wash Bar", brand="Sunlight",
        description="Powerful grease-cutting dish wash bar", price=28.0,
        category=ProductCategory.HOUSEHOLD, unit="500 g",
        image_url="https://cdn.example.com/sunlight.jpg", rating=4.0, in_stock=True,
    ),
    "PROD-006": Product(
        id="PROD-006", name="Lays Classic Salted Chips", brand="Lays",
        description="Crispy potato chips lightly salted", price=20.0,
        category=ProductCategory.SNACKS, unit="26 g",
        image_url="https://cdn.example.com/lays.jpg", rating=4.4, in_stock=True,
    ),
    "PROD-007": Product(
        id="PROD-007", name="Nature's Basket Banana", brand="Nature's Basket",
        description="Fresh ripe yellow bananas", price=45.0,
        category=ProductCategory.FRUITS, unit="6 pcs",
        image_url="https://cdn.example.com/banana.jpg", rating=4.1, in_stock=True,
    ),
    "PROD-008": Product(
        id="PROD-008", name="Nescafe Classic Coffee", brand="Nescafe",
        description="Rich aromatic instant coffee", price=225.0,
        category=ProductCategory.BEVERAGES, unit="100 g",
        image_url="https://cdn.example.com/nescafe.jpg", rating=4.7, in_stock=True,
    ),
}


# ──────────────────────────────────────────────
#  STORES
# ──────────────────────────────────────────────
stores_db: dict[str, StoreLocation] = {
    "STORE-BLR-001": StoreLocation(
        store_id="STORE-BLR-001", store_name="Dark Store – Koramangala",
        latitude=12.9352, longitude=77.6245,
        address="100 Feet Road, Koramangala, Bengaluru 560034",
        distance_km=1.2, delivery_time_minutes=12,
    ),
    "STORE-BLR-002": StoreLocation(
        store_id="STORE-BLR-002", store_name="Dark Store – Indiranagar",
        latitude=12.9784, longitude=77.6408,
        address="12th Main, Indiranagar, Bengaluru 560038",
        distance_km=3.5, delivery_time_minutes=20,
    ),
    "STORE-BLR-003": StoreLocation(
        store_id="STORE-BLR-003", store_name="Dark Store – HSR Layout",
        latitude=12.9121, longitude=77.6446,
        address="27th Main, HSR Layout, Bengaluru 560102",
        distance_km=5.1, delivery_time_minutes=28,
    ),
}


# ──────────────────────────────────────────────
#  INVENTORY  (product_id → list[Inventory])
# ──────────────────────────────────────────────
inventory_db: dict[str, list[Inventory]] = {
    "PROD-001": [
        Inventory(inventory_id="INV-P001-S001", product_id="PROD-001",
                  store=stores_db["STORE-BLR-001"], available_quantity=45,
                  reserved_quantity=3, is_available=True, price_at_store=68.0),
        Inventory(inventory_id="INV-P001-S002", product_id="PROD-001",
                  store=stores_db["STORE-BLR-002"], available_quantity=30,
                  reserved_quantity=0, is_available=True, price_at_store=68.0),
    ],
    "PROD-002": [
        Inventory(inventory_id="INV-P002-S001", product_id="PROD-002",
                  store=stores_db["STORE-BLR-001"], available_quantity=20,
                  reserved_quantity=2, is_available=True, price_at_store=35.0),
        Inventory(inventory_id="INV-P002-S003", product_id="PROD-002",
                  store=stores_db["STORE-BLR-003"], available_quantity=15,
                  reserved_quantity=0, is_available=True, price_at_store=35.0),
    ],
    "PROD-003": [
        Inventory(inventory_id="INV-P003-S001", product_id="PROD-003",
                  store=stores_db["STORE-BLR-001"], available_quantity=60,
                  reserved_quantity=5, is_available=True, price_at_store=55.0),
    ],
    "PROD-004": [
        Inventory(inventory_id="INV-P004-S002", product_id="PROD-004",
                  store=stores_db["STORE-BLR-002"], available_quantity=25,
                  reserved_quantity=0, is_available=True, price_at_store=99.0),
    ],
    "PROD-005": [
        Inventory(inventory_id="INV-P005-S001", product_id="PROD-005",
                  store=stores_db["STORE-BLR-001"], available_quantity=80,
                  reserved_quantity=0, is_available=True, price_at_store=28.0),
        Inventory(inventory_id="INV-P005-S003", product_id="PROD-005",
                  store=stores_db["STORE-BLR-003"], available_quantity=50,
                  reserved_quantity=1, is_available=True, price_at_store=28.0),
    ],
    "PROD-008": [
        Inventory(inventory_id="INV-P008-S002", product_id="PROD-008",
                  store=stores_db["STORE-BLR-002"], available_quantity=40,
                  reserved_quantity=0, is_available=True, price_at_store=225.0),
    ],
}


# ──────────────────────────────────────────────
#  CARTS  (user_id → Cart)
# ──────────────────────────────────────────────
carts_db: dict[str, Cart] = {}


# ──────────────────────────────────────────────
#  ORDERS  (order_id → Order)
# ──────────────────────────────────────────────
orders_db: dict[str, Order] = {}


# ──────────────────────────────────────────────
#  DELIVERIES  (order_id → Delivery)
# ──────────────────────────────────────────────
deliveries_db: dict[str, Delivery] = {}


# ──────────────────────────────────────────────
#  DELIVERY PARTNERS
# ──────────────────────────────────────────────
delivery_partners_pool = [
    {"partner_id": "DP-001", "name": "Ravi Kumar",  "phone": "9876500001",
     "vehicle_type": "Bike",  "vehicle_number": "KA01AB1234", "rating": 4.8,
     "current_latitude": 12.9300, "current_longitude": 77.6260},
    {"partner_id": "DP-002", "name": "Suresh Nair",  "phone": "9876500002",
     "vehicle_type": "Bike",  "vehicle_number": "KA01CD5678", "rating": 4.6,
     "current_latitude": 12.9360, "current_longitude": 77.6250},
    {"partner_id": "DP-003", "name": "Anita Desai", "phone": "9876500003",
     "vehicle_type": "Cycle", "vehicle_number": None,          "rating": 4.9,
     "current_latitude": 12.9340, "current_longitude": 77.6240},
]
