import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def activities_data(monkeypatch):
    activities = {
        "Chess Club": {
            "description": "Practice chess",
            "schedule": "Fridays",
            "max_participants": 12,
            "participants": ["existing@example.com"],
        }
    }
    monkeypatch.setattr(app_module, "activities", activities)
    return activities


@pytest.fixture
def client(activities_data):
    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_activity_data(client, activities_data):
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json() == activities_data


def test_signup_adds_participant(client, activities_data):
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "new@example.com"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Signed up new@example.com for Chess Club"}
    assert activities_data["Chess Club"]["participants"] == [
        "existing@example.com",
        "new@example.com",
    ]


def test_signup_rejects_duplicate_participant(client, activities_data):
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "existing@example.com"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"
    assert activities_data["Chess Club"]["participants"] == ["existing@example.com"]


def test_signup_rejects_unknown_activity(client):
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": "new@example.com"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(client, activities_data):
    response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": "existing@example.com"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Unregistered existing@example.com from Chess Club"
    }
    assert activities_data["Chess Club"]["participants"] == []


def test_unregister_rejects_absent_participant(client, activities_data):
    response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": "absent@example.com"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
    assert activities_data["Chess Club"]["participants"] == ["existing@example.com"]


def test_unregister_rejects_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown Club/signup",
        params={"email": "existing@example.com"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"