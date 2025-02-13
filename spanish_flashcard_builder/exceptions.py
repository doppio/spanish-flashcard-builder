"""Custom exceptions for the Spanish Flashcard Builder."""


class SpanishFlashcardError(Exception):
    """Base exception for all Spanish Flashcard Builder errors."""

    pass


class IoError(SpanishFlashcardError):
    """Raised when an I/O operation fails."""

    pass
