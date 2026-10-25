from fastapi import APIRouter, HTTPException, status

from backend.app.api.dependencies import CurrentUser, DbSession
from backend.app.repositories.study_repository import study_repository
from backend.app.schemas.study import (
    StudyConfiguration,
    StudySummary,
    StudyVersionSummary,
    StudyStatus,
    ValidationResult,
)
from backend.app.services.study_service import StudyService


router = APIRouter(prefix="/studies", tags=["studies"])
study_service = StudyService(study_repository)


@router.post("/drafts", response_model=StudyConfiguration, status_code=status.HTTP_201_CREATED)
def create_draft(configuration: StudyConfiguration, db: DbSession, user: CurrentUser) -> StudyConfiguration:
    """Create a draft study configuration."""
    return study_service.create_draft(db, configuration, user)


@router.get("", response_model=list[StudySummary])
def list_studies(db: DbSession, user: CurrentUser) -> list[StudySummary]:
    """List study metadata without exposing participant data."""
    return study_service.list_studies(db, user)


@router.get("/{study_id}", response_model=StudyConfiguration)
def get_study(study_id: str, db: DbSession, user: CurrentUser) -> StudyConfiguration:
    study = study_service.get_study(db, study_id, user)
    if study is None:
        raise HTTPException(status_code=404, detail="Study not found")
    return study


@router.post("/{study_id}/versions", response_model=StudyConfiguration, status_code=status.HTTP_201_CREATED)
def create_version(
    study_id: str, configuration: StudyConfiguration, db: DbSession, user: CurrentUser
) -> StudyConfiguration:
    """Create a new draft version without mutating an existing version."""
    try:
        return study_service.create_version(db, study_id, configuration, user)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{study_id}/versions", response_model=list[StudyVersionSummary])
def list_versions(study_id: str, db: DbSession, user: CurrentUser) -> list[StudyVersionSummary]:
    try:
        return study_service.list_versions(db, study_id, user)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{study_id}/versions/{version}", response_model=StudyConfiguration)
def get_version(study_id: str, version: int, db: DbSession, user: CurrentUser) -> StudyConfiguration:
    try:
        return study_service.get_version(db, study_id, version, user)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{study_id}/validate", response_model=ValidationResult)
def validate_study(study_id: str, db: DbSession, user: CurrentUser) -> ValidationResult:
    study = study_service.get_study(db, study_id, user)
    if study is None:
        raise HTTPException(status_code=404, detail="Study not found")
    return study_service.validate(study)


@router.post("/{study_id}/publish", response_model=StudyConfiguration)
def publish_study(study_id: str, db: DbSession, user: CurrentUser) -> StudyConfiguration:
    study = study_service.get_study(db, study_id, user)
    if study is None:
        raise HTTPException(status_code=404, detail="Study not found")
    try:
        return study_service.publish(db, study, user)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/{study_id}/pause", response_model=StudyConfiguration)
def pause_study(study_id: str, db: DbSession, user: CurrentUser) -> StudyConfiguration:
    try:
        return study_service.transition_status(db, study_id, user, StudyStatus.PAUSED)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/{study_id}/end", response_model=StudyConfiguration)
def end_study(study_id: str, db: DbSession, user: CurrentUser) -> StudyConfiguration:
    try:
        return study_service.transition_status(db, study_id, user, StudyStatus.ENDED)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
