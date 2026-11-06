"""HTTP client with automatic retries and error mapping."""

from __future__ import annotations

import time
from typing import Any, Optional

import httpx

from .errors import AslanError, AslanErrorCode

_SDK_VERSION = "0.1.0"
_USER_AGENT = f"aslan-payment-python/{_SDK_VERSION}"

_RETRYABLE_STATUS_CODES = frozenset({408, 429, 500, 502, 503, 504})


def _map_error_code(status: int, server_code: Optional[str] = None) -> AslanErrorCode:
    if server_code == "VALIDATION_ERROR":
        return "VALIDATION_ERROR"
    if server_code == "IDEMPOTENCY_ERROR":
        return "IDEMPOTENCY_ERROR"
    if server_code is not None and server_code.startswith("PROVIDER_ACCOUNT_"):
        return server_code  # type: ignore[return-value]
    mapping: dict[int, AslanErrorCode] = {
        401: "AUTHENTICATION_ERROR",
        403: "AUTHORIZATION_ERROR",
        404: "NOT_FOUND",
        409: "IDEMPOTENCY_ERROR",
        422: "VALIDATION_ERROR",
        429: "RATE_LIMITED",
    }
    if status in mapping:
        return mapping[status]
    return "SERVER_ERROR" if status >= 500 else "VALIDATION_ERROR"


def _build_headers(
    secret_key: str,
    extra: Optional[dict[str, str]] = None,
) -> dict[str, str]:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {secret_key}",
        "User-Agent": _USER_AGENT,
    }
    if extra:
        headers.update(extra)
    return headers


def _handle_error_response(response: httpx.Response, request_id: Optional[str]) -> None:
    """Raise an AslanError for any non-2xx response.

    Accepts the flat shape ``{statusCode, code, error, message, details?}`` and the
    nested shape ``{error: {code, message, details?}}``.
    """
    status = response.status_code
    default_message = f"Request failed with status {status}"
    try:
        body: Any = response.json()
    except Exception:
        body = None

    source: dict[str, Any] = {}
    fallback_message: Optional[str] = None
    if isinstance(body, dict):
        nested = body.get("error")
        if isinstance(nested, dict):
            source = nested
        else:
            source = body
            if isinstance(nested, str):
                fallback_message = nested  # e.g. "Unauthorized"

    server_code = source.get("code")
    message = source.get("message")
    if not isinstance(message, str) or not message:
        message = fallback_message or (
            default_message if body is not None else f"Unexpected response from server ({status})"
        )
    raise AslanError(
        _map_error_code(status, server_code if isinstance(server_code, str) else None),
        message,
        http_status=status,
        details=source.get("details"),
        request_id=request_id,
    )


def _query_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _parse_success(response: httpx.Response) -> Any:
    """Decode a 2xx response, unwrapping the ``{"data": X}`` single-object envelope.

    List responses (``{data, pagination}``) and unwrapped objects are returned as-is.
    Non-JSON bodies (e.g. a raw QR image) are returned as bytes.
    """
    if response.status_code == 204 or not response.content:
        return None
    if "json" not in response.headers.get("content-type", "application/json"):
        return response.content
    try:
        body = response.json()
    except ValueError:
        raise AslanError(
            "SERVER_ERROR",
            f"Invalid JSON in response ({response.status_code})",
            http_status=response.status_code,
            request_id=response.headers.get("x-request-id"),
        )
    if isinstance(body, dict) and len(body) == 1 and "data" in body:
        return body["data"]
    return body


def http_request(
    *,
    method: str,
    path: str,
    secret_key: str,
    base_url: str,
    timeout: float,
    max_retries: int,
    body: Optional[dict[str, Any]] = None,
    query: Optional[dict[str, Any]] = None,
    headers: Optional[dict[str, str]] = None,
) -> Any:
    """Synchronous HTTP request with exponential backoff retries."""
    url = base_url.rstrip("/") + path
    request_headers = _build_headers(secret_key, headers)

    # Filter out None values from query params
    params: Optional[dict[str, str]] = None
    if query:
        params = {k: _query_value(v) for k, v in query.items() if v is not None}

    # Filter out None values from body
    json_body: Optional[dict[str, Any]] = None
    if body is not None:
        json_body = {k: v for k, v in body.items() if v is not None}

    last_error: Optional[AslanError] = None

    for attempt in range(max_retries + 1):
        if attempt > 0:
            delay = min(0.5 * (2 ** (attempt - 1)), 5.0)
            time.sleep(delay)

        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.request(
                    method,
                    url,
                    headers=request_headers,
                    params=params,
                    json=json_body if method != "GET" else None,
                )

            request_id = response.headers.get("x-request-id")

            if response.status_code in _RETRYABLE_STATUS_CODES and attempt < max_retries:
                last_error = AslanError(
                    "SERVER_ERROR",
                    f"Request failed with status {response.status_code}",
                    http_status=response.status_code,
                    request_id=request_id,
                )
                continue

            if not response.is_success:
                _handle_error_response(response, request_id)

            return _parse_success(response)

        except AslanError:
            raise
        except httpx.TimeoutException:
            last_error = AslanError("NETWORK_ERROR", "Request timed out")
            if attempt < max_retries:
                continue
        except httpx.HTTPError as exc:
            last_error = AslanError("NETWORK_ERROR", f"Network request failed: {exc}")
            if attempt < max_retries:
                continue

    raise last_error or AslanError("NETWORK_ERROR", "Request failed after retries")


async def async_http_request(
    *,
    method: str,
    path: str,
    secret_key: str,
    base_url: str,
    timeout: float,
    max_retries: int,
    body: Optional[dict[str, Any]] = None,
    query: Optional[dict[str, Any]] = None,
    headers: Optional[dict[str, str]] = None,
) -> Any:
    """Asynchronous HTTP request with exponential backoff retries."""
    import asyncio

    url = base_url.rstrip("/") + path
    request_headers = _build_headers(secret_key, headers)

    params: Optional[dict[str, str]] = None
    if query:
        params = {k: _query_value(v) for k, v in query.items() if v is not None}

    json_body: Optional[dict[str, Any]] = None
    if body is not None:
        json_body = {k: v for k, v in body.items() if v is not None}

    last_error: Optional[AslanError] = None

    for attempt in range(max_retries + 1):
        if attempt > 0:
            delay = min(0.5 * (2 ** (attempt - 1)), 5.0)
            await asyncio.sleep(delay)

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.request(
                    method,
                    url,
                    headers=request_headers,
                    params=params,
                    json=json_body if method != "GET" else None,
                )

            request_id = response.headers.get("x-request-id")

            if response.status_code in _RETRYABLE_STATUS_CODES and attempt < max_retries:
                last_error = AslanError(
                    "SERVER_ERROR",
                    f"Request failed with status {response.status_code}",
                    http_status=response.status_code,
                    request_id=request_id,
                )
                continue

            if not response.is_success:
                _handle_error_response(response, request_id)

            return _parse_success(response)

        except AslanError:
            raise
        except httpx.TimeoutException:
            last_error = AslanError("NETWORK_ERROR", "Request timed out")
            if attempt < max_retries:
                continue
        except httpx.HTTPError as exc:
            last_error = AslanError("NETWORK_ERROR", f"Network request failed: {exc}")
            if attempt < max_retries:
                continue

    raise last_error or AslanError("NETWORK_ERROR", "Request failed after retries")
