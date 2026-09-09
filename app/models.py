
from datetime import datetime

from app.database import db


# Shopper Analytics
class FootfallEvent(db.Model):
    __tablename__ = "footfall_events"

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    direction = db.Column(db.String(10), nullable=False)   # 'IN' or 'OUT'
    zone = db.Column(db.String(100), default="main_entrance")
    tracking_id = db.Column(db.String(50))  # ephemeral anonymous tracker ID, not identity

    __table_args__ = (
        db.CheckConstraint("direction IN ('IN', 'OUT')", name="ck_footfall_direction"),
    )


# Inventory Monitoring
class ShelfSkuMap(db.Model):
    """Planogram map: which SKU SHOULD occupy which physical shelf position."""
    __tablename__ = "shelf_sku_map"

    shelf_zone = db.Column(db.String(100), primary_key=True)  # e.g. 'aisle_3_shelf_2_pos_4'
    sku_id = db.Column(db.String(100), nullable=False)         # e.g. 'MAGGI_MASALA_70G'
    sku_name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100))
    min_facings = db.Column(db.Integer, default=1)

    oos_events = db.relationship("OosEvent", backref="shelf", cascade="all, delete-orphan")


class OosEvent(db.Model):
    __tablename__ = "oos_events"

    id = db.Column(db.Integer, primary_key=True)
    shelf_zone = db.Column(db.String(100), db.ForeignKey("shelf_sku_map.shelf_zone"), nullable=False)
    sku_id = db.Column(db.String(100))  # resolved via shelf_sku_map at insert time
    detected_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    resolved_at = db.Column(db.DateTime)  # NULL until restocked
    status = db.Column(db.String(20), default="OUT_OF_STOCK", nullable=False)
    duration_secs = db.Column(db.Integer)  # computed once resolved

    __table_args__ = (
        db.CheckConstraint(
            "status IN ('LOW_STOCK', 'OUT_OF_STOCK', 'RESOLVED')", name="ck_oos_status"
        ),
    )


# Queue Intelligence
class Counter(db.Model):
    """Store configuration: total checkout counters and open/closed state."""
    __tablename__ = "counters"

    counter_id = db.Column(db.String(50), primary_key=True)
    is_open = db.Column(db.Integer, default=1, nullable=False)  # 1 = open, 0 = closed

    queue_events = db.relationship("QueueEvent", backref="counter", cascade="all, delete-orphan")


class QueueEvent(db.Model):
    __tablename__ = "queue_events"

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    counter_id = db.Column(db.String(50), db.ForeignKey("counters.counter_id"), nullable=False)
    queue_length = db.Column(db.Integer, nullable=False)
    avg_wait_secs = db.Column(db.Float)
    service_secs = db.Column(db.Float)


# Dashboard — Alerts & Users
class Alert(db.Model):
    __tablename__ = "alerts"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    source = db.Column(db.String(20), nullable=False)     # 'INVENTORY' | 'QUEUE' | 'FOOTFALL' | 'SYSTEM'
    severity = db.Column(db.String(20), default="INFO", nullable=False)  # 'INFO' | 'WARNING' | 'CRITICAL'
    message = db.Column(db.Text, nullable=False)
    acknowledged = db.Column(db.Integer, default=0, nullable=False)  # 0 = unread, 1 = ack'd

    __table_args__ = (
        db.CheckConstraint(
            "source IN ('INVENTORY', 'QUEUE', 'FOOTFALL', 'SYSTEM')", name="ck_alert_source"
        ),
        db.CheckConstraint(
            "severity IN ('INFO', 'WARNING', 'CRITICAL')", name="ck_alert_severity"
        ),
    )


class User(db.Model):
    """Same pattern as your hospital app's User model, retail-specific roles."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="staff", nullable=False)  # 'staff' | 'manager' | 'admin'

    __table_args__ = (
        db.CheckConstraint("role IN ('staff', 'manager', 'admin')", name="ck_user_role"),
    )