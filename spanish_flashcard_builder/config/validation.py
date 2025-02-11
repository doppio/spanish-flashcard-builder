"""Configuration validation for Spanish Flashcard Builder."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from spanish_flashcard_builder.exceptions import ConfigurationError


@dataclass
class OpenAIConfig:
    """OpenAI API configuration."""

    model: str
    temperature: float
    max_tokens: Optional[int] = None

    def validate(self) -> None:
        """Validate OpenAI configuration.

        Raises:
            ConfigurationError: If configuration is invalid
        """
        if not self.model:
            raise ConfigurationError("OpenAI model name is required")
        if not 0 <= self.temperature <= 2:
            raise ConfigurationError("Temperature must be between 0 and 2")
        if self.max_tokens is not None and self.max_tokens <= 0:
            raise ConfigurationError("Max tokens must be positive")


@dataclass
class PathConfig:
    """Path configuration for data and output directories."""

    data_dir: Path
    output_dir: Path
    terms_dir: Path
    raw_vocab_file: Path
    sanitized_vocab_file: Path
    curator_history_file: Path
    deck_file: Path

    def validate(self) -> None:
        """Validate path configuration.

        Raises:
            ConfigurationError: If paths are invalid
        """
        # Check required directories exist
        for dir_path in [self.data_dir, self.output_dir]:
            if not dir_path.exists():
                dir_path.mkdir(parents=True)

        # Ensure parent directories exist for files
        for file_path in [
            self.raw_vocab_file,
            self.sanitized_vocab_file,
            self.curator_history_file,
            self.deck_file,
        ]:
            file_path.parent.mkdir(parents=True, exist_ok=True)


@dataclass
class AnkiConfig:
    """Anki deck configuration."""

    deck_name: str
    deck_id: int
    model_id: int

    def validate(self) -> None:
        """Validate Anki configuration.

        Raises:
            ConfigurationError: If configuration is invalid
        """
        if not self.deck_name:
            raise ConfigurationError("Deck name is required")
        if self.deck_id <= 0:
            raise ConfigurationError("Deck ID must be positive")
        if self.model_id <= 0:
            raise ConfigurationError("Model ID must be positive")


@dataclass
class ImageConfig:
    """Image processing configuration."""

    max_dimension: int

    def validate(self) -> None:
        """Validate image configuration.

        Raises:
            ConfigurationError: If configuration is invalid
        """
        if self.max_dimension <= 0:
            raise ConfigurationError("Max image dimension must be positive")
