from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class DeliveryStatus(str, Enum):
    PARTNER_ASSIGNED = "PARTNER_ASSIGNED"
    PARTNER_HEADING_TO_STORE = "PARTNER_HEADING_TO_STORE"
    PARTNER_AT_STORE = "PARTNER_AT_STORE"
    ORDER_PICKED_UP = "ORDER_PICKED_UP"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    NEARBY = "NEARBY"
    DELIVERED = "DELIVERED"
    DELIVERY_FAILED = "DELIVERY_FAILED"


class DeliveryPartner(BaseModel):
    """Delivery partner/agent details."""
    partner_id: str = Field(..., description="Partner unique ID")
    name: str = Field(..., description="Partner name")
    phone: str = Field(..., description="Partner phone number")
    vehicle_type: str = Field(..., description="e.g., Bike, Cycle")
    vehicle_number: Optional[str] = Field(None, description="Vehicle registration number")
    rating: Optional[float] = Field(None, ge=0, le=5, description="Partner rating")
    current_latitude: Optional[float] = Field(None, description="Real-time latitude")
    current_longitude: Optional[float] = Field(None, description="Real-time longitude")


class TrackingEvent(BaseModel):
    """A single event in the delivery tracking timeline."""
    event: str = Field(..., description="Event description")
    timestamp: datetime = Field(..., description="When this event occurred")
    location: Optional[str] = Field(None, description="Location description")


class Delivery(BaseModel):
    """Delivery record for an order."""
    delivery_id: str = Field(..., description="Unique delivery ID")
    order_id: str = Field(..., description="Associated order ID")
    partner: Optional[DeliveryPartner] = Field(None, description="Assigned delivery partner")
    status: DeliveryStatus = Field(..., description="Current delivery status")
    estimated_delivery_time: int = Field(..., description="ETA in minutes")
    estimated_arrival_at: Optional[datetime] = Field(None, description="Estimated arrival datetime")
    distance_remaining_km: Optional[float] = Field(None, description="Remaining distance in km")
    tracking_events: List[TrackingEvent] = Field(default=[], description="Timeline of events")
    assigned_at: Optional[datetime] = Field(None)
    delivered_at: Optional[datetime] = Field(None)


class DeliveryStatusResponse(BaseModel):
    """Response for GET /api/v1/delivery/{order_id}/status"""
    status: str = Field("success", description="API response status")
    order_id: str = Field(..., description="Order ID")
    delivery: Delivery = Field(..., description="Delivery details")

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "success",
                "order_id": "ORD-20241012-001",
                "delivery": {
                    "delivery_id": "DEL-001",
                    "order_id": "ORD-20241012-001",
                    "partner": {
                        "partner_id": "DP-001",
                        "name": "Ravi Kumar",
                        "phone": "9876500001",
                        "vehicle_type": "Bike",
                        "vehicle_number": "KA01AB1234",
                        "rating": 4.8,
                        "current_latitude": 12.9300,
                        "current_longitude": 77.6260
                    },
                    "status": "OUT_FOR_DELIVERY",
                    "estimated_delivery_time": 8,
                    "distance_remaining_km": 0.9,
                    "tracking_events": [
                        {"event": "Order confirmed", "timestamp": "2024-10-12T09:00:00Z"},
                        {"event": "Delivery partner assigned", "timestamp": "2024-10-12T09:02:00Z"},
                        {"event": "Order picked up from store", "timestamp": "2024-10-12T09:10:00Z"}
                    ]
                }
            }
        }
    }
