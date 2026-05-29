from app.llm.classifier import classify_support_email
from app.models.contracts import SupportCategory
from app.prompts.loader import load_prompt_config


class FakeParsedMessage:
    def __init__(self, parsed):
        self.parsed = parsed
        self.refusal = None


class FakeChoice:
    def __init__(self, parsed):
        self.message = FakeParsedMessage(parsed)


class FakeResponse:
    def __init__(self, parsed):
        self.choices = [FakeChoice(parsed)]


class FakeCompletions:
    def parse(self, **kwargs):
        return FakeResponse(
            {
                "category": SupportCategory.ACCOUNT,
                "summary": "Customer cannot access the account after failed password reset attempts.",
            }
        )


class FakeChat:
    def __init__(self):
        self.completions = FakeCompletions()


class FakeBeta:
    def __init__(self):
        self.chat = FakeChat()


class FakeClient:
    def __init__(self):
        self.beta = FakeBeta()


def test_classify_support_email_returns_valid_output(monkeypatch):
    monkeypatch.setattr("app.llm.classifier.build_openai_client", lambda: FakeClient())
    prompt_config = load_prompt_config("prompts/support_classifier_v1.yaml")

    result = classify_support_email(
        email_text="I am locked out of my account and password reset is not working.",
        prompt_config=prompt_config,
    )

    assert result.category == SupportCategory.ACCOUNT
    assert "access" in result.summary.lower() or "account" in result.summary.lower()
