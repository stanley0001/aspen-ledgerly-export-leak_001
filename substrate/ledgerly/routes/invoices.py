from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status

from ledgerly.auth import current_user
from ledgerly.models import Invoice, LineItem, User, store


router = APIRouter(prefix="/invoices", tags=["invoices"])


def _get_invoice_or_404(invoice_id: str) -> Invoice:
    invoice = store.get_invoice(invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )
    return invoice


def _ensure_invoice_access(user: User, invoice: Invoice) -> None:
    if user.is_admin:
        return
    if invoice.owner_username != user.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invoice access denied",
        )


def _line_item_public(item: LineItem) -> dict:
    return {
        "sku": item.sku,
        "description": item.description,
        "quantity": item.quantity,
        "unit_price_cents": item.unit_price_cents,
        "line_total_cents": item.line_total_cents,
    }


def _line_item_internal(item: LineItem) -> dict:
    public = _line_item_public(item)
    public.update(
        {
            "supplier_cost_cents": item.supplier_cost_cents,
            "internal_tag": item.internal_tag,
            "margin_bps": item.margin_bps,
        }
    )
    return public


def _invoice_summary(invoice: Invoice) -> dict:
    return {
        "invoice_id": invoice.invoice_id,
        "customer_name": invoice.customer_name,
        "owner_username": invoice.owner_username,
        "status": invoice.status,
        "currency": invoice.currency,
        "total_cents": invoice.total_cents,
    }


def _invoice_detail(invoice: Invoice) -> dict:
    summary = _invoice_summary(invoice)
    summary.update(
        {
            "visible_notes": invoice.visible_notes,
            "line_items": [_line_item_public(item) for item in invoice.line_items],
        }
    )
    return summary


def _customer_export(invoice: Invoice) -> dict:
    return {
        "scope": "customer",
        "invoice_id": invoice.invoice_id,
        "customer_name": invoice.customer_name,
        "status": invoice.status,
        "currency": invoice.currency,
        "visible_notes": invoice.visible_notes,
        "line_items": [_line_item_public(item) for item in invoice.line_items],
        "total_cents": invoice.total_cents,
    }


def _internal_export(invoice: Invoice) -> dict:
    payload = _customer_export(invoice)
    payload.update(
        {
            "scope": "internal",
            "collection_notes": invoice.collection_notes,
            "fraud_score": invoice.fraud_score,
            "payment_token_hint": invoice.payment_token_hint,
            "line_items": [_line_item_internal(item) for item in invoice.line_items],
        }
    )
    return payload


def _select_export_payload(invoice: Invoice, scope: Literal["customer", "internal"]) -> dict:
    if scope == "internal":
        return _internal_export(invoice)
    return _customer_export(invoice)


@router.get("")
def list_invoices(user: User = Depends(current_user)):
    invoices = store.list_invoices()
    if not user.is_admin:
        invoices = [invoice for invoice in invoices if invoice.owner_username == user.username]
    return [_invoice_summary(invoice) for invoice in invoices]


@router.get("/{invoice_id}")
def get_invoice(invoice_id: str, user: User = Depends(current_user)):
    invoice = _get_invoice_or_404(invoice_id)
    _ensure_invoice_access(user, invoice)
    return _invoice_detail(invoice)


@router.get("/{invoice_id}/export-preview")
def export_preview(
    invoice_id: str,
    scope: Literal["customer", "internal"] = "customer",
    user: User = Depends(current_user),
):
    invoice = _get_invoice_or_404(invoice_id)
    _ensure_invoice_access(user, invoice)
    return _select_export_payload(invoice, scope)


@router.get("/{invoice_id}/export-download")
def export_download(
    invoice_id: str,
    scope: Literal["customer", "internal"] = "customer",
    user: User = Depends(current_user),
):
    invoice = _get_invoice_or_404(invoice_id)
    _ensure_invoice_access(user, invoice)
    return {
        "file_name": f"{invoice.invoice_id}-{scope}.json",
        "export": _select_export_payload(invoice, scope),
    }


@router.post("/{invoice_id}/share-export")
def share_export(
    invoice_id: str,
    scope: Literal["customer", "internal"] = "customer",
    user: User = Depends(current_user),
):
    invoice = _get_invoice_or_404(invoice_id)
    _ensure_invoice_access(user, invoice)
    return {
        "share_id": f"shr-{invoice.invoice_id}-{scope}",
        "export": _select_export_payload(invoice, scope),
    }
