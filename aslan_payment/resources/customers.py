"""Customers resource."""

from __future__ import annotations

from typing import Any, Optional
from urllib.parse import quote

from ..http import async_http_request, http_request
from ..types import Customer, ListCustomersParams, PaginatedResponse


def _build_query(params: Optional[ListCustomersParams]) -> Optional[dict[str, Any]]:
    if not params:
        return None
    query: dict[str, Any] = {}
    for key in ("page", "pageSize", "search", "sortBy", "sortOrder"):
        if key in params:
            query[key] = params[key]  # type: ignore[literal-required]
    return query or None


class Customers:
    """Synchronous customers resource."""

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

    def list(self, params: Optional[ListCustomersParams] = None) -> PaginatedResponse:
        """List customers with optional filters.

        Args:
            params: Optional filtering and pagination parameters.

        Returns:
            Paginated list of customers.
        """
        return http_request(
            method="GET",
            path="/api/v1/customers",
            query=_build_query(params),
            **self._request_kwargs(),
        )

    def retrieve(self, customer_id: str) -> Customer:
        """Retrieve a customer by ID.

        Args:
            customer_id: The customer identifier.

        Returns:
            The customer object.
        """
        return http_request(
            method="GET",
            path=f"/api/v1/customers/{quote(customer_id, safe='')}",
            **self._request_kwargs(),
        )


class AsyncCustomers:
    """Asynchronous customers resource."""

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

    async def list(self, params: Optional[ListCustomersParams] = None) -> PaginatedResponse:
        """List customers with optional filters (async).

        Args:
            params: Optional filtering and pagination parameters.

        Returns:
            Paginated list of customers.
        """
        return await async_http_request(
            method="GET",
            path="/api/v1/customers",
            query=_build_query(params),
            **self._request_kwargs(),
        )

    async def retrieve(self, customer_id: str) -> Customer:
        """Retrieve a customer by ID (async).

        Args:
            customer_id: The customer identifier.

        Returns:
            The customer object.
        """
        return await async_http_request(
            method="GET",
            path=f"/api/v1/customers/{quote(customer_id, safe='')}",
            **self._request_kwargs(),
        )
