# LLM Regression Guard - Phase 1

Phase 1 implements the feature under test for a future model regression detection system:
- A customer support email classifier
- Versioned YAML prompt configs
- Typed input/output contracts with Pydantic
- Structured-output parsing through the OpenAI Python SDK
- Structured logging and a local smoke-test script

## What this phase does

Given a customer support email, the classifier returns:
- `category`: one of `billing`, `technical`, `account`, `general`
- `summary`: a single-sentence operational summary

## Project structure

```text
app/
  settings.py
  exceptions.py
  logging_config.py
  main.py
  smoke_test.py
  models/
    prompt_config.py
    contracts.py
  prompts/
    loader.py
  llm/
    client.py
    classifier.py
prompts/
  support_classifier_v1.yaml
tests/
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.example .env
```

Set `OPENAI_API_KEY` in `.env`.

## Run single example

```bash
python -m app.main --email "I was charged twice for my subscription and need a refund."
```

## Run smoke test

```bash
python -m app.smoke_test
```

## Test

```bash
pytest
```
