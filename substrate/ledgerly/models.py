from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class User:
    username: str
    password: str
    role: str
    full_name: str

    @property
    def is_admin(self) -> bool:
        return self.role == "ADMIN"


@dataclass
class LineItem:
    sku: str
    description: str
    quantity: int
    unit_price_cents: int
    supplier_cost_cents: int
    internal_tag: str
    margin_bps: int

    @property
    def line_total_cents(self) -> int:
        return self.quantity * self.unit_price_cents


@dataclass
class Invoice:
    invoice_id: str
    owner_username: str
    customer_name: str
    status: str
    currency: str
    visible_notes: str
    collection_notes: str
    fraud_score: int
    payment_token_hint: str
    line_items: List[LineItem] = field(default_factory=list)

    @property
    def total_cents(self) -> int:
        return sum(item.line_total_cents for item in self.line_items)


class Store:
    def __init__(self) -> None:
        self._users: Dict[str, User] = {}
        self._invoices: Dict[str, Invoice] = {}

    def reset(self) -> None:
        self._users.clear()
        self._invoices.clear()

    def add_user(self, user: User) -> None:
        self._users[user.username] = user

    def add_invoice(self, invoice: Invoice) -> None:
        self._invoices[invoice.invoice_id] = invoice

    def get_user(self, username: str) -> Optional[User]:
        return self._users.get(username)

    def list_users(self) -> List[User]:
        return list(self._users.values())

    def get_invoice(self, invoice_id: str) -> Optional[Invoice]:
        return self._invoices.get(invoice_id)

    def list_invoices(self) -> List[Invoice]:
        return list(self._invoices.values())


store = Store()


def seed(target: Store) -> None:
    target.add_user(
        User(
            username="admin",
            password="admin123",
            role="ADMIN",
            full_name="Avery Finch",
        )
    )
    target.add_user(
        User(
            username="alice",
            password="alice123",
            role="USER",
            full_name="Alice Mercer",
        )
    )
    target.add_user(
        User(
            username="bob",
            password="bob123",
            role="USER",
            full_name="Bob Imani",
        )
    )

    target.add_invoice(
        Invoice(
            invoice_id="inv-1001",
            owner_username="alice",
            customer_name="Acme Retail",
            status="draft",
            currency="USD",
            visible_notes="Customer requested a PDF copy for procurement.",
            collection_notes="Needs CFO sign-off before discounting.",
            fraud_score=82,
            payment_token_hint="tok_live_visa_4242",
            line_items=[
                LineItem(
                    sku="plan-pro",
                    description="Annual Pro plan",
                    quantity=1,
                    unit_price_cents=120000,
                    supplier_cost_cents=45000,
                    internal_tag="margin-anchor",
                    margin_bps=6250,
                ),
                LineItem(
                    sku="svc-onboarding",
                    description="Guided onboarding",
                    quantity=2,
                    unit_price_cents=15000,
                    supplier_cost_cents=4000,
                    internal_tag="partner-routed",
                    margin_bps=7333,
                ),
            ],
        )
    )
    target.add_invoice(
        Invoice(
            invoice_id="inv-1002",
            owner_username="alice",
            customer_name="Northwind Labs",
            status="sent",
            currency="USD",
            visible_notes="Invoice includes quarterly support uplift.",
            collection_notes="Renewal at risk if discount exceeds 12%.",
            fraud_score=18,
            payment_token_hint="tok_live_amex_3005",
            line_items=[
                LineItem(
                    sku="support-q",
                    description="Quarterly support block",
                    quantity=1,
                    unit_price_cents=45000,
                    supplier_cost_cents=12000,
                    internal_tag="renewal-watch",
                    margin_bps=7333,
                )
            ],
        )
    )
    target.add_invoice(
        Invoice(
            invoice_id="inv-2001",
            owner_username="bob",
            customer_name="Blue Mesa Foods",
            status="draft",
            currency="USD",
            visible_notes="Customer asked for split billing next month.",
            collection_notes="Collections hold if card update slips again.",
            fraud_score=44,
            payment_token_hint="tok_live_mc_5454",
            line_items=[
                LineItem(
                    sku="plan-team",
                    description="Team plan",
                    quantity=3,
                    unit_price_cents=30000,
                    supplier_cost_cents=11000,
                    internal_tag="channel-led",
                    margin_bps=6333,
                )
            ],
        )
    )
