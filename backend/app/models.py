"""SQLAlchemy ORM models for creators, brands, tickets, and authentication."""

from datetime import datetime, timezone
import enum

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Index, text,
)
from sqlalchemy.orm import relationship

from .database import Base


class UserRole(str, enum.Enum):
    """Roles soportados. Extensible: agregar un valor aquí + su fila en la matriz
    de permisos (doc/auth-diseno-fase1.md §2) no requiere migración de esquema."""

    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    CREADOR = "creador"


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


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(150), nullable=False)
    role = Column(String(20), nullable=False)
    creator_id = Column(Integer, ForeignKey("creators.id", ondelete="SET NULL"), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    must_change_password = Column(Boolean, nullable=False, default=False)
    token_version = Column(Integer, nullable=False, default=0)
    failed_login_attempts = Column(Integer, nullable=False, default=0)
    locked_until = Column(DateTime, nullable=True)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    creator = relationship("Creator")
    refresh_tokens = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )

    __table_args__ = (
        # Un Creator tiene a lo sumo un usuario vinculado (NULL = sin vincular, permitido).
        Index(
            "ix_users_creator_id_unique",
            "creator_id",
            unique=True,
            sqlite_where=text("creator_id IS NOT NULL"),
        ),
    )


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=False)
    revoked_at = Column(DateTime, nullable=True)
    replaced_by_id = Column(Integer, ForeignKey("refresh_tokens.id"), nullable=True)

    user = relationship("User", back_populates="refresh_tokens")


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    actor_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(50), nullable=False)
    target_type = Column(String(50), nullable=True)
    target_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
