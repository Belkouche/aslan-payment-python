# Aslan Payment SDK for Python

Server-side Python library for the [Aslan Payment API](https://doc.aslanpay.ma).

## Installation

```bash
pip install git+https://github.com/Belkouche/aslan-payment-python.git
```

## Quick Start

```python
from aslan_payment import Aslan

aslan = Aslan("sk_test_xxx")

# Create a checkout session
session = aslan.checkout_sessions.create({
    "amount": 5000,        # 50.00 MAD (amount in centimes)
    "success_url": "https://example.com/success",
    "cancel_url": "https://example.com/cancel",
})

# Redirect customer to the payment page
print(session["url"])
```

## Configuration

```python
from aslan_payment import Aslan

aslan = Aslan(
    "sk_live_xxx",
    base_url="https://api.aslanpay.ma/pay",  # default
    timeout=30,                                # seconds, default
    max_retries=2,                             # default
)

# Check if using test mode
if aslan.is_test_mode:
    print("Running in test mode")
```

## Naming conventions

- **Request params** use snake_case keys (`success_url`, `line_items`, `page_size`, ...). The SDK
  converts them to the API's camelCase on the wire; camelCase keys (`successUrl`) are accepted too.
  `metadata` dicts are sent verbatim (your keys are never renamed).
- **Responses** are returned exactly as the API sends them, so their keys are **camelCase**
  (`expiresAt`, `createdAt`, `providerAccount`, `pagination.totalPages`, ...).
  Single objects come back unwrapped; list methods return `{"data": [...], "pagination": {...}}`.

## Resources

### Checkout Sessions

```python
# Create a checkout session
session = aslan.checkout_sessions.create({
    "amount": 5000,
    "success_url": "https://example.com/success",
    "cancel_url": "https://example.com/cancel",
    "customer": {
        "email": "customer@example.com",
        "name": "Ahmed Benali",
        "phone": "+212600000004",
    },
    "line_items": [
        {
            "name": "Widget",
            "quantity": 2,
            "unit_price": 2500,
        },
    ],
    "metadata": {
        "order_id": "order_123",
    },
})

# With idempotency key (safe to retry)
session = aslan.checkout_sessions.create(
    {"amount": 5000, "success_url": "...", "cancel_url": "..."},
    idempotency_key="unique-key-123",
)

# Process on an additional PSP account (alias); omit or "default" for the default account.
# Also supported by payment_links.create. Responses carry "providerAccount".
session = aslan.checkout_sessions.create(
    {"amount": 5000, "success_url": "...", "cancel_url": "...", "providerAccount": "foreign"},
)

# Retrieve a checkout session
session = aslan.checkout_sessions.retrieve("cs_xxx")
```

### Transactions

```python
# Retrieve a transaction
transaction = aslan.transactions.retrieve("txn_xxx")

# List transactions with filters
result = aslan.transactions.list({
    "page": 1,
    "page_size": 20,
    "status": "succeeded",
    "from_date": "2025-01-01T00:00:00Z",
    "to_date": "2025-12-31T23:59:59Z",
    "sort_by": "created_at",                  # sent as sortBy=createdAt
    "sort_order": "desc",
})

for txn in result["data"]:
    print(f"{txn['id']}: {txn['amount']} {txn['currency']}")

print(f"Page {result['pagination']['page']} of {result['pagination']['totalPages']}")
```

### Payment Links

```python
# Create a payment link
link = aslan.payment_links.create({
    "amount": 10000,
    "description": "Invoice #456",
    "max_payments": 1,
    "metadata": {"invoice_id": "inv_456"},
})
print(link["url"])

# Retrieve a payment link
link = aslan.payment_links.retrieve("pl_xxx")

# QR code: {"dataUri", "mimeType"} by default, raw image bytes when a format is given
qr = aslan.payment_links.get_qr("pl_xxx")
svg_bytes = aslan.payment_links.get_qr("pl_xxx", {"format": "svg"})

# List payment links
result = aslan.payment_links.list({
    "page": 1,
    "page_size": 10,
    "status": "active",
})
```

### Refunds

```python
# Create a full refund
refund = aslan.refunds.create({
    "transaction_id": "txn_xxx",
    "amount": 5000,
    "reason": "Customer requested refund",
})

# Retrieve a refund
refund = aslan.refunds.retrieve("ref_xxx")
```

### Webhook Verification

```python
from aslan_payment import Aslan

webhooks = Aslan.webhooks("whsec_xxx")

# In your webhook handler (e.g., Flask / Django / FastAPI)
def handle_webhook(request):
    payload = request.body  # raw body as string or bytes
    signature = request.headers["Aslan-Signature"]

    try:
        event = webhooks.verify(payload, signature)
    except Exception as e:
        return {"error": str(e)}, 400

    if event["event"] == "payment.succeeded":
        transaction = event["data"]["transaction"]
        # Fulfill the order
        print(f"Payment succeeded: {transaction['id']}")

    return {"received": True}, 200
```

## Error Handling

```python
from aslan_payment import Aslan, AslanError

aslan = Aslan("sk_test_xxx")

try:
    session = aslan.checkout_sessions.retrieve("cs_nonexistent")
except AslanError as e:
    print(f"Code: {e.code}")            # e.g., "NOT_FOUND"
    print(f"Message: {e.message}")       # Human-readable message
    print(f"Status: {e.http_status}")    # e.g., 404
    print(f"Request ID: {e.request_id}") # For support inquiries
    print(f"Details: {e.details}")       # Additional error info
```

Every non-2xx response raises `AslanError` (including HTML error pages from a proxy).

### Error Codes

| Code | Description |
|------|-------------|
| `AUTHENTICATION_ERROR` | Invalid or missing API key |
| `AUTHORIZATION_ERROR` | Insufficient permissions |
| `VALIDATION_ERROR` | Invalid request parameters |
| `NOT_FOUND` | Resource not found |
| `RATE_LIMITED` | Too many requests |
| `IDEMPOTENCY_ERROR` | Idempotency key conflict |
| `NETWORK_ERROR` | Connection or timeout error |
| `SERVER_ERROR` | Aslan API server error (5xx) |
| `PROVIDER_ACCOUNT_NOT_FOUND` | `providerAccount` names no account of your merchant |
| `PROVIDER_ACCOUNT_INACTIVE` | The `providerAccount` is deactivated |
| `PROVIDER_ACCOUNT_UNSUPPORTED` | The account's provider cannot take this request |
| `PROVIDER_ACCOUNT_RECURRING_DISABLED` | The account does not allow recurring payments |

## Async Usage

The SDK provides a fully async client powered by `httpx`:

```python
import asyncio
from aslan_payment import AsyncAslan

async def main():
    aslan = AsyncAslan("sk_test_xxx")

    session = await aslan.checkout_sessions.create({
        "amount": 5000,
        "success_url": "https://example.com/success",
        "cancel_url": "https://example.com/cancel",
    })
    print(session["url"])

    # All resources support async
    txn = await aslan.transactions.retrieve("txn_xxx")
    links = await aslan.payment_links.list()
    refund = await aslan.refunds.create({
        "transaction_id": "txn_xxx",
        "amount": 5000,
    })

asyncio.run(main())
```

## Types Reference

The SDK ships with full type annotations (PEP 561 compatible). All parameter and return types are available as `TypedDict` imports:

```python
from aslan_payment import (
    # Parameter types
    CreateCheckoutSessionParams,
    CreatePaymentLinkParams,
    CreateRefundParams,
    ListTransactionsParams,
    ListPaymentLinksParams,
    CustomerParams,
    Address,
    ShippingAddress,
    LineItem,

    # Response types
    CheckoutSession,
    Transaction,
    PaymentLink,
    Refund,
    PaginatedResponse,
    WebhookEvent,

    # Literal types
    TransactionStatus,
    PaymentLinkStatus,
    RefundStatus,
)
```

## Security

- API keys are sent via the `Authorization: Bearer` header over HTTPS.
- Never expose your secret key in client-side code. This SDK is for server-side use only.
- Webhook signatures use HMAC-SHA256 with timing-safe comparison to prevent timing attacks.
- The SDK automatically retries on 5xx errors and network failures with exponential backoff.

## Requirements

- Python >= 3.9
- httpx >= 0.24.0

## License

MIT -- Copyright (c) 2025 Aslan
