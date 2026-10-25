from datetime import datetime, time
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StudyStatus(StrEnum):
    DRAFT = "draft"
    VALIDATED = "validated"
    APPROVED = "approved"
    PUBLISHED = "published"
    PAUSED = "paused"
    ENDED = "ended"


class QuestionType(StrEnum):
    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"
    LIKERT = "likert"
    SLIDER = "slider"
    NUMERIC = "numeric"
    FREE_TEXT = "free_text"
    YES_NO = "yes_no"


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ConsentConfiguration(StrictModel):
    version: int = Field(ge=1)
    text: str = Field(min_length=1)
    ai_adaptation_disclosure: bool = False
    data_processing_purposes: list[str] = Field(min_length=1)


class StudyLifecycle(StrictModel):
    start_at: datetime
    end_at: datetime
    timezone: str = Field(min_length=1, max_length=64)

    @model_validator(mode="after")
    def end_after_start(self) -> "StudyLifecycle":
        if self.end_at <= self.start_at:
            raise ValueError("end_at must be later than start_at")
        return self


class QuietHours(StrictModel):
    start: time
    end: time


class SamplingConfiguration(StrictModel):
    daily_limit: int = Field(ge=1, le=100)
    quiet_hours: list[QuietHours] = Field(default_factory=list)
    rules: list[str] = Field(default_factory=list)


class QuestionOption(StrictModel):
    value: str = Field(min_length=1)
    label: str = Field(min_length=1)


class Question(StrictModel):
    question_id: str = Field(default_factory=lambda: f"question-{uuid4().hex[:12]}")
    text: str = Field(min_length=1, max_length=500)
    type: QuestionType
    required: bool = True
    order: int = Field(ge=1)
    options: list[QuestionOption] = Field(default_factory=list)
    adaptation_allowed: bool = False
    follow_up_allowed: bool = False

    @model_validator(mode="after")
    def validate_options(self) -> "Question":
        option_types = {
            QuestionType.SINGLE_CHOICE,
            QuestionType.MULTIPLE_CHOICE,
            QuestionType.LIKERT,
        }
        if self.type in option_types and not self.options:
            raise ValueError(f"{self.type} questions require options")
        if self.type not in option_types and self.options:
            raise ValueError(f"{self.type} questions cannot define options")
        return self


class LlmPolicy(StrictModel):
    adaptation_allowed: bool = False
    max_follow_ups: int = Field(default=0, ge=0, le=5)
    approved_topics: list[str] = Field(default_factory=list)
    researcher_approval_required: bool = True


class StudyConfiguration(StrictModel):
    schema_version: str = Field(default="1.0", min_length=1)
    study_id: str = Field(default_factory=lambda: f"study-{uuid4().hex[:12]}")
    version: int = Field(default=1, ge=1)
    status: StudyStatus = StudyStatus.DRAFT
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=2000)
    consent: ConsentConfiguration
    lifecycle: StudyLifecycle
    sampling: SamplingConfiguration
    questions: list[Question] = Field(min_length=1)
    llm_policy: LlmPolicy = Field(default_factory=LlmPolicy)

    @model_validator(mode="after")
    def validate_question_order(self) -> "StudyConfiguration":
        orders = [question.order for question in self.questions]
        if len(orders) != len(set(orders)):
            raise ValueError("question order values must be unique")
        return self


class StudySummary(StrictModel):
    study_id: str
    title: str
    version: int
    status: StudyStatus


class StudyVersionSummary(StrictModel):
    version: int
    status: StudyStatus
    created_at: datetime
    published_at: datetime | None = None


class ValidationResult(StrictModel):
    valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
