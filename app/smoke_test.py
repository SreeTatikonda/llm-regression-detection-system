import json
import sys

from app.exceptions import AppError, SmokeTestError
from app.llm.classifier import classify_support_email
from app.logging_config import configure_logging
from app.prompts.loader import load_prompt_config

SMOKE_TEST_EMAILS = [
    "I was charged twice for my yearly subscription and need one of the payments refunded.",
    "I can log in, but the Salesforce integration stopped syncing today and the dashboard shows a 500 error.",
    "I am locked out of my account and password reset emails never arrive.",
    "We are evaluating your platform and want to know whether onboarding is included with annual plans.",
]


def main() -> int:
    configure_logging()

    try:
        prompt_config = load_prompt_config()
        results = []
        for email in SMOKE_TEST_EMAILS:
            result = classify_support_email(email_text=email, prompt_config=prompt_config)
            results.append(
                {
                    "email": email,
                    "category": result.category.value,
                    "summary": result.summary,
                }
            )
        print(json.dumps(results, indent=2))
        return 0
    except AppError as exc:
        raise SmokeTestError(f"Smoke test failed: {exc}") from exc


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SmokeTestError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
