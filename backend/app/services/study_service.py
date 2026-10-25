from sqlalchemy.orm import Session

from backend.app.db.models import User
from backend.app.repositories.study_repository import StudyRepository
from backend.app.schemas.study import (
    StudyConfiguration,
    StudyStatus,
    StudySummary,
    StudyVersionSummary,
    ValidationResult,
)


class StudyService:
    def __init__(self, repository: StudyRepository) -> None:
        self.repository = repository

    def create_draft(self, db: Session, study: StudyConfiguration, owner: User) -> StudyConfiguration:
        study.status = StudyStatus.DRAFT
        return self.repository.create(db, study, owner.id)

    def get_study(self, db: Session, study_id: str, owner: User) -> StudyConfiguration | None:
        return self.repository.get(db, study_id, owner.id)

    def list_studies(self, db: Session, owner: User) -> list[StudySummary]:
        return [
            StudySummary(
                study_id=study.study_id,
                title=study.title,
                version=study.version,
                status=study.status,
            )
            for study in self.repository.list(db, owner.id)
        ]

    def validate(self, study: StudyConfiguration) -> ValidationResult:
        warnings: list[str] = []
        if len(study.questions) > 8:
            warnings.append("Questionnaire has more than eight questions; review participant burden.")
        if study.llm_policy.adaptation_allowed and not study.consent.ai_adaptation_disclosure:
            return ValidationResult(
                valid=False,
                errors=["AI adaptation requires an AI adaptation disclosure in consent."],
                warnings=warnings,
            )
        return ValidationResult(valid=True, warnings=warnings)

    def publish(self, db: Session, study: StudyConfiguration, owner: User) -> StudyConfiguration:
        result = self.validate(study)
        if not result.valid:
            raise ValueError("Study cannot be published: " + "; ".join(result.errors))
        published = self.repository.publish(db, study.study_id, owner.id)
        if published is None:
            raise ValueError("Study not found")
        return published

    def create_version(
        self, db: Session, study_id: str, configuration: StudyConfiguration, owner: User
    ) -> StudyConfiguration:
        version = self.repository.create_version(db, study_id, owner.id, configuration)
        if version is None:
            raise ValueError("Study not found")
        return version

    def list_versions(
        self, db: Session, study_id: str, owner: User
    ) -> list[StudyVersionSummary]:
        versions = self.repository.list_versions(db, study_id, owner.id)
        if versions is None:
            raise ValueError("Study not found")
        return versions

    def get_version(
        self, db: Session, study_id: str, version: int, owner: User
    ) -> StudyConfiguration:
        configuration = self.repository.get_version(db, study_id, version, owner.id)
        if configuration is None:
            raise ValueError("Study version not found")
        return configuration

    def transition_status(
        self, db: Session, study_id: str, owner: User, target_status: StudyStatus
    ) -> StudyConfiguration:
        configuration = self.repository.transition_status(db, study_id, owner.id, target_status)
        if configuration is None:
            raise ValueError("Study not found")
        return configuration
