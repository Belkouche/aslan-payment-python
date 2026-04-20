"""Webhooks Config resource."""

from __future__ import annotations

from typing import Any, List, Optional

from ..http import async_http_request, http_request
from ..types import UpdateWebhookConfigParams, WebhookConfig


def _build_update_body(params: UpdateWebhookConfigParams) -> dict[str, Any]:
    body: dict[str, Any] = {"url": params["url"]}
    if "events" in params:
        body["events"] = params["events"]
    return body


class WebhooksConfig:
    """Synchronous webhooks configuration resource."""

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

    def retrieve(self) -> WebhookConfig:
        """Retrieve the current webhook configuration.

        Returns:
            The webhook configuration object containing ``url``, ``secret``,
            and ``events``.
        """
        return http_request(
            method="GET",
            path="/api/v1/webhooks/config",
            **self._request_kwargs(),
        )

    def update(self, params: UpdateWebhookConfigParams) -> WebhookConfig:
        """Create or replace the webhook configuration.

        Args:
            params: Webhook configuration parameters. ``url`` is required.
                ``events`` defaults to all event types when omitted.

        Returns:
            The updated webhook configuration object.
        """
        return http_request(
            method="POST",
            path="/api/v1/webhooks/config",
            body=_build_update_body(params),
            **self._request_kwargs(),
        )


class AsyncWebhooksConfig:
    """Asynchronous webhooks configuration resource."""

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

    async def retrieve(self) -> WebhookConfig:
        """Retrieve the current webhook configuration (async).

        Returns:
            The webhook configuration object containing ``url``, ``secret``,
            and ``events``.
        """
        return await async_http_request(
            method="GET",
            path="/api/v1/webhooks/config",
            **self._request_kwargs(),
        )

    async def update(self, params: UpdateWebhookConfigParams) -> WebhookConfig:
        """Create or replace the webhook configuration (async).

        Args:
            params: Webhook configuration parameters. ``url`` is required.
                ``events`` defaults to all event types when omitted.

        Returns:
            The updated webhook configuration object.
        """
        return await async_http_request(
            method="POST",
            path="/api/v1/webhooks/config",
            body=_build_update_body(params),
            **self._request_kwargs(),
        )
