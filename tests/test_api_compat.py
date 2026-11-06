"""Wire-format, envelope and error handling against the real API contract (httpx mocked)."""

from __future__ import annotations

import asyncio
import json
from typing import Any, Callable, Optional
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest

from aslan_payment import AslanError, AsyncAslan, Aslan

Handler = Callable[[httpx.Request], httpx.Response]


class Recorder:
    def __init__(self) -> None:
        self.requests: list[httpx.Request] = []
        self.response: httpx.Response = httpx.Response(200, json={})

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        r = self.response  # fresh copy so one canned response can serve sync and async clients
        return httpx.Response(r.status_code, headers=r.headers, content=r.content)

    @property
    def last(self) -> httpx.Request:
        return self.requests[-1]

    def body(self) -> Any:
        return json.loads(self.last.content)

    def query(self) -> dict[str, str]:
        return {k: v[0] for k, v in parse_qs(urlsplit(str(self.last.url)).query).items()}


@pytest.fixture
def rec(monkeypatch: pytest.MonkeyPatch) -> Recorder:
    recorder = Recorder()
    transport = httpx.MockTransport(recorder.handler)
    real_client, real_async = httpx.Client, httpx.AsyncClient

    def client(**kwargs: Any) -> httpx.Client:
        return real_client(transport=transport, **kwargs)

    def async_client(**kwargs: Any) -> httpx.AsyncClient:
        return real_async(transport=transport, **kwargs)

    monkeypatch.setattr(httpx, "Client", client)
    monkeypatch.setattr(httpx, "AsyncClient", async_client)
    return recorder


def sync_client() -> Aslan:
    return Aslan("sk_test_xxx", max_retries=0)


def async_client() -> AsyncAslan:
    return AsyncAslan("sk_test_xxx", max_retries=0)


PAGINATION = {"total": 41, "page": 2, "pageSize": 20, "totalPages": 3}


# ── Request wire names ──


CHECKOUT_PARAMS: Any = {
    "amount": 5000,
    "success_url": "https://example.com/s",
    "cancel_url": "https://example.com/c",
    "customer": {"email": "a@b.ma", "phone_country_code": "+212"},
    "billing_address": {"line1": "1 rue", "postal_code": "20000", "country": "MA"},
    "shipping_address": {"postal_code": "20000", "recipient_name": "Ahmed"},
    "line_items": [
        {"name": "W", "quantity": 2, "unit_price": 2500, "image_url": "https://x/i.png", "seller_id": "s1"}
    ],
    "sellers": [{"id": "s1", "name": "S", "metadata": {"seller_ref": "x"}}],
    "metadata": {"order_id": "o_1"},
    "vendorId": "v",
    "providerAccount": "foreign",
}

CHECKOUT_WIRE = {
    "amount": 5000,
    "currency": "MAD",
    "successUrl": "https://example.com/s",
    "cancelUrl": "https://example.com/c",
    "customer": {"email": "a@b.ma", "phoneCountryCode": "+212"},
    "billingAddress": {"line1": "1 rue", "postalCode": "20000", "country": "MA"},
    "shippingAddress": {"postalCode": "20000", "recipientName": "Ahmed"},
    "lineItems": [
        {"name": "W", "quantity": 2, "unitPrice": 2500, "imageUrl": "https://x/i.png", "sellerId": "s1"}
    ],
    "sellers": [{"id": "s1", "name": "S", "metadata": {"seller_ref": "x"}}],
    "metadata": {"order_id": "o_1"},  # user keys sent verbatim
    "vendorId": "v",
    "providerAccount": "foreign",
}


def test_checkout_create_body_is_camel_case(rec: Recorder) -> None:
    rec.response = httpx.Response(201, json={"id": "cs_1", "url": "https://pay", "expiresAt": "t"})
    session = sync_client().checkout_sessions.create(CHECKOUT_PARAMS, idempotency_key="k1")
    assert rec.last.method == "POST"
    assert rec.last.url.path == "/pay/api/v1/checkout/sessions"
    assert rec.last.headers["Idempotency-Key"] == "k1"
    assert rec.body() == CHECKOUT_WIRE
    # checkout create is not wrapped in {data}
    assert session["id"] == "cs_1"
    assert session["expiresAt"] == "t"


def test_checkout_create_async_body_is_camel_case(rec: Recorder) -> None:
    rec.response = httpx.Response(201, json={"id": "cs_1"})
    session = asyncio.run(async_client().checkout_sessions.create(CHECKOUT_PARAMS))
    assert rec.body() == CHECKOUT_WIRE
    assert session["id"] == "cs_1"


