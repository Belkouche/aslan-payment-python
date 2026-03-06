"""Webhook signature verification."""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from typing import Union

from ..errors import AslanError
from ..types import WebhookEvent


class Webhooks:
    """Webhook signature verification.

    Uses HMAC-SHA256 with the format ``t=TIMESTAMP,v1=SIGNATURE``.
    """

    def __init__(self, webhook_secret: str) -> None:
        self._webhook_secret = webhook_secret

    def verify(
        self,
        payload: Union[str, bytes],
        signature: str,
        *,
        tolerance: int = 300,
    ) -> WebhookEvent:
        """Verify a webhook signature and parse the event payload.

        Args:
            payload: Raw request body (string or bytes).
            signature: Value of the ``Aslan-Signature`` header (format: ``t=TIMESTAMP,v1=SIGNATURE``).
            tolerance: Maximum allowed age of the webhook in seconds. Defaults to 300 (5 minutes).

        Returns:
            Parsed webhook event.

        Raises:
            AslanError: If the signature is invalid, the timestamp is too old, or the payload is malformed.
        """
        payload_str = payload if isinstance(payload, str) else payload.decode("utf-8")

        parts = signature.split(",")
        timestamp_part = next((p for p in parts if p.startswith("t=")), None)
        signature_part = next((p for p in parts if p.startswith("v1=")), None)

        if not timestamp_part or not signature_part:
            raise AslanError("VALIDATION_ERROR", "Invalid webhook signature format")

        try:
            timestamp = int(timestamp_part[2:])
        except ValueError:
            raise AslanError("VALIDATION_ERROR", "Invalid webhook timestamp")

        now = int(time.time())
        if abs(now - timestamp) > tolerance:
            raise AslanError("VALIDATION_ERROR", "Webhook timestamp too old")

        signed_payload = f"{timestamp}.{payload_str}"
        computed_sig = hmac.new(
            self._webhook_secret.encode("utf-8"),
            signed_payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        expected_sig = signature_part[3:]

        expected_bytes = bytes.fromhex(expected_sig)
        computed_bytes = bytes.fromhex(computed_sig)

        if not hmac.compare_digest(expected_bytes, computed_bytes):
            raise AslanError("VALIDATION_ERROR", "Webhook signature verification failed")

        try:
            return json.loads(payload_str)
        except json.JSONDecodeError:
            raise AslanError("VALIDATION_ERROR", "Invalid webhook payload JSON")
