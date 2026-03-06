"""Refunds resource."""

from __future__ import annotations

from typing import Any, Optional

from ..http import async_http_request, http_request
from ..types import CreateRefundParams, Refund


def _build_body(params: CreateRefundParams) -> dict[str, Any]:
    body: dict[str, Any] = {
        "transaction_id": params["transaction_id"],
        "amount": params["amount"],
    }
    if "reason" in params:
        body["reason"] = params["reason"]
    return body


class Refunds:
    """Synchronous refunds resource."""

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
        params: CreateRefundParams,
        *,
        idempotency_key: Optional[str] = None,
    ) -> Refund:
        """Create a refund for a transaction.

        Args:
            params: Refund parameters including transaction_id and amount.
            idempotency_key: Optional idempotency key for safe retries.

        Returns:
            The created refund object.
        """
        headers: Optional[dict[str, str]] = None
        if idempotency_key:
            headers = {"Idempotency-Key": idempotency_key}

        return http_request(
            method="POST",
            path="/api/v1/refunds",
            body=_build_body(params),
            headers=headers,
            **self._request_kwargs(),
        )

    def retrieve(self, refund_id: str) -> Refund:
        """Retrieve a refund by ID.

        Args:
            refund_id: The refund identifier.

        Returns:
            The refund object.
        """
        from urllib.parse import quote

        return http_request(
            method="GET",
            path=f"/api/v1/refunds/{quote(refund_id, safe='')}",
            **self._request_kwargs(),
        )


class AsyncRefunds:
    """Asynchronous refunds resource."""

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
        params: CreateRefundParams,
        *,
        idempotency_key: Optional[str] = None,
    ) -> Refund:
        """Create a refund for a transaction (async).

        Args:
            params: Refund parameters including transaction_id and amount.
            idempotency_key: Optional idempotency key for safe retries.

        Returns:
            The created refund object.
        """
        headers: Optional[dict[str, str]] = None
        if idempotency_key:
            headers = {"Idempotency-Key": idempotency_key}

        return await async_http_request(
            method="POST",
            path="/api/v1/refunds",
            body=_build_body(params),
            headers=headers,
            **self._request_kwargs(),
        )

    async def retrieve(self, refund_id: str) -> Refund:
        """Retrieve a refund by ID (async).

        Args:
            refund_id: The refund identifier.

        Returns:
            The refund object.
        """
        from urllib.parse import quote

        return await async_http_request(
            method="GET",
            path=f"/api/v1/refunds/{quote(refund_id, safe='')}",
            **self._request_kwargs(),
        )
