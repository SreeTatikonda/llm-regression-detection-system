class AppError(Exception):
    """Base exception for application-level failures."""


class SettingsError(AppError):
    """Raised when application settings are invalid."""


class PromptConfigError(AppError):
    """Raised when a prompt config file is missing or invalid."""


class ClassifierInputError(AppError):
    """Raised when the classifier input is invalid."""


class LLMServiceError(AppError):
    """Raised when the LLM provider call fails or returns unusable data."""


class SmokeTestError(AppError):
    """Raised when local smoke tests fail."""
