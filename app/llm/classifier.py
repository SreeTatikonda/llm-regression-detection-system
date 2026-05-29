import structlog

from app.exceptions import ClassifierInputError, LLMServiceError
from app.llm.client import build_openai_client
from app.models.contracts import ClassifierOutput, SupportEmailInput
from app.models.prompt_config import PromptConfig

logger = structlog.get_logger(__name__)


def classify_support_email(email_text: str, prompt_config: PromptConfig) -> ClassifierOutput:
    email_input = SupportEmailInput(email_text=email_text)
    client = build_openai_client()

    logger.info(
        "classifier_request_started",
        prompt_version=prompt_config.version,
        model=prompt_config.model,
        input_chars=len(email_input.email_text),
        example_count=len(prompt_config.few_shot_examples),
    )

    messages: list[dict[str, str]] = [{"role": "system", "content": prompt_config.system_prompt}]

    for idx, instruction in enumerate(prompt_config.instructions, start=1):
        messages.append(
            {
                "role": "system",
                "content": f"Instruction {idx}: {instruction}",
            }
        )

    for example in prompt_config.few_shot_examples:
        messages.append({"role": "user", "content": example.input_email})
        messages.append(
            {
                "role": "assistant",
                "content": ClassifierOutput(
                    category=example.category,
                    summary=example.summary,
                ).model_dump_json(),
            }
        )

    category_list = ", ".join(category.value for category in prompt_config.allowed_categories)
    user_message = (
        "Classify the following customer support email and produce a concise operational summary. "
        f"You must choose exactly one category from: {category_list}.

"
        f"Customer email:
{email_input.email_text}"
    )
    messages.append({"role": "user", "content": user_message})

    try:
        response = client.beta.chat.completions.parse(
            model=prompt_config.model,
            messages=messages,
            temperature=prompt_config.temperature,
            max_tokens=prompt_config.max_output_tokens,
            response_format=ClassifierOutput,
        )
    except Exception as exc:
        logger.exception(
            "classifier_request_failed",
            prompt_version=prompt_config.version,
            model=prompt_config.model,
        )
        raise LLMServiceError(f"OpenAI classifier request failed: {exc}") from exc

    try:
        choice = response.choices[0]
        parsed = choice.message.parsed
    except (AttributeError, IndexError) as exc:
        logger.exception(
            "classifier_response_missing_parsed_output",
            prompt_version=prompt_config.version,
            model=prompt_config.model,
        )
        raise LLMServiceError("OpenAI response did not contain a parsed classifier output.") from exc

    if parsed is None:
        refusal = getattr(choice.message, "refusal", None)
        if refusal:
            logger.warning(
                "classifier_request_refused",
                prompt_version=prompt_config.version,
                model=prompt_config.model,
                refusal=refusal,
            )
            raise LLMServiceError(f"Model refused the request: {refusal}")
        raise LLMServiceError("Structured output parsing returned None.")

    try:
        result = ClassifierOutput.model_validate(parsed)
    except Exception as exc:
        logger.exception(
            "classifier_output_validation_failed",
            prompt_version=prompt_config.version,
            model=prompt_config.model,
        )
        raise ClassifierInputError(f"Parsed classifier output failed validation: {exc}") from exc

    logger.info(
        "classifier_request_succeeded",
        prompt_version=prompt_config.version,
        model=prompt_config.model,
        category=result.category.value,
        summary_length=len(result.summary),
    )
    return result
