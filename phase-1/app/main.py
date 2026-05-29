import argparse
import json
import sys
from pathlib import Path

from app.exceptions import AppError
from app.llm.classifier import classify_support_email
from app.logging_config import configure_logging
from app.prompts.loader import DEFAULT_PROMPT_PATH, load_prompt_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Phase 1 support email classifier.")
    parser.add_argument("--email", required=True, help="Raw customer support email text to classify.")
    parser.add_argument(
        "--prompt-file",
        default=str(DEFAULT_PROMPT_PATH),
        help="Path to the prompt YAML file.",
    )
    parser.add_argument(
        "--output-file",
        default=None,
        help="Optional path to save the structured JSON result.",
    )
    return parser


def main() -> int:
    configure_logging()
    parser = build_parser()
    args = parser.parse_args()

    try:
        prompt_config = load_prompt_config(args.prompt_file)
        result = classify_support_email(email_text=args.email, prompt_config=prompt_config)
    except AppError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    payload = {
        "prompt_version": prompt_config.version,
        "model": prompt_config.model,
        "result": result.model_dump(),
    }
    rendered = json.dumps(payload, indent=2)
    print(rendered)

    if args.output_file:
        output_path = Path(args.output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered + "
", encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
