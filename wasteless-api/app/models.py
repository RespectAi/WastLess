# app/models.py

from sqlalchemy import (
    Column, Integer, String, Text, Date, 
    Boolean, ForeignKey, Enum
)
from sqlalchemy.orm import relationship
from .db import Base

class User(Base):
    __tablename__ = "users"

    user_id       = Column(Integer, primary_key=True, index=True)
    email         = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name          = Column(String(100))
    created_at    = Column(Date, nullable=False)

    # Relationships
    fridges       = relationship(
        "Fridge",
        secondary="fridge_users",
        back_populates="users"
    )
    added_items   = relationship("FridgeItem", back_populates="added_by_user")
    notifications = relationship("Notification", back_populates="user")


class Fridge(Base):
    __tablename__ = "fridges"

    fridge_id     = Column(Integer, primary_key=True, index=True)
    name          = Column(String(100), nullable=False)
    location_desc = Column(Text)
    created_at    = Column(Date, nullable=False)

    users         = relationship(
        "User",
        secondary="fridge_users",
        back_populates="fridges"
    )
    items         = relationship("FridgeItem", back_populates="fridge")


class FridgeUser(Base):
    __tablename__ = "fridge_users"

    fridge_id = Column(Integer, ForeignKey("fridges.fridge_id", ondelete="CASCADE"), primary_key=True)
    user_id   = Column(Integer, ForeignKey("users.user_id",   ondelete="CASCADE"), primary_key=True)
    role      = Column(String(20), nullable=False)


class Product(Base):
    __tablename__ = "products"

    product_id         = Column(Integer, primary_key=True, index=True)
    name               = Column(String(255), nullable=False)
    category           = Column(String(100))
    default_shelf_life = Column(Integer, nullable=False)  # days
    default_open_life  = Column(Integer)                  # days


class QRCode(Base):
    __tablename__ = "qr_codes"

    qr_code    = Column(String(100), primary_key=True)
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)
    batch_info = Column(String(255))
    info_url   = Column(Text)

    product    = relationship("Product", backref="qr_codes")


class FridgeItem(Base):
    __tablename__ = "fridge_items"

    item_id            = Column(Integer, primary_key=True, index=True)
    fridge_id          = Column(Integer, ForeignKey("fridges.fridge_id", ondelete="CASCADE"), nullable=False)
    added_by           = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    qr_code            = Column(String(100), ForeignKey("qr_codes.qr_code"), nullable=False)
    added_at           = Column(Date, nullable=False)
    factory_expires_at = Column(Date, nullable=False)
    opened_at          = Column(Date)
    open_life_days     = Column(Integer, nullable=False)
    spoil_date         = Column(Date)

    # Relationships
    fridge       = relationship("Fridge",    back_populates="items")
    added_by_user = relationship("User",      back_populates="added_items")
    qr            = relationship("QRCode")


class Notification(Base):
    __tablename__ = "notifications"

    note_id     = Column(Integer, primary_key=True, index=True)
    item_id     = Column(Integer, ForeignKey("fridge_items.item_id", ondelete="CASCADE"), nullable=False)
    user_id     = Column(Integer, ForeignKey("users.user_id"),          nullable=False)
    notified_at = Column(Date,    nullable=False)
    type        = Column(String(20), nullable=False)
    sent        = Column(Boolean, default=False)

    # Relationships
    user = relationship("User",      back_populates="notifications")
    item = relationship("FridgeItem")
