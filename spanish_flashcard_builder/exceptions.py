"""Custom exceptions for the Spanish Flashcard Builder."""


class SpanishFlashcardError(Exception):
    """Base exception for all Spanish Flashcard Builder errors."""

    pass


class ContentGenerationError(SpanishFlashcardError):
    """Raised when content generation fails."""

    pass


class ConfigurationError(SpanishFlashcardError):
    """Raised when configuration is invalid or missing."""

    pass


class MediaProcessingError(SpanishFlashcardError):
    """Raised when processing media files fails."""

    pass


class ValidationError(SpanishFlashcardError):
    """Raised when data validation fails."""

    pass
