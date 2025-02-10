import logging
import os
from pathlib import Path
from typing import Any, Dict

import yaml
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_FILENAME = "config.yml"

# YAML config keys
PATHS = "paths"
DATA = "data"
OUTPUT = "output"
TERMS = "terms"
COMPONENTS = "components"
DIR = "dir"
ANKI_DECK = "anki_deck"
SPACY = "spacy"
OPENAI = "openai"
GOOGLE = "google"
IMAGES = "images"


class ConfigError(Exception):
    """Raised when there's an error in configuration."""

    pass


# Internal classes and functions
class _YamlConfig:
    """Internal class to handle YAML configuration loading and access."""

    def __init__(self, config_filename: str) -> None:
        self.config: Dict[str, Any] = {}
        self.load(config_filename)

    def load(self, config_file: str) -> None:
        """Load and parse the YAML configuration file."""
        config_path = PROJECT_ROOT / config_file

        try:
            with open(config_path) as f:
                self.config = yaml.safe_load(f)
        except (FileNotFoundError, yaml.YAMLError) as e:
            logging.error(f"Error loading config file at {config_path}:\n{e}")
            raise ConfigError(f"Failed to load config: {e}") from e

    def get_value(self, *keys: str, default: Any = None) -> Any:
        """Safely get nested config values with optional default."""
        value = self.config
        for key in keys[:-1]:  # All but last key
            if not isinstance(value, dict):
                raise ConfigError(f"Expected dict at key '{key}', got {type(value)}")
            value = value.get(key, {})
        return value.get(keys[-1], default) if keys else value

    def get_path(self, *keys: str) -> Path:
        """Get a path value from config, joining with PROJECT_ROOT."""
        return PROJECT_ROOT / self.get_value(*keys)


# Initialize Config instance
config = _YamlConfig(CONFIG_FILENAME)


class _Paths:
    """Paths configuration for data and output directories."""

    @staticmethod
    def _ensure_dir(path: Path) -> None:
        """Ensure directory exists, create if it doesn't."""
        path.mkdir(parents=True, exist_ok=True)

    def __init__(self):
        # Data paths
        self.data_dir = config.get_path(PATHS, DATA, DIR)
        self._ensure_dir(self.data_dir)
        self.raw_vocab = self.data_dir / config.get_value(PATHS, DATA, "raw_vocab")
        self.cleaned_vocab = self.data_dir / config.get_value(
            PATHS, DATA, "cleaned_vocab"
        )
        self.selector_history = self.data_dir / config.get_value(
            PATHS, DATA, "selector_history"
        )

        # Output paths
        self.output_dir = config.get_path(PATHS, OUTPUT, DIR)
        self._ensure_dir(self.output_dir)
        self.terms_dir = self.output_dir / config.get_value(PATHS, OUTPUT, TERMS, DIR)
        self._ensure_dir(self.terms_dir)
        self.deck_file = self.output_dir / config.get_value(PATHS, OUTPUT, "deck")

        # Term component filenames
        self.dictionary_entry_filename = config.get_value(
            PATHS, OUTPUT, TERMS, COMPONENTS, "dictionary_entry"
        )
        self.augmented_term_filename = config.get_value(
            PATHS, OUTPUT, TERMS, COMPONENTS, "augmented_term"
        )
        self.pronunciation_filename = config.get_value(
            PATHS, OUTPUT, TERMS, COMPONENTS, "pronunciation"
        )
        self.image_filename = config.get_value(
            PATHS, OUTPUT, TERMS, COMPONENTS, "image"
        )


class _Image:
    """Image configuration."""

    max_dimension: int = config.get_value(IMAGES, "max_dimension")


class _Anki:
    """Anki deck configuration."""

    deck_name: str = config.get_value(ANKI_DECK, "deck_name")
    deck_id: int = config.get_value(ANKI_DECK, "deck_id")


class _Spacy:
    """SpaCy model configuration."""

    def __init__(self):
        self.model_name: str = config.get_value(SPACY, "model_name")


class _OpenAI:
    """OpenAI API configuration."""

    def __init__(self):
        self.model: str = config.get_value(OPENAI, "model")
        self.temperature: float = config.get_value(OPENAI, "temperature")
        self.validate()

    def validate(self) -> None:
        """Validate OpenAI configuration values."""
        if not 0 <= self.temperature <= 1:
            raise ConfigError(
                f"OpenAI temperature must be between 0 and 1, got {self.temperature}"
            )
        if not self.model:
            raise ConfigError("OpenAI model name cannot be empty")


class _Keys:
    """API key configuration."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_keys()
        return cls._instance

    def _init_keys(self) -> None:
        """Initialize and validate API keys from environment variables."""
        self.merriam_webster = self._get_required_key("MERRIAM_WEBSTER_API_KEY")
        self.openai = self._get_required_key("OPENAI_API_KEY")
        self.google_search = self._get_required_key("GOOGLE_API_KEY")
        self.google_search_engine_id = self._get_required_key("GOOGLE_SEARCH_ENGINE_ID")

    @staticmethod
    def _get_required_key(env_var: str) -> str:
        """Get a required API key from environment variables."""
        key = os.getenv(env_var)
        if not key:
            raise ConfigError(f"Missing required environment variable: {env_var}")
        return key


# Configuration instances for external use
paths = _Paths()
api_keys = _Keys()
spacy_config = _Spacy()
openai_config = _OpenAI()
image_config = _Image()
