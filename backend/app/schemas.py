"""Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class CreatorBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    initial_budget: float = Field(..., gt=0)


class CreatorCreate(CreatorBase):
    pass


class CreatorUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    initial_budget: Optional[float] = Field(None, gt=0)
    is_active: Optional[bool] = None


class CreatorResponse(CreatorBase):
    id: int
    spent_budget: float
    remaining_budget: float
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class CreatorKpiResponse(BaseModel):
    total_budget: float
    total_spent: float
    total_remaining: float
    active_creators: int


class BrandBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class BrandCreate(BrandBase):
    pass


class BrandUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None


class BrandResponse(BrandBase):
    id: int
    is_active: bool

    model_config = {"from_attributes": True}


class TicketResponse(BaseModel):
    id: int
    creator_id: int
    brand_id: int
    amount: float
    file_name: str
    file_path: str
    mime_type: str
    upload_date: datetime
    notes: Optional[str] = None
    creator_name: Optional[str] = None
    brand_name: Optional[str] = None

    model_config = {"from_attributes": True}


class BrandSpendItem(BaseModel):
    brand_name: str
    total_spent: float


class MessageResponse(BaseModel):
    message: str


# ── Dashboard ──────────────────────────────────────────────────────────────────


class MonthlySpendItem(BaseModel):
    month: str  # "2026-07"
    total: float
    count: int


class CreatorUsageItem(BaseModel):
    creator_id: int
    name: str
    spent: float
    initial_budget: float
    percentage: float  # 0-100


class DashboardSummary(BaseModel):
    total_spent: float
    ticket_count: int
    avg_ticket: float
    active_brands: int


# ── Autenticación ────────────────────────────────────────────────────────────


class LoginRequest(BaseModel):
    identificador: str = Field(..., min_length=1, description="Nombre de usuario o correo")
    password: str = Field(..., min_length=1)


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: str
    role: str
    creator_id: Optional[int] = None
    is_active: bool
    must_change_password: bool
    last_login: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    user: UserResponse


class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=150)
    email: Optional[EmailStr] = None


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=10)


# ── Gestión de usuarios (Administración) ────────────────────────────────────


class UserCreateRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=150)
    role: str
    password: Optional[str] = Field(None, min_length=10)
    creator_id: Optional[int] = None


class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=150)
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    creator_id: Optional[int] = None


class SetUserActiveRequest(BaseModel):
    is_active: bool
    confirm_username: Optional[str] = None


class ResetPasswordResponse(BaseModel):
    temporary_password: str
