"""Aslan Payment SDK error types."""

from __future__ import annotations

from typing import Any, Literal, Optional

AslanErrorCode = Literal[
    "AUTHENTICATION_ERROR",
    "AUTHORIZATION_ERROR",
    "VALIDATION_ERROR",
    "NOT_FOUND",
    "RATE_LIMITED",
    "IDEMPOTENCY_ERROR",
    "NETWORK_ERROR",
    "SERVER_ERROR",
]


class AslanError(Exception):
    """Base exception for all Aslan Payment API errors.

    Attributes:
        code: Machine-readable error code.
        message: Human-readable error description.
        http_status: HTTP status code from the API response, if applicable.
        details: Additional error details from the API.
        request_id: Unique request identifier for support inquiries.
    """

    code: AslanErrorCode
    message: str
    http_status: Optional[int]
    details: Optional[dict[str, Any]]
    request_id: Optional[str]

    def __init__(
        self,
        code: AslanErrorCode,
        message: str,
        *,
        http_status: Optional[int] = None,
        details: Optional[dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.http_status = http_status
        self.details = details
        self.request_id = request_id

    def __repr__(self) -> str:
        parts = [f"code={self.code!r}", f"message={self.message!r}"]
        if self.http_status is not None:
            parts.append(f"http_status={self.http_status}")
        if self.request_id is not None:
            parts.append(f"request_id={self.request_id!r}")
        return f"AslanError({', '.join(parts)})"
