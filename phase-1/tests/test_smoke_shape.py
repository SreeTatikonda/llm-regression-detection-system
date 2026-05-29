from app.models.contracts import ClassifierOutput, SupportCategory


def test_classifier_output_enum_values():
    assert SupportCategory.BILLING.value == "billing"
    assert SupportCategory.TECHNICAL.value == "technical"
    assert SupportCategory.ACCOUNT.value == "account"
    assert SupportCategory.GENERAL.value == "general"


def test_classifier_output_shape():
    result = ClassifierOutput(
        category=SupportCategory.BILLING,
        summary="Customer reports a duplicate subscription charge and requests a refund.",
    )
    dumped = result.model_dump()
    assert set(dumped.keys()) == {"category", "summary"}
