from typing import Any
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.vehicle_report import VehicleReport

REPORTS_URL = "/api/v1/reports"
LISTING_URL = "https://example.com/listings/123"


def valid_payload(**overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "listing_url": LISTING_URL,
        "make": "Toyota",
        "model": "Corolla",
        "year": 2018,
        "mileage": 85000,
        "price": "12500.00",
    }
    payload.update(overrides)
    return payload


def test_create_report_returns_201_with_report(client: TestClient) -> None:
    response = client.post(REPORTS_URL, json=valid_payload())

    assert response.status_code == 201
    body = response.json()
    UUID(body["id"])
    assert body["listing_url"] == LISTING_URL
    assert body["make"] == "Toyota"
    assert body["model"] == "Corolla"
    assert body["year"] == 2018
    assert body["mileage"] == 85000
    assert float(body["price"]) == 12500.00
    assert body["status"] == "pending"
    assert body["created_at"]


def test_create_report_accepts_only_required_fields(client: TestClient) -> None:
    response = client.post(REPORTS_URL, json={"make": "Honda", "model": "Civic"})

    assert response.status_code == 201
    body = response.json()
    assert body["listing_url"] is None
    assert body["year"] is None
    assert body["mileage"] is None
    assert body["price"] is None


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param(valid_payload(mileage=-1), id="negative-mileage"),
        pytest.param(valid_payload(price="-0.01"), id="negative-price"),
        pytest.param(valid_payload(year=1885), id="year-too-early"),
        pytest.param(valid_payload(year=2101), id="year-too-late"),
        pytest.param(valid_payload(year="not-a-year"), id="year-not-integer"),
        pytest.param(valid_payload(make=""), id="empty-make"),
        pytest.param(
            {k: v for k, v in valid_payload().items() if k != "make"},
            id="missing-make",
        ),
        pytest.param(
            {k: v for k, v in valid_payload().items() if k != "model"},
            id="missing-model",
        ),
        pytest.param({}, id="empty-body"),
    ],
)
def test_create_report_rejects_invalid_payload(
    client: TestClient,
    payload: dict[str, Any],
) -> None:
    response = client.post(REPORTS_URL, json=payload)

    assert response.status_code == 422


def test_get_report_returns_existing_report(client: TestClient) -> None:
    created = client.post(REPORTS_URL, json=valid_payload()).json()

    response = client.get(f"{REPORTS_URL}/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created


def test_get_report_returns_404_for_unknown_id(client: TestClient) -> None:
    response = client.get(f"{REPORTS_URL}/{uuid4()}")

    assert response.status_code == 404


def test_get_report_returns_422_for_malformed_id(client: TestClient) -> None:
    response = client.get(f"{REPORTS_URL}/not-a-uuid")

    assert response.status_code == 422


def test_create_report_returns_409_when_listing_is_pending(
    client: TestClient,
) -> None:
    first = client.post(REPORTS_URL, json=valid_payload())
    assert first.status_code == 201

    response = client.post(REPORTS_URL, json=valid_payload())

    assert response.status_code == 409


def test_create_report_allows_listing_without_pending_report(
    client: TestClient,
    db_session: Session,
) -> None:
    db_session.add(
        VehicleReport(
            listing_url=LISTING_URL,
            make="Toyota",
            model="Corolla",
            status="completed",
        )
    )
    db_session.commit()

    response = client.post(REPORTS_URL, json=valid_payload())

    assert response.status_code == 201
    assert response.json()["status"] == "pending"


def test_create_report_allows_different_listing_url(client: TestClient) -> None:
    client.post(REPORTS_URL, json=valid_payload())

    response = client.post(
        REPORTS_URL,
        json=valid_payload(listing_url="https://example.com/listings/456"),
    )

    assert response.status_code == 201


def test_create_report_without_listing_url_never_conflicts(
    client: TestClient,
) -> None:
    first = client.post(REPORTS_URL, json=valid_payload(listing_url=None))
    second = client.post(REPORTS_URL, json=valid_payload(listing_url=None))

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["id"] != second.json()["id"]
