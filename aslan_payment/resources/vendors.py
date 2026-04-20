"""Vendors resource."""

from __future__ import annotations

from typing import Any, Optional
from urllib.parse import quote

from ..http import async_http_request, http_request
from ..types import (
    CreateVendorParams,
    ListVendorsParams,
    UpdateVendorParams,
    Vendor,
    VendorListResponse,
)


def _build_create_body(params: CreateVendorParams) -> dict[str, Any]:
    body: dict[str, Any] = {"name": params["name"]}
    for key in ("externalId", "email", "commissionRate", "metadata"):
        if key in params:
            body[key] = params[key]  # type: ignore[literal-required]
    return body


def _build_update_body(params: UpdateVendorParams) -> dict[str, Any]:
    body: dict[str, Any] = {}
    for key in ("name", "email", "commissionRate", "externalId", "isActive", "metadata"):
        if key in params:
            body[key] = params[key]  # type: ignore[literal-required]
    return body


def _build_query(params: Optional[ListVendorsParams]) -> Optional[dict[str, Any]]:
    if not params:
        return None
    query: dict[str, Any] = {}
    for key in ("page", "limit", "search", "isActive"):
        if key in params:
            query[key] = params[key]  # type: ignore[literal-required]
    return query or None


class Vendors:
    """Synchronous vendors resource."""

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
        params: CreateVendorParams,
        *,
        idempotency_key: Optional[str] = None,
    ) -> Vendor:
        """Create a new vendor.

        Args:
            params: Vendor parameters. ``name`` is required.
            idempotency_key: Optional idempotency key for safe retries.

        Returns:
            The created vendor object.
        """
        headers: Optional[dict[str, str]] = None
        if idempotency_key:
            headers = {"Idempotency-Key": idempotency_key}

        return http_request(
            method="POST",
            path="/api/v1/vendors",
            body=_build_create_body(params),
            headers=headers,
            **self._request_kwargs(),
        )

    def retrieve(self, vendor_id: str) -> Vendor:
        """Retrieve a vendor by ID.

        Args:
            vendor_id: The vendor identifier.

        Returns:
            The vendor object.
        """
        return http_request(
            method="GET",
            path=f"/api/v1/vendors/{quote(vendor_id, safe='')}",
            **self._request_kwargs(),
        )

    def list(self, params: Optional[ListVendorsParams] = None) -> VendorListResponse:
        """List vendors with optional filters.

        Args:
            params: Optional filtering and pagination parameters.

        Returns:
            Paginated list of vendors with ``data``, ``total``, ``page``, ``limit``,
            and ``totalPages`` fields.
        """
        return http_request(
            method="GET",
            path="/api/v1/vendors",
            query=_build_query(params),
            **self._request_kwargs(),
        )

    def update(self, vendor_id: str, params: UpdateVendorParams) -> Vendor:
        """Update a vendor.

        Args:
            vendor_id: The vendor identifier.
            params: Fields to update.

        Returns:
            The updated vendor object.
        """
        return http_request(
            method="PATCH",
            path=f"/api/v1/vendors/{quote(vendor_id, safe='')}",
            body=_build_update_body(params),
            **self._request_kwargs(),
        )

    def delete(self, vendor_id: str) -> None:
        """Delete a vendor.

        Args:
            vendor_id: The vendor identifier.
        """
        http_request(
            method="DELETE",
            path=f"/api/v1/vendors/{quote(vendor_id, safe='')}",
            **self._request_kwargs(),
        )


class AsyncVendors:
    """Asynchronous vendors resource."""

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
        params: CreateVendorParams,
        *,
        idempotency_key: Optional[str] = None,
    ) -> Vendor:
        """Create a new vendor (async).

        Args:
            params: Vendor parameters. ``name`` is required.
            idempotency_key: Optional idempotency key for safe retries.

        Returns:
            The created vendor object.
        """
        headers: Optional[dict[str, str]] = None
        if idempotency_key:
            headers = {"Idempotency-Key": idempotency_key}

        return await async_http_request(
            method="POST",
            path="/api/v1/vendors",
            body=_build_create_body(params),
            headers=headers,
            **self._request_kwargs(),
        )

    async def retrieve(self, vendor_id: str) -> Vendor:
        """Retrieve a vendor by ID (async).

        Args:
            vendor_id: The vendor identifier.

        Returns:
            The vendor object.
        """
        return await async_http_request(
            method="GET",
            path=f"/api/v1/vendors/{quote(vendor_id, safe='')}",
            **self._request_kwargs(),
        )

    async def list(self, params: Optional[ListVendorsParams] = None) -> VendorListResponse:
        """List vendors with optional filters (async).

        Args:
            params: Optional filtering and pagination parameters.

        Returns:
            Paginated list of vendors with ``data``, ``total``, ``page``, ``limit``,
            and ``totalPages`` fields.
        """
        return await async_http_request(
            method="GET",
            path="/api/v1/vendors",
            query=_build_query(params),
            **self._request_kwargs(),
        )

    async def update(self, vendor_id: str, params: UpdateVendorParams) -> Vendor:
        """Update a vendor (async).

        Args:
            vendor_id: The vendor identifier.
            params: Fields to update.

        Returns:
            The updated vendor object.
        """
        return await async_http_request(
            method="PATCH",
            path=f"/api/v1/vendors/{quote(vendor_id, safe='')}",
            body=_build_update_body(params),
            **self._request_kwargs(),
        )

    async def delete(self, vendor_id: str) -> None:
        """Delete a vendor (async).

        Args:
            vendor_id: The vendor identifier.
        """
        await async_http_request(
            method="DELETE",
            path=f"/api/v1/vendors/{quote(vendor_id, safe='')}",
            **self._request_kwargs(),
        )
