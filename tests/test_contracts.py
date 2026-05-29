import pytest
from pydantic import ValidationError

from app.models.contracts import ClassifierOutput, SupportCategory, SupportEmailInput


def test_support_email_input_rejects_blank():
    with pytest.raises(Exception):
        SupportEmailInput(email_text="   ")


def test_classifier_output_accepts_valid_payload():
    result = ClassifierOutput(
        category=SupportCategory.BILLING,
        summary="Customer reports a duplicate charge and requests a refund.",
    )
    assert result.category == SupportCategory.BILLING


def test_classifier_output_rejects_long_multisentence_summary():
    with pytest.raises(ValidationError):
        ClassifierOutput(
            category=SupportCategory.TECHNICAL,
            summary="The customer reports a syncing issue. They also mention another bug. Please escalate.",
        )
