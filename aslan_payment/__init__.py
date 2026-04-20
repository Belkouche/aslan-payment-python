"""Aslan Payment SDK for Python.

Server-side Python library for the Aslan Payment API.

Quick start::

    from aslan_payment import Aslan

    aslan = Aslan("sk_test_xxx")
    session = aslan.checkout_sessions.create({
        "amount": 5000,
        "success_url": "https://example.com/success",
        "cancel_url": "https://example.com/cancel",
    })
    print(session["url"])
"""

from .client import Aslan, AsyncAslan
from .errors import AslanError
from .types import (
    Address,
    ApiKey,
    BrowserInfo,
    CheckoutSession,
    CreateApiKeyParams,
    CreateCheckoutSessionParams,
    CreatePaymentLinkParams,
    CreateRefundParams,
    CreateVendorParams,
    Customer,
    CustomerParams,
    LineItem,
    ListCustomersParams,
    ListPaymentLinksParams,
    ListRefundsParams,
    ListTransactionsParams,
    ListVendorsParams,
    PaginatedResponse,
    Pagination,
    PaymentLink,
    PaymentLinkStatus,
    Refund,
    RefundStatus,
    SellerParams,
    ShippingAddress,
    Transaction,
    TransactionCustomer,
    TransactionStatus,
    UpdateVendorParams,
    UpdateWebhookConfigParams,
    Vendor,
    VendorListResponse,
    WebhookConfig,
    WebhookEvent,
    WebhookEventType,
)

__version__ = "0.2.0"

__all__ = [
    "Aslan",
    "AsyncAslan",
    "AslanError",
    # Types — checkout
    "Address",
    "BrowserInfo",
    "CheckoutSession",
    "CreateCheckoutSessionParams",
    "CustomerParams",
    "LineItem",
    "SellerParams",
    "ShippingAddress",
    # Types — transactions
    "ListTransactionsParams",
    "Transaction",
    "TransactionCustomer",
    "TransactionStatus",
    # Types — payment links
    "CreatePaymentLinkParams",
    "ListPaymentLinksParams",
    "PaymentLink",
    "PaymentLinkStatus",
    # Types — refunds
    "CreateRefundParams",
    "ListRefundsParams",
    "Refund",
    "RefundStatus",
    # Types — pagination
    "PaginatedResponse",
    "Pagination",
    # Types — vendors
    "CreateVendorParams",
    "ListVendorsParams",
    "UpdateVendorParams",
    "Vendor",
    "VendorListResponse",
    # Types — customers
    "Customer",
    "ListCustomersParams",
    # Types — api keys
    "ApiKey",
    "CreateApiKeyParams",
    # Types — webhooks
    "UpdateWebhookConfigParams",
    "WebhookConfig",
    "WebhookEvent",
    "WebhookEventType",
]
