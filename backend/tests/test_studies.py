import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from backend.app.main import app
from backend.app.db.models import Study, StudyVersion
from backend.app.db.session import Base, get_db


client = TestClient(app)
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


def valid_payload() -> dict:
    return {
        "title": "Daily experience pilot",
        "description": "A short pilot study.",
        "consent": {
            "version": 1,
            "text": "I understand this study.",
            "ai_adaptation_disclosure": False,
            "data_processing_purposes": ["esm_responses"],
        },
        "lifecycle": {
            "start_at": "2026-11-01T09:00:00Z",
            "end_at": "2026-11-14T18:00:00Z",
            "timezone": "Europe/Helsinki",
        },
        "sampling": {"daily_limit": 5, "quiet_hours": [], "rules": []},
        "questions": [
            {
                "text": "How are you feeling right now?",
                "type": "likert",
                "order": 1,
                "options": [
                    {"value": "1", "label": "Very low"},
                    {"value": "5", "label": "Very high"},
                ],
            }
        ],
    }


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_dashboard_is_served() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "ESM Researcher Dashboard" in response.text


def auth_headers() -> dict[str, str]:
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "researcher@example.com",
            "password": "a-secure-password",
            "display_name": "Researcher",
        },
    )
    assert register_response.status_code == 201
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "researcher@example.com", "password": "a-secure-password"},
    )
    assert login_response.status_code == 200
    return {"Authorization": f"Bearer {login_response.json()['access_token']}"}


def test_create_validate_and_publish_study() -> None:
    headers = auth_headers()
    create_response = client.post("/api/v1/studies/drafts", json=valid_payload(), headers=headers)
    assert create_response.status_code == 201
    study_id = create_response.json()["study_id"]

    validation_response = client.post(f"/api/v1/studies/{study_id}/validate", headers=headers)
    assert validation_response.status_code == 200
    assert validation_response.json()["valid"] is True

    publish_response = client.post(f"/api/v1/studies/{study_id}/publish", headers=headers)
    assert publish_response.status_code == 200
    assert publish_response.json()["status"] == "published"


def test_invalid_lifecycle_is_rejected() -> None:
    payload = valid_payload()
    payload["lifecycle"]["end_at"] = "2026-10-01T18:00:00Z"
    response = client.post("/api/v1/studies/drafts", json=payload, headers=auth_headers())
    assert response.status_code == 422


def test_studies_require_authentication() -> None:
    response = client.get("/api/v1/studies")
    assert response.status_code == 401


def test_new_version_does_not_mutate_published_configuration() -> None:
    headers = auth_headers()
    create_response = client.post("/api/v1/studies/drafts", json=valid_payload(), headers=headers)
    study_id = create_response.json()["study_id"]
    publish_response = client.post(f"/api/v1/studies/{study_id}/publish", headers=headers)
    assert publish_response.json()["version"] == 1

    history_response = client.get(f"/api/v1/studies/{study_id}/versions", headers=headers)
    assert history_response.status_code == 200
    assert history_response.json()[0]["status"] == "published"
    version_response = client.get(f"/api/v1/studies/{study_id}/versions/1", headers=headers)
    assert version_response.status_code == 200
    assert version_response.json()["title"] == "Daily experience pilot"

    next_payload = valid_payload()
    next_payload["title"] = "Updated pilot"
    version_response = client.post(
        f"/api/v1/studies/{study_id}/versions", json=next_payload, headers=headers
    )
    assert version_response.status_code == 201
    assert version_response.json()["version"] == 2
    assert version_response.json()["status"] == "draft"

    current_response = client.get(f"/api/v1/studies/{study_id}", headers=headers)
    assert current_response.status_code == 200
    assert current_response.json()["title"] == "Updated pilot"
    assert current_response.json()["version"] == 2

    db = TestingSessionLocal()
    try:
        study = db.query(Study).filter(Study.study_id == study_id).one()
        versions = db.query(StudyVersion).filter(StudyVersion.study_id == study.id).all()
        assert [(version.version, version.status) for version in versions] == [(1, "published"), (2, "draft")]
    finally:
        db.close()


def test_published_study_can_be_paused_and_ended() -> None:
    headers = auth_headers()
    create_response = client.post("/api/v1/studies/drafts", json=valid_payload(), headers=headers)
    study_id = create_response.json()["study_id"]
    client.post(f"/api/v1/studies/{study_id}/publish", headers=headers)

    pause_response = client.post(f"/api/v1/studies/{study_id}/pause", headers=headers)
    assert pause_response.status_code == 200
    assert pause_response.json()["status"] == "paused"

    end_response = client.post(f"/api/v1/studies/{study_id}/end", headers=headers)
    assert end_response.status_code == 200
    assert end_response.json()["status"] == "ended"
