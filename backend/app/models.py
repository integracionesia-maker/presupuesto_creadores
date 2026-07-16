"""SQLAlchemy ORM models for creators, brands, and tickets."""

from datetime import datetime, timezone

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey,
)
from sqlalchemy.orm import relationship

from .database import Base


class Creator(Base):
    __tablename__ = "creators"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    initial_budget = Column(Float, nullable=False)
    spent_budget = Column(Float, nullable=False, default=0.00)
    remaining_budget = Column(Float, nullable=False, default=0.00)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    tickets = relationship("Ticket", back_populates="creator", lazy="selectin")


class Brand(Base):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    tickets = relationship("Ticket", back_populates="brand", lazy="selectin")


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    creator_id = Column(Integer, ForeignKey("creators.id", ondelete="RESTRICT"), nullable=False)
    brand_id = Column(Integer, ForeignKey("brands.id", ondelete="RESTRICT"), nullable=False)
    amount = Column(Float, nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    mime_type = Column(String(100), nullable=False)
    upload_date = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    notes = Column(Text, nullable=True)

    creator = relationship("Creator", back_populates="tickets")
    brand = relationship("Brand", back_populates="tickets")
