"""Checkout Sessions resource."""

from __future__ import annotations

from typing import Any, Optional

from ..http import async_http_request, http_request
from ..types import CheckoutSession, CreateCheckoutSessionParams


class _ConfigMixin:
    _secret_key: str
    _base_url: str
    _timeout: float
    _max_retries: int

    def _request_kwargs(self) -> dict[str, Any]:
        return {
            "secret_key": self._secret_key,
            "base_url": self._base_url,
            "timeout": self._timeout,
            "max_retries": self._max_retries,
        }


def _build_body(params: CreateCheckoutSessionParams) -> dict[str, Any]:
    body: dict[str, Any] = {
        "amount": params["amount"],
        "currency": params.get("currency", "MAD"),
        "success_url": params["success_url"],
        "cancel_url": params["cancel_url"],
    }
    for key in ("customer", "billing_address", "shipping_address", "line_items", "metadata"):
        if key in params:
            body[key] = params[key]  # type: ignore[literal-required]
    return body


class CheckoutSessions(_ConfigMixin):
    """Synchronous checkout sessions resource."""

    def __init__(self, secret_key: str, base_url: str, timeout: float, max_retries: int) -> None:
        self._secret_key = secret_key
        self._base_url = base_url
        self._timeout = timeout
        self._max_retries = max_retries

    def create(
        self,
        params: CreateCheckoutSessionParams,
        *,
        idempotency_key: Optional[str] = None,
    ) -> CheckoutSession:
        """Create a new checkout session.

        Args:
            params: Checkout session parameters including amount, success_url, cancel_url.
            idempotency_key: Optional idempotency key for safe retries.

        Returns:
            The created checkout session with a redirect URL.
        """
        headers: Optional[dict[str, str]] = None
        if idempotency_key:
            headers = {"Idempotency-Key": idempotency_key}

        return http_request(
            method="POST",
            path="/api/v1/checkout/sessions",
            body=_build_body(params),
            headers=headers,
            **self._request_kwargs(),
        )

    def retrieve(self, session_id: str) -> CheckoutSession:
        """Retrieve an existing checkout session by ID.

        Args:
            session_id: The checkout session identifier.

        Returns:
            The checkout session object.
        """
        from urllib.parse import quote

        return http_request(
            method="GET",
            path=f"/api/v1/checkout/sessions/{quote(session_id, safe='')}",
            **self._request_kwargs(),
        )


class AsyncCheckoutSessions(_ConfigMixin):
    """Asynchronous checkout sessions resource."""

    def __init__(self, secret_key: str, base_url: str, timeout: float, max_retries: int) -> None:
        self._secret_key = secret_key
        self._base_url = base_url
        self._timeout = timeout
        self._max_retries = max_retries

    async def create(
        self,
        params: CreateCheckoutSessionParams,
        *,
        idempotency_key: Optional[str] = None,
    ) -> CheckoutSession:
        """Create a new checkout session (async).

        Args:
            params: Checkout session parameters including amount, success_url, cancel_url.
            idempotency_key: Optional idempotency key for safe retries.

        Returns:
            The created checkout session with a redirect URL.
        """
        headers: Optional[dict[str, str]] = None
        if idempotency_key:
            headers = {"Idempotency-Key": idempotency_key}

        return await async_http_request(
            method="POST",
            path="/api/v1/checkout/sessions",
            body=_build_body(params),
            headers=headers,
            **self._request_kwargs(),
        )

    async def retrieve(self, session_id: str) -> CheckoutSession:
        """Retrieve an existing checkout session by ID (async).

        Args:
            session_id: The checkout session identifier.

        Returns:
            The checkout session object.
        """
        from urllib.parse import quote

        return await async_http_request(
            method="GET",
            path=f"/api/v1/checkout/sessions/{quote(session_id, safe='')}",
            **self._request_kwargs(),
        )
