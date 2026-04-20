"""API Keys resource."""

from __future__ import annotations

from typing import Any, List, Optional
from urllib.parse import quote

from ..http import async_http_request, http_request
from ..types import ApiKey, CreateApiKeyParams


class ApiKeys:
    """Synchronous API keys resource."""

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
        params: CreateApiKeyParams,
        *,
        idempotency_key: Optional[str] = None,
    ) -> ApiKey:
        """Create a new API key.

        Args:
            params: API key parameters. Both ``name`` and ``type`` are required.
                ``type`` must be ``"live"`` or ``"test"``.
            idempotency_key: Optional idempotency key for safe retries.

        Returns:
            The created API key object. ``secretKey`` is only present on creation.
        """
        headers: Optional[dict[str, str]] = None
        if idempotency_key:
            headers = {"Idempotency-Key": idempotency_key}

        return http_request(
            method="POST",
            path="/api/v1/api-keys",
            body={"name": params["name"], "type": params["type"]},
            headers=headers,
            **self._request_kwargs(),
        )

    def list(self) -> List[ApiKey]:
        """List all API keys for the current merchant.

        Returns:
            List of API key objects (``secretKey`` is never returned in list).
        """
        return http_request(
            method="GET",
            path="/api/v1/api-keys",
            **self._request_kwargs(),
        )

    def delete(self, key_id: str) -> None:
        """Delete (revoke) an API key.

        Args:
            key_id: The API key identifier.
        """
        http_request(
            method="DELETE",
            path=f"/api/v1/api-keys/{quote(key_id, safe='')}",
            **self._request_kwargs(),
        )


class AsyncApiKeys:
    """Asynchronous API keys resource."""

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
        params: CreateApiKeyParams,
        *,
        idempotency_key: Optional[str] = None,
    ) -> ApiKey:
        """Create a new API key (async).

        Args:
            params: API key parameters. Both ``name`` and ``type`` are required.
                ``type`` must be ``"live"`` or ``"test"``.
            idempotency_key: Optional idempotency key for safe retries.

        Returns:
            The created API key object. ``secretKey`` is only present on creation.
        """
        headers: Optional[dict[str, str]] = None
        if idempotency_key:
            headers = {"Idempotency-Key": idempotency_key}

        return await async_http_request(
            method="POST",
            path="/api/v1/api-keys",
            body={"name": params["name"], "type": params["type"]},
            headers=headers,
            **self._request_kwargs(),
        )

    async def list(self) -> List[ApiKey]:
        """List all API keys for the current merchant (async).

        Returns:
            List of API key objects (``secretKey`` is never returned in list).
        """
        return await async_http_request(
            method="GET",
            path="/api/v1/api-keys",
            **self._request_kwargs(),
        )

    async def delete(self, key_id: str) -> None:
        """Delete (revoke) an API key (async).

        Args:
            key_id: The API key identifier.
        """
        await async_http_request(
            method="DELETE",
            path=f"/api/v1/api-keys/{quote(key_id, safe='')}",
            **self._request_kwargs(),
        )
