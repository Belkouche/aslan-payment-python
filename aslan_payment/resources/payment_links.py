"""Payment Links resource."""

from __future__ import annotations

from typing import Any, Optional

from ..http import async_http_request, http_request
from ..types import CreatePaymentLinkParams, ListPaymentLinksParams, PaginatedResponse, PaymentLink


def _build_body(params: CreatePaymentLinkParams) -> dict[str, Any]:
    body: dict[str, Any] = {
        "amount": params["amount"],
        "currency": params.get("currency", "MAD"),
    }
    for key in ("description", "max_payments", "expires_at", "metadata"):
        if key in params:
            body[key] = params[key]  # type: ignore[literal-required]
    return body


def _build_query(params: Optional[ListPaymentLinksParams]) -> Optional[dict[str, Any]]:
    if not params:
        return None
    query: dict[str, Any] = {}
    if "page" in params:
        query["page"] = params["page"]
    if "page_size" in params:
        query["page_size"] = params["page_size"]
    if "status" in params:
        query["status"] = params["status"]
    return query or None


class PaymentLinks:
    """Synchronous payment links resource."""

    def __init__(self, secret_key: str, base_url: str, timeout: float, max_retries: int) -> None:
        self._secret_key = secret_key
        self._base_url = base_url
        self._timeout = timeout
        self._max_retries = max_retries

    def _request_kwargs(self) -> dict[str, Any]:
        return {
            "secret_key": self._secret_key,
            "base_url": self._base_url,
            "timeout": self._timeout,
            "max_retries": self._max_retries,
        }

    def create(
        self,
        params: CreatePaymentLinkParams,
        *,
        idempotency_key: Optional[str] = None,
    ) -> PaymentLink:
        """Create a new payment link.

        Args:
            params: Payment link parameters including amount.
            idempotency_key: Optional idempotency key for safe retries.

        Returns:
            The created payment link.
        """
        headers: Optional[dict[str, str]] = None
        if idempotency_key:
            headers = {"Idempotency-Key": idempotency_key}

        return http_request(
            method="POST",
            path="/api/v1/payment-links",
            body=_build_body(params),
            headers=headers,
            **self._request_kwargs(),
        )

    def retrieve(self, link_id: str) -> PaymentLink:
        """Retrieve a payment link by ID.

        Args:
            link_id: The payment link identifier.

        Returns:
            The payment link object.
        """
        from urllib.parse import quote

        return http_request(
            method="GET",
            path=f"/api/v1/payment-links/{quote(link_id, safe='')}",
            **self._request_kwargs(),
        )

    def list(self, params: Optional[ListPaymentLinksParams] = None) -> PaginatedResponse:
        """List payment links with optional filters.

        Args:
            params: Optional filtering and pagination parameters.

        Returns:
            Paginated list of payment links.
        """
        return http_request(
            method="GET",
            path="/api/v1/payment-links",
            query=_build_query(params),
            **self._request_kwargs(),
        )


class AsyncPaymentLinks:
    """Asynchronous payment links resource."""

    def __init__(self, secret_key: str, base_url: str, timeout: float, max_retries: int) -> None:
        self._secret_key = secret_key
        self._base_url = base_url
        self._timeout = timeout
        self._max_retries = max_retries

    def _request_kwargs(self) -> dict[str, Any]:
        return {
            "secret_key": self._secret_key,
            "base_url": self._base_url,
            "timeout": self._timeout,
            "max_retries": self._max_retries,
        }

    async def create(
        self,
        params: CreatePaymentLinkParams,
        *,
        idempotency_key: Optional[str] = None,
    ) -> PaymentLink:
        """Create a new payment link (async).

        Args:
            params: Payment link parameters including amount.
            idempotency_key: Optional idempotency key for safe retries.

        Returns:
            The created payment link.
        """
        headers: Optional[dict[str, str]] = None
        if idempotency_key:
            headers = {"Idempotency-Key": idempotency_key}

        return await async_http_request(
            method="POST",
            path="/api/v1/payment-links",
            body=_build_body(params),
            headers=headers,
            **self._request_kwargs(),
        )

    async def retrieve(self, link_id: str) -> PaymentLink:
        """Retrieve a payment link by ID (async).

        Args:
            link_id: The payment link identifier.

        Returns:
            The payment link object.
        """
        from urllib.parse import quote

        return await async_http_request(
            method="GET",
            path=f"/api/v1/payment-links/{quote(link_id, safe='')}",
            **self._request_kwargs(),
        )

    async def list(self, params: Optional[ListPaymentLinksParams] = None) -> PaginatedResponse:
        """List payment links with optional filters (async).

        Args:
            params: Optional filtering and pagination parameters.

        Returns:
            Paginated list of payment links.
        """
        return await async_http_request(
            method="GET",
            path="/api/v1/payment-links",
            query=_build_query(params),
            **self._request_kwargs(),
        )
