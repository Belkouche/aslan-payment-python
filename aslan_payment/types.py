"""Type definitions for the Aslan Payment SDK.

All types use TypedDict for maximum compatibility and zero runtime overhead.
"""

from __future__ import annotations

from typing import Any, Literal, Optional, TypedDict


# ── Checkout Sessions ──


class CustomerParams(TypedDict, total=False):
    email: str
    name: str
    phone: str
    phone_country_code: str


class Address(TypedDict, total=False):
    line1: str
    city: str
    postal_code: str
    state: str
    country: str  # ISO 3166-1 alpha-2


class ShippingAddress(Address, total=False):
    recipient_name: str


class LineItem(TypedDict, total=False):
    name: str  # Required at runtime
    quantity: int  # Required at runtime
    unit_price: int  # Required at runtime, price per unit in centimes
    description: str
    sku: str
    image_url: str
    category: str
    seller_id: str


class CreateCheckoutSessionParams(TypedDict, total=False):
    amount: int  # Required: amount in centimes (100 = 1.00 MAD)
    currency: Literal["MAD"]
    success_url: str  # Required: HTTPS redirect URL on success
    cancel_url: str  # Required: HTTPS redirect URL on cancel
    customer: CustomerParams
    billing_address: Address
    shipping_address: ShippingAddress
    line_items: list[LineItem]
    metadata: dict[str, str]


class CheckoutSession(TypedDict, total=False):
    id: str
    token: str
    url: str
    expires_at: str
    amount: int
    currency: str
    status: str
    metadata: dict[str, str]


# ── Transactions ──

TransactionStatus = Literal[
    "pending",
    "processing",
    "succeeded",
    "failed",
    "expired",
    "refunded",
    "partially_refunded",
]


class TransactionCustomer(TypedDict, total=False):
    email: str
    name: str
    phone: str


class Transaction(TypedDict, total=False):
    id: str
    amount: int
    currency: str
    status: TransactionStatus
    merchant_id: str
    checkout_session_id: str
    paid_at: str
    created_at: str
    updated_at: str
    metadata: dict[str, str]
    customer: TransactionCustomer


class ListTransactionsParams(TypedDict, total=False):
    page: int
    page_size: int
    status: TransactionStatus
    from_date: str  # ISO 8601 datetime string
    to_date: str  # ISO 8601 datetime string
    sort_by: Literal["created_at", "amount", "status"]
    sort_order: Literal["asc", "desc"]


class Pagination(TypedDict):
    page: int
    page_size: int
    total: int
    total_pages: int


class PaginatedResponse(TypedDict):
    data: list[Any]
    pagination: Pagination


# ── Payment Links ──


class CreatePaymentLinkParams(TypedDict, total=False):
    amount: int  # Required: amount in centimes
    currency: Literal["MAD"]
    description: str
    max_payments: int
    expires_at: str  # ISO 8601 datetime string
    metadata: dict[str, str]


PaymentLinkStatus = Literal["active", "inactive", "expired"]


class PaymentLink(TypedDict, total=False):
    id: str
    url: str
    amount: int
    currency: str
    description: str
    status: PaymentLinkStatus
    max_payments: int
    payment_count: int
    expires_at: str
    created_at: str
    metadata: dict[str, str]


class ListPaymentLinksParams(TypedDict, total=False):
    page: int
    page_size: int
    status: PaymentLinkStatus


class UpdatePaymentLinkParams(TypedDict, total=False):
    description: str
    status: PaymentLinkStatus
    max_payments: int
    expires_at: str  # ISO 8601 datetime string
    metadata: dict[str, str]


class QrCodeParams(TypedDict, total=False):
    format: Literal["png", "svg"]
    size: int


class QrCode(TypedDict, total=False):
    url: str
    format: str
    size: int
    data: str


# ── Refunds ──

RefundStatus = Literal["pending", "succeeded", "failed"]


class CreateRefundParams(TypedDict, total=False):
    transaction_id: str  # Required
    amount: int  # Required: refund amount in centimes
    reason: str


class Refund(TypedDict, total=False):
    id: str
    transaction_id: str
    amount: int
    currency: str
    status: RefundStatus
    reason: str
    created_at: str


class ListRefundsParams(TypedDict, total=False):
    page: int
    page_size: int
    status: RefundStatus
    transaction_id: str


# ── Webhooks ──


class WebhookEvent(TypedDict, total=False):
    id: str
    type: str
    data: dict[str, Any]
    created_at: str
