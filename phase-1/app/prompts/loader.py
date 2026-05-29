from pathlib import Path

import yaml
from pydantic import ValidationError

from app.exceptions import PromptConfigError
from app.models.prompt_config import PromptConfig


DEFAULT_PROMPT_PATH = Path("prompts/support_classifier_v1.yaml")


def load_prompt_config(prompt_file: str | Path = DEFAULT_PROMPT_PATH) -> PromptConfig:
    path = Path(prompt_file)

    if not path.exists():
        raise PromptConfigError(f"Prompt config file not found: {path}")
    if path.suffix.lower() not in {".yaml", ".yml"}:
        raise PromptConfigError(f"Prompt config must be a YAML file: {path}")

    try:
        with path.open("r", encoding="utf-8") as handle:
            raw = yaml.safe_load(handle)
    except yaml.YAMLError as exc:
        raise PromptConfigError(f"Failed to parse YAML in {path}: {exc}") from exc
    except OSError as exc:
        raise PromptConfigError(f"Failed to read prompt config {path}: {exc}") from exc

    if raw is None:
        raise PromptConfigError(f"Prompt config file is empty: {path}")
    if not isinstance(raw, dict):
        raise PromptConfigError(f"Prompt config root must be a mapping/object: {path}")

    try:
        return PromptConfig.model_validate(raw)
    except ValidationError as exc:
        raise PromptConfigError(f"Prompt config validation failed for {path}: {exc}") from exc
