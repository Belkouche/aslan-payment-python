"""Aslan Payment SDK client."""

from __future__ import annotations

from typing import Optional

from .errors import AslanError
from .resources.api_keys import ApiKeys, AsyncApiKeys
from .resources.checkout_sessions import AsyncCheckoutSessions, CheckoutSessions
from .resources.customers import AsyncCustomers, Customers
from .resources.payment_links import AsyncPaymentLinks, PaymentLinks
from .resources.refunds import AsyncRefunds, Refunds
from .resources.transactions import AsyncTransactions, Transactions
from .resources.vendors import AsyncVendors, Vendors
from .resources.webhooks import Webhooks
from .resources.webhooks_config import AsyncWebhooksConfig, WebhooksConfig

_DEFAULT_BASE_URL = "https://api.aslanpay.ma/pay"
_DEFAULT_TIMEOUT = 30.0
_DEFAULT_MAX_RETRIES = 2


class Aslan:
    """Synchronous Aslan Payment API client.

    Args:
        secret_key: Your Aslan secret API key (must start with ``sk_live_`` or ``sk_test_``).
        base_url: API base URL. Defaults to ``https://api.aslanpay.ma/pay``.
        timeout: Request timeout in seconds. Defaults to 30.
        max_retries: Maximum retries on 5xx/network errors. Defaults to 2.

    Raises:
        AslanError: If the secret key format is invalid.

    Example::

        from aslan_payment import Aslan

        aslan = Aslan("sk_test_xxx")
        session = aslan.checkout_sessions.create({
            "amount": 5000,
            "success_url": "https://example.com/success",
            "cancel_url": "https://example.com/cancel",
        })
        print(session["url"])
    """

    checkout_sessions: CheckoutSessions
    transactions: Transactions
    payment_links: PaymentLinks
    refunds: Refunds
    vendors: Vendors
    customers: Customers
    api_keys: ApiKeys
    webhooks_config: WebhooksConfig

    def __init__(
        self,
        secret_key: str,
        *,
        base_url: Optional[str] = None,
        timeout: float = _DEFAULT_TIMEOUT,
        max_retries: int = _DEFAULT_MAX_RETRIES,
    ) -> None:
        if not secret_key.startswith("sk_live_") and not secret_key.startswith("sk_test_"):
            raise AslanError(
                "AUTHENTICATION_ERROR",
                "Invalid secret key format. Must start with sk_live_ or sk_test_",
            )

        self._secret_key = secret_key
        self._base_url = base_url or _DEFAULT_BASE_URL
        self._timeout = timeout
        self._max_retries = max_retries

        args = (self._secret_key, self._base_url, self._timeout, self._max_retries)
        self.checkout_sessions = CheckoutSessions(*args)
        self.transactions = Transactions(*args)
        self.payment_links = PaymentLinks(*args)
        self.refunds = Refunds(*args)
        self.vendors = Vendors(*args)
        self.customers = Customers(*args)
        self.api_keys = ApiKeys(*args)
        self.webhooks_config = WebhooksConfig(*args)

    @property
    def is_test_mode(self) -> bool:
        """Whether the client is using a test mode secret key."""
        return self._secret_key.startswith("sk_test_")

    @staticmethod
    def webhooks(webhook_secret: str) -> Webhooks:
        """Create a Webhooks instance for signature verification.

        Args:
            webhook_secret: Your webhook signing secret.

        Returns:
            A Webhooks instance.
        """
        return Webhooks(webhook_secret)


class AsyncAslan:
    """Asynchronous Aslan Payment API client.

    Provides the same API surface as :class:`Aslan` but with ``async``/``await`` methods.

    Args:
        secret_key: Your Aslan secret API key (must start with ``sk_live_`` or ``sk_test_``).
        base_url: API base URL. Defaults to ``https://api.aslanpay.ma/pay``.
        timeout: Request timeout in seconds. Defaults to 30.
        max_retries: Maximum retries on 5xx/network errors. Defaults to 2.

    Example::

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

        asyncio.run(main())
    """

    checkout_sessions: AsyncCheckoutSessions
    transactions: AsyncTransactions
    payment_links: AsyncPaymentLinks
    refunds: AsyncRefunds
    vendors: AsyncVendors
    customers: AsyncCustomers
    api_keys: AsyncApiKeys
    webhooks_config: AsyncWebhooksConfig

    def __init__(
        self,
        secret_key: str,
        *,
        base_url: Optional[str] = None,
        timeout: float = _DEFAULT_TIMEOUT,
        max_retries: int = _DEFAULT_MAX_RETRIES,
    ) -> None:
        if not secret_key.startswith("sk_live_") and not secret_key.startswith("sk_test_"):
            raise AslanError(
                "AUTHENTICATION_ERROR",
                "Invalid secret key format. Must start with sk_live_ or sk_test_",
            )

        self._secret_key = secret_key
        self._base_url = base_url or _DEFAULT_BASE_URL
        self._timeout = timeout
        self._max_retries = max_retries

        args = (self._secret_key, self._base_url, self._timeout, self._max_retries)
        self.checkout_sessions = AsyncCheckoutSessions(*args)
        self.transactions = AsyncTransactions(*args)
        self.payment_links = AsyncPaymentLinks(*args)
        self.refunds = AsyncRefunds(*args)
        self.vendors = AsyncVendors(*args)
        self.customers = AsyncCustomers(*args)
        self.api_keys = AsyncApiKeys(*args)
        self.webhooks_config = AsyncWebhooksConfig(*args)

    @property
    def is_test_mode(self) -> bool:
        """Whether the client is using a test mode secret key."""
        return self._secret_key.startswith("sk_test_")

    @staticmethod
    def webhooks(webhook_secret: str) -> Webhooks:
        """Create a Webhooks instance for signature verification.

        Args:
            webhook_secret: Your webhook signing secret.

        Returns:
            A Webhooks instance.
        """
        return Webhooks(webhook_secret)
