from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.db.models import Study, StudyVersion
from backend.app.schemas.study import StudyConfiguration, StudyStatus, StudyVersionSummary


class StudyRepository:
    """SQLAlchemy persistence adapter for studies and immutable configurations."""

    def create(self, db: Session, study: StudyConfiguration, owner_id: int) -> StudyConfiguration:
        study_record = Study(
            study_id=study.study_id,
            owner_id=owner_id,
            current_version=study.version,
            status=study.status.value,
        )
        study_record.versions.append(
            StudyVersion(
                version=study.version,
                status=study.status.value,
                configuration=study.model_dump(mode="json"),
            )
        )
        db.add(study_record)
        db.commit()
        return study

    def get(self, db: Session, study_id: str, owner_id: int) -> StudyConfiguration | None:
        statement = select(Study).where(Study.study_id == study_id, Study.owner_id == owner_id)
        study_record = db.scalar(statement)
        if study_record is None:
            return None
        version_record = max(study_record.versions, key=lambda version: version.version)
        return StudyConfiguration.model_validate(version_record.configuration)

    def list(self, db: Session, owner_id: int) -> list[StudyConfiguration]:
        statement = select(Study).where(Study.owner_id == owner_id).order_by(Study.created_at)
        records = db.scalars(statement).all()
        return [
            StudyConfiguration.model_validate(
                max(record.versions, key=lambda version: version.version).configuration
            )
            for record in records
        ]

    def publish(self, db: Session, study_id: str, owner_id: int) -> StudyConfiguration | None:
        statement = select(Study).where(Study.study_id == study_id, Study.owner_id == owner_id)
        study_record = db.scalar(statement)
        if study_record is None:
            return None
        study_record.status = "published"
        latest = max(study_record.versions, key=lambda version: version.version)
        latest.status = "published"
        latest.published_at = latest.published_at or datetime.now(UTC)
        latest.configuration = {**latest.configuration, "status": "published"}
        db.commit()
        return StudyConfiguration.model_validate(latest.configuration)

    def create_version(
        self, db: Session, study_id: str, owner_id: int, configuration: StudyConfiguration
    ) -> StudyConfiguration | None:
        statement = select(Study).where(Study.study_id == study_id, Study.owner_id == owner_id)
        study_record = db.scalar(statement)
        if study_record is None:
            return None
        next_version = max(version.version for version in study_record.versions) + 1
        draft = configuration.model_copy(
            update={"study_id": study_id, "version": next_version, "status": StudyStatus.DRAFT}
        )
        study_record.current_version = next_version
        study_record.status = StudyStatus.DRAFT.value
        study_record.versions.append(
            StudyVersion(
                version=next_version,
                status=StudyStatus.DRAFT.value,
                configuration=draft.model_dump(mode="json"),
            )
        )
        db.commit()
        return draft

    def list_versions(self, db: Session, study_id: str, owner_id: int) -> list[StudyVersionSummary] | None:
        statement = select(Study).where(Study.study_id == study_id, Study.owner_id == owner_id)
        study_record = db.scalar(statement)
        if study_record is None:
            return None
        return [
            StudyVersionSummary(
                version=version.version,
                status=version.status,
                created_at=version.created_at,
                published_at=version.published_at,
            )
            for version in sorted(study_record.versions, key=lambda item: item.version)
        ]

    def get_version(
        self, db: Session, study_id: str, version_number: int, owner_id: int
    ) -> StudyConfiguration | None:
        statement = select(Study).where(Study.study_id == study_id, Study.owner_id == owner_id)
        study_record = db.scalar(statement)
        if study_record is None:
            return None
        version = next(
            (item for item in study_record.versions if item.version == version_number), None
        )
        if version is None:
            return None
        return StudyConfiguration.model_validate(version.configuration)

    def transition_status(
        self, db: Session, study_id: str, owner_id: int, target_status: StudyStatus
    ) -> StudyConfiguration | None:
        statement = select(Study).where(Study.study_id == study_id, Study.owner_id == owner_id)
        study_record = db.scalar(statement)
        if study_record is None:
            return None
        latest = max(study_record.versions, key=lambda version: version.version)
        if latest.status not in {StudyStatus.PUBLISHED.value, StudyStatus.PAUSED.value}:
            raise ValueError(f"A {latest.status} study cannot be {target_status.value}")
        latest.status = target_status.value
        latest.configuration = {**latest.configuration, "status": target_status.value}
        study_record.status = target_status.value
        db.commit()
        return StudyConfiguration.model_validate(latest.configuration)


study_repository = StudyRepository()
