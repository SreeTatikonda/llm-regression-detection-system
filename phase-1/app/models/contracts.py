import re
from enum import Enum

from pydantic import BaseModel, Field, field_validator

from app.exceptions import ClassifierInputError


class SupportCategory(str, Enum):
    BILLING = "billing"
    TECHNICAL = "technical"
    ACCOUNT = "account"
    GENERAL = "general"


class SupportEmailInput(BaseModel):
    email_text: str = Field(..., min_length=5, max_length=10000, description="Raw customer support email text.")

    @field_validator("email_text")
    @classmethod
    def validate_email_text(cls, value: str) -> str:
        normalized = " ".join(value.strip().split())
        if not normalized:
            raise ClassifierInputError("Email text cannot be empty or whitespace.")
        if len(normalized) < 5:
            raise ClassifierInputError("Email text is too short to classify reliably.")
        return normalized


class ClassifierOutput(BaseModel):
    category: SupportCategory = Field(..., description="Predicted customer support category.")
    summary: str = Field(
        ...,
        min_length=10,
        max_length=220,
        description="One-sentence operational summary for support triage.",
    )

    @field_validator("summary")
    @classmethod
    def validate_summary(cls, value: str) -> str:
        normalized = " ".join(value.strip().split())
        if not normalized:
            raise ValueError("Summary cannot be empty.")
        if len(normalized.split()) > 35:
            raise ValueError("Summary is too long for operational triage.")
        sentence_endings = normalized.count(".") + normalized.count("!") + normalized.count("?")
        if sentence_endings > 2:
            raise ValueError("Summary must be concise and close to a single sentence.")
        if re.search(r"(category|billing|technical|account|general)", normalized, re.IGNORECASE):
            raise ValueError("Summary should not explicitly mention category labels.")
        return normalized
