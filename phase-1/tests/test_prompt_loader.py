from pathlib import Path

import pytest

from app.exceptions import PromptConfigError
from app.prompts.loader import load_prompt_config


def test_load_prompt_config_success():
    config = load_prompt_config("prompts/support_classifier_v1.yaml")
    assert config.version == "support-email-classifier-v1.0.0"
    assert config.model == "gpt-4o-mini"
    assert len(config.few_shot_examples) >= 1


def test_load_prompt_config_missing_file():
    with pytest.raises(PromptConfigError):
        load_prompt_config("prompts/does_not_exist.yaml")


def test_load_prompt_config_invalid_extension(tmp_path: Path):
    invalid_file = tmp_path / "prompt.txt"
    invalid_file.write_text("version: v1", encoding="utf-8")
    with pytest.raises(PromptConfigError):
        load_prompt_config(invalid_file)