def test_checkout_camel_case_input_passes_through(rec: Recorder) -> None:
    rec.response = httpx.Response(201, json={"id": "cs_1"})
    sync_client().checkout_sessions.create(
        {"amount": 100, "successUrl": "https://a", "cancelUrl": "https://b"}  # type: ignore[typeddict-unknown-key]
    )
    assert rec.body() == {"amount": 100, "currency": "MAD", "successUrl": "https://a", "cancelUrl": "https://b"}


def test_refund_create_body(rec: Recorder) -> None:
    rec.response = httpx.Response(201, json={"data": {"id": "ref_1", "transactionId": "t1"}})
    refund = sync_client().refunds.create({"transaction_id": "t1", "amount": 500, "reason": "r"})
    assert rec.body() == {"transactionId": "t1", "amount": 500, "reason": "r"}
    assert refund == {"id": "ref_1", "transactionId": "t1"}


def test_payment_link_create_and_update_bodies(rec: Recorder) -> None:
    rec.response = httpx.Response(201, json={"data": {"id": "pl_1"}})
    link = sync_client().payment_links.create(
        {"amount": 100, "max_payments": 1, "expires_at": "2030-01-01T00:00:00Z", "metadata": {"inv_id": "1"}}
    )
    assert rec.body() == {
        "currency": "MAD",
        "amount": 100,
        "maxPayments": 1,
        "expiresAt": "2030-01-01T00:00:00Z",
        "metadata": {"inv_id": "1"},
    }
    assert link == {"id": "pl_1"}

    rec.response = httpx.Response(200, json={"data": {"id": "pl_1", "status": "inactive"}})
    updated = asyncio.run(
        async_client().payment_links.update("pl_1", {"status": "inactive", "max_payments": 3})
    )
    assert rec.last.method == "PATCH"
    assert rec.body() == {"status": "inactive", "maxPayments": 3}
    assert updated["status"] == "inactive"


def test_transactions_list_query(rec: Recorder) -> None:
    rec.response = httpx.Response(200, json={"data": [{"id": "t1"}], "pagination": PAGINATION})
    result = sync_client().transactions.list(
        {
            "page": 2,
            "page_size": 20,
            "status": "succeeded",
            "from_date": "2025-01-01T00:00:00Z",
            "to_date": "2025-12-31T00:00:00Z",
            "sort_by": "created_at",
            "sort_order": "desc",
        }
    )
    assert rec.query() == {
        "page": "2",
        "pageSize": "20",
        "status": "succeeded",
        "from": "2025-01-01T00:00:00Z",
        "to": "2025-12-31T00:00:00Z",
        "sortBy": "createdAt",
        "sortOrder": "desc",
    }
    # list responses keep the {data, pagination} shape
    assert result["data"] == [{"id": "t1"}]
    assert result["pagination"] == PAGINATION


def test_refunds_and_payment_links_list_query(rec: Recorder) -> None:
    rec.response = httpx.Response(200, json={"data": [], "pagination": PAGINATION})
    asyncio.run(async_client().refunds.list({"page_size": 5, "transaction_id": "t1", "status": "pending"}))
    assert rec.query() == {"pageSize": "5", "transactionId": "t1", "status": "pending"}

    page = sync_client().payment_links.list({"page": 1, "page_size": 10, "status": "active"})
    assert rec.query() == {"page": "1", "pageSize": "10", "status": "active"}
    assert page["pagination"]["totalPages"] == 3


def test_boolean_query_values_are_lowercase(rec: Recorder) -> None:
    rec.response = httpx.Response(200, json={"data": [], "total": 0, "page": 1, "limit": 20, "totalPages": 0})
    sync_client().vendors.list({"isActive": True})
    assert rec.query() == {"isActive": "true"}


# ── Response envelope ──


@pytest.mark.parametrize(
    "call",
    [
        lambda c: c.transactions.retrieve("t1"),
        lambda c: c.refunds.retrieve("r1"),
        lambda c: c.payment_links.retrieve("pl_1"),
        lambda c: c.customers.retrieve("cu_1"),
        lambda c: c.vendors.retrieve("v1"),
        lambda c: c.webhooks_config.retrieve(),
    ],
)
def test_single_object_envelope_is_unwrapped(rec: Recorder, call: Callable[[Aslan], Any]) -> None:
    rec.response = httpx.Response(200, json={"data": {"id": "x1", "createdAt": "t"}})
    assert call(sync_client()) == {"id": "x1", "createdAt": "t"}


def test_single_object_envelope_is_unwrapped_async(rec: Recorder) -> None:
    rec.response = httpx.Response(200, json={"data": {"id": "t1", "paidAt": None}})
    assert asyncio.run(async_client().transactions.retrieve("t1")) == {"id": "t1", "paidAt": None}


