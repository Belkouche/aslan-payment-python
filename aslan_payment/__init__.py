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
    CheckoutSession,
    CreateCheckoutSessionParams,
    CreatePaymentLinkParams,
    CreateRefundParams,
    CustomerParams,
    LineItem,
    ListPaymentLinksParams,
    ListTransactionsParams,
    PaginatedResponse,
    Pagination,
    PaymentLink,
    PaymentLinkStatus,
    Refund,
    RefundStatus,
    ShippingAddress,
    Transaction,
    TransactionCustomer,
    TransactionStatus,
    WebhookEvent,
)

__version__ = "0.1.0"

__all__ = [
    "Aslan",
    "AsyncAslan",
    "AslanError",
    # Types
    "Address",
    "CheckoutSession",
    "CreateCheckoutSessionParams",
    "CreatePaymentLinkParams",
    "CreateRefundParams",
    "CustomerParams",
    "LineItem",
    "ListPaymentLinksParams",
    "ListTransactionsParams",
    "PaginatedResponse",
    "Pagination",
    "PaymentLink",
    "PaymentLinkStatus",
    "Refund",
    "RefundStatus",
    "ShippingAddress",
    "Transaction",
    "TransactionCustomer",
    "TransactionStatus",
    "WebhookEvent",
]
