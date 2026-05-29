from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.contracts import SupportCategory


class PromptExample(BaseModel):
    input_email: str = Field(..., min_length=10, description="Example customer support email.")
    category: SupportCategory = Field(..., description="Expected category for the example.")
    summary: str = Field(..., min_length=10, max_length=220, description="Expected one-sentence summary.")
    rationale: str = Field(..., min_length=20, max_length=500, description="Why this label choice is correct.")

    @field_validator("input_email", "summary", "rationale")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        return " ".join(value.strip().split())


class PromptConfig(BaseModel):
    version: str = Field(..., min_length=2, max_length=50)
    created_at: datetime = Field(..., description="UTC timestamp for this prompt version.")
    feature_name: str = Field(default="support_email_classifier", min_length=3, max_length=100)
    owner: str = Field(..., min_length=3, max_length=100)
    model: str = Field(..., min_length=1, max_length=100)
    temperature: float = Field(default=0.0, ge=0.0, le=1.0)
    max_output_tokens: int = Field(default=120, ge=50, le=500)
    prompt_intent: Literal["classification", "classification_and_summarization"] = "classification_and_summarization"
    system_prompt: str = Field(..., min_length=200, max_length=8000)
    instructions: list[str] = Field(default_factory=list)
    few_shot_examples: list[PromptExample] = Field(default_factory=list)
    allowed_categories: list[SupportCategory] = Field(
        default_factory=lambda: [
            SupportCategory.BILLING,
            SupportCategory.TECHNICAL,
            SupportCategory.ACCOUNT,
            SupportCategory.GENERAL,
        ]
    )

    @field_validator("version", "feature_name", "owner", "model", "system_prompt")
    @classmethod
    def normalize_scalar_text(cls, value: str) -> str:
        return value.strip()

    @field_validator("instructions")
    @classmethod
    def normalize_instructions(cls, value: list[str]) -> list[str]:
        cleaned = [" ".join(item.strip().split()) for item in value if item and item.strip()]
        if len(cleaned) != len(value):
            raise ValueError("Instructions cannot contain empty entries.")
        return cleaned

    @field_validator("created_at")
    @classmethod
    def ensure_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @model_validator(mode="after")
    def validate_examples_and_categories(self) -> "PromptConfig":
        allowed = set(self.allowed_categories)
        for example in self.few_shot_examples:
            if example.category not in allowed:
                raise ValueError(f"Example category {example.category} is not in allowed_categories.")
        if len(set(self.allowed_categories)) != len(self.allowed_categories):
            raise ValueError("allowed_categories contains duplicates.")
        if not self.few_shot_examples:
            raise ValueError("At least one few-shot example is required for a production-grade prompt config.")
        return self
