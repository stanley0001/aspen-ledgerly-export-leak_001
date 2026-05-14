from typing import List, Literal

from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    username: str
    role: Literal["ADMIN", "USER"]


class InvoiceSummary(BaseModel):
    invoice_id: str
    customer_name: str
    owner_username: str
    status: str
    currency: str
    total_cents: int


class LineItemPublic(BaseModel):
    sku: str
    description: str
    quantity: int
    unit_price_cents: int
    line_total_cents: int


class InvoiceDetail(BaseModel):
    invoice_id: str
    customer_name: str
    owner_username: str
    status: str
    currency: str
    visible_notes: str
    line_items: List[LineItemPublic]
    total_cents: int
