"""Transactions resource."""

from __future__ import annotations

from typing import Any, Optional

from ..http import async_http_request, http_request
from ..types import ListTransactionsParams, PaginatedResponse, Transaction


def _build_query(params: Optional[ListTransactionsParams]) -> Optional[dict[str, Any]]:
    if not params:
        return None
    query: dict[str, Any] = {}
    if "page" in params:
        query["page"] = params["page"]
    if "page_size" in params:
        query["page_size"] = params["page_size"]
    if "status" in params:
        query["status"] = params["status"]
    if "from_date" in params:
        query["from"] = params["from_date"]
    if "to_date" in params:
        query["to"] = params["to_date"]
    if "sort_by" in params:
        query["sort_by"] = params["sort_by"]
    if "sort_order" in params:
        query["sort_order"] = params["sort_order"]
    return query or None


class Transactions:
    """Synchronous transactions resource."""

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

    def retrieve(self, transaction_id: str) -> Transaction:
        """Retrieve a transaction by ID.

        Args:
            transaction_id: The transaction identifier.

        Returns:
            The transaction object.
        """
        from urllib.parse import quote

        return http_request(
            method="GET",
            path=f"/api/v1/transactions/{quote(transaction_id, safe='')}",
            **self._request_kwargs(),
        )

    def list(self, params: Optional[ListTransactionsParams] = None) -> PaginatedResponse:
        """List transactions with optional filters.

        Args:
            params: Optional filtering, sorting, and pagination parameters.

        Returns:
            Paginated list of transactions.
        """
        return http_request(
            method="GET",
            path="/api/v1/transactions",
            query=_build_query(params),
            **self._request_kwargs(),
        )


class AsyncTransactions:
    """Asynchronous transactions resource."""

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

    async def retrieve(self, transaction_id: str) -> Transaction:
        """Retrieve a transaction by ID (async).

        Args:
            transaction_id: The transaction identifier.

        Returns:
            The transaction object.
        """
        from urllib.parse import quote

        return await async_http_request(
            method="GET",
            path=f"/api/v1/transactions/{quote(transaction_id, safe='')}",
            **self._request_kwargs(),
        )

    async def list(self, params: Optional[ListTransactionsParams] = None) -> PaginatedResponse:
        """List transactions with optional filters (async).

        Args:
            params: Optional filtering, sorting, and pagination parameters.

        Returns:
            Paginated list of transactions.
        """
        return await async_http_request(
            method="GET",
            path="/api/v1/transactions",
            query=_build_query(params),
            **self._request_kwargs(),
        )
