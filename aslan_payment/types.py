"""Type definitions for the Aslan Payment SDK.

All types use TypedDict for maximum compatibility and zero runtime overhead.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, TypedDict


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


class SellerParams(TypedDict, total=False):
    id: str  # Required at runtime
    name: str  # Required at runtime
    email: str
    commissionRate: int  # 0-10000 basis points
    fixedFee: int
    metadata: Dict[str, str]


class BrowserInfo(TypedDict, total=False):
    userAgent: str
    acceptHeader: str
    language: str
    colorDepth: int
    screenHeight: int
    screenWidth: int
    timeZoneOffset: int
    javaEnabled: bool


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
    sellers: list[SellerParams]
    browserInfo: BrowserInfo
    require3ds: bool
    vendorId: str


class CheckoutSession(TypedDict, total=False):
    id: str
    token: str
    url: str
    expires_at: str
    amount: int
    currency: str
    status: str
    metadata: dict[str, str]
    openAmount: bool


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
    amount: Optional[int]  # Optional: amount in centimes (null = open amount)
    currency: Literal["MAD"]
    description: str
    max_payments: int
    expires_at: str  # ISO 8601 datetime string
    metadata: dict[str, str]
    minAmount: int
    maxAmount: int
    vendorId: str


PaymentLinkStatus = Literal["active", "inactive", "expired"]


class PaymentLink(TypedDict, total=False):
    id: str
    url: str
    amount: Optional[int]
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

RefundStatus = Literal[
    "pending",
    "approved",
    "processing",
    "succeeded",
    "failed",
    "rejected",
]


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


# ── Vendors ──


class Vendor(TypedDict, total=False):
    id: str
    externalId: Optional[str]
    name: str
    email: Optional[str]
    commissionRate: Optional[float]
    isActive: bool
    metadata: Optional[Dict[str, str]]
    createdAt: str
    updatedAt: str


class CreateVendorParams(TypedDict, total=False):
    name: str  # Required at runtime
    externalId: str
    email: str
    commissionRate: float
    metadata: Dict[str, str]


class UpdateVendorParams(TypedDict, total=False):
    name: str
    email: Optional[str]
    commissionRate: Optional[float]
    externalId: Optional[str]
    isActive: bool
    metadata: Dict[str, str]


class ListVendorsParams(TypedDict, total=False):
    page: int
    limit: int
    search: str
    isActive: bool


class VendorListResponse(TypedDict):
    data: List[Vendor]
    total: int
    page: int
    limit: int
    totalPages: int


# ── Customers ──


class Customer(TypedDict, total=False):
    id: str
    email: Optional[str]
    name: Optional[str]
    phone: Optional[str]
    createdAt: str
    transactionCount: int
    totalSpent: int


class ListCustomersParams(TypedDict, total=False):
    page: int
    pageSize: int
    search: str
    sortBy: str
    sortOrder: str


# ── API Keys ──


class ApiKey(TypedDict, total=False):
    id: str
    name: str
    type: str
    prefix: str
    publishableKey: str
    secretKey: str  # Only present on creation
    createdAt: str


class CreateApiKeyParams(TypedDict):
    name: str
    type: str  # "live" | "test"


# ── Webhooks Config ──

WebhookEventType = Literal[
    "payment.succeeded",
    "payment.failed",
    "payment.expired",
    "refund.created",
    "refund.updated",
]


class WebhookConfig(TypedDict, total=False):
    url: str
    secret: str
    events: List[str]


class UpdateWebhookConfigParams(TypedDict, total=False):
    url: str  # Required at runtime
    events: List[str]