def test_checkout_retrieve_is_not_wrapped(rec: Recorder) -> None:
    rec.response = httpx.Response(200, json={"id": "cs_1", "status": "open", "successUrl": "https://a"})
    session = sync_client().checkout_sessions.retrieve("cs_1")
    assert session == {"id": "cs_1", "status": "open", "successUrl": "https://a"}


def test_api_keys_list_unwraps_to_list(rec: Recorder) -> None:
    rec.response = httpx.Response(200, json={"data": [{"id": "k1"}]})
    assert sync_client().api_keys.list() == [{"id": "k1"}]


def test_delete_204_returns_none(rec: Recorder) -> None:
    rec.response = httpx.Response(204)
    sync_client().payment_links.delete("pl_1")
    assert rec.last.method == "DELETE"


def test_qr_json_and_raw(rec: Recorder) -> None:
    rec.response = httpx.Response(200, json={"data": {"dataUri": "data:image/png;base64,AA", "mimeType": "image/png"}})
    assert sync_client().payment_links.get_qr("pl_1") == {
        "dataUri": "data:image/png;base64,AA",
        "mimeType": "image/png",
    }
    rec.response = httpx.Response(200, content=b"<svg/>", headers={"content-type": "image/svg+xml"})
    assert sync_client().payment_links.get_qr("pl_1", {"format": "svg"}) == b"<svg/>"
    assert rec.query() == {"format": "svg"}


# ── Errors ──


def _raise(rec: Recorder, response: httpx.Response, use_async: bool = False) -> AslanError:
    rec.response = response
    with pytest.raises(AslanError) as info:
        if use_async:
            asyncio.run(async_client().transactions.retrieve("t1"))
        else:
            sync_client().transactions.retrieve("t1")
    return info.value


@pytest.mark.parametrize("use_async", [False, True])
def test_flat_error_shape(rec: Recorder, use_async: bool) -> None:
    err = _raise(
        rec,
        httpx.Response(
            401,
            json={"statusCode": 401, "code": "AUTHENTICATION_ERROR", "error": "Unauthorized", "message": "Invalid API key"},
            headers={"x-request-id": "req_1"},
        ),
        use_async,
    )
    assert err.code == "AUTHENTICATION_ERROR"
    assert err.message == "Invalid API key"
    assert err.http_status == 401
    assert err.request_id == "req_1"


def test_flat_error_with_details(rec: Recorder) -> None:
    details = {"errors": {"successUrl": ["Required"]}}
    err = _raise(
        rec,
        httpx.Response(
            400,
            json={"statusCode": 400, "code": "VALIDATION_ERROR", "error": "Bad Request", "message": "Invalid", "details": details},
        ),
    )
    assert err.code == "VALIDATION_ERROR"
    assert err.details == details


def test_flat_error_without_message_uses_error_string(rec: Recorder) -> None:
    err = _raise(rec, httpx.Response(401, json={"statusCode": 401, "error": "Unauthorized"}))
    assert err.code == "AUTHENTICATION_ERROR"
    assert err.message == "Unauthorized"


@pytest.mark.parametrize("use_async", [False, True])
def test_nested_error_shape(rec: Recorder, use_async: bool) -> None:
    err = _raise(
        rec,
        httpx.Response(
            404,
            json={"error": {"code": "NOT_FOUND", "message": "Transaction not found", "details": {"id": "t1"}}},
        ),
        use_async,
    )
    assert err.code == "NOT_FOUND"
    assert err.message == "Transaction not found"
    assert err.details == {"id": "t1"}


def test_provider_account_error_code_passthrough(rec: Recorder) -> None:
    err = _raise(
        rec,
        httpx.Response(400, json={"statusCode": 400, "code": "PROVIDER_ACCOUNT_INACTIVE", "error": "Bad Request", "message": "x"}),
    )
    assert err.code == "PROVIDER_ACCOUNT_INACTIVE"


@pytest.mark.parametrize(
    "response,code",
    [
        (httpx.Response(502, text="<html>Bad Gateway</html>"), "SERVER_ERROR"),
        (httpx.Response(404, text="Not Found"), "NOT_FOUND"),
        (httpx.Response(429, json=["unexpected"]), "RATE_LIMITED"),
        (httpx.Response(403, json="Forbidden"), "AUTHORIZATION_ERROR"),
        (httpx.Response(500, json={}), "SERVER_ERROR"),
    ],
)
def test_unexpected_error_bodies_still_raise_aslan_error(
    rec: Recorder, response: httpx.Response, code: Optional[str]
) -> None:
    err = _raise(rec, response)
    assert err.code == code
    assert err.http_status == response.status_code
