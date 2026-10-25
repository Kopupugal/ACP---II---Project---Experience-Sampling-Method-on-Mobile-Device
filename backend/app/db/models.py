from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(120))
    password_hash: Mapped[str] = mapped_column(Text)
    role: Mapped[str] = mapped_column(String(32), default="researcher")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    studies: Mapped[list["Study"]] = relationship(back_populates="owner")


class Study(Base):
    __tablename__ = "studies"

    id: Mapped[int] = mapped_column(primary_key=True)
    study_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    current_version: Mapped[int] = mapped_column(default=1)
    status: Mapped[str] = mapped_column(String(32), default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    owner: Mapped[User] = relationship(back_populates="studies")
    versions: Mapped[list["StudyVersion"]] = relationship(
        back_populates="study", cascade="all, delete-orphan"
    )


class StudyVersion(Base):
    __tablename__ = "study_versions"
    __table_args__ = (UniqueConstraint("study_id", "version", name="uq_study_version"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    study_id: Mapped[int] = mapped_column(ForeignKey("studies.id"), index=True)
    version: Mapped[int] = mapped_column()
    status: Mapped[str] = mapped_column(String(32), default="draft")
    configuration: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    study: Mapped[Study] = relationship(back_populates="versions")
