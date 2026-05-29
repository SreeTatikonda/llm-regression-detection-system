from openai import OpenAI

from app.settings import get_settings


def build_openai_client() -> OpenAI:
    settings = get_settings()
    return OpenAI(
        api_key=settings.openai_api_key,
        timeout=settings.openai_timeout_seconds,
        max_retries=settings.openai_max_retries,
    )
