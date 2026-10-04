"""
schema.py — Pydantic models that define the shape of a valid receipt.

This is the contract between Gemini and the rest of the app.
Gemini's output is validated against these models before any code trusts it.
"""

from typing import Literal
from pydantic import BaseModel, Field


class LineItem(BaseModel):
    """One line on the receipt: an item, its quantity, and its price."""

    name: str = Field(description="Item name as printed on the receipt")
    quantity: float = Field(default=1.0, description="Quantity purchased")
    unit_price: float | None = Field(default=None, description="Price per unit, null if not printed")
    line_total: float = Field(description="Total for this line (quantity × unit_price)")


class Receipt(BaseModel):
    """The full structured receipt."""

    # Who & where
    merchant: str | None = Field(default=None, description="Store or restaurant name")
    currency: str = Field(default="INR", description="Currency symbol or code shown on receipt")

    # What was bought
    items: list[LineItem] = Field(description="All line items on the receipt")

    # What it added up to
    subtotal: float | None = Field(default=None, description="Sum before tax/service/tip")
    tax: float | None = Field(default=None, description="Tax amount (GST/VAT/sales tax)")
    service_charge: float | None = Field(default=None, description="Service charge if separate")
    tip: float | None = Field(default=None, description="Tip if separate")
    total: float = Field(description="Final amount printed on the receipt")

    # How confident are we
    status: Literal["ok", "partial", "unreadable"] = Field(
        default="ok",
        description="ok = fully readable; partial = some fields missing; unreadable = image unusable",
    )
    notes: str | None = Field(
        default=None,
        description="Plain-text caveats: 'tip handwritten', 'third item smudged', etc.",
    )