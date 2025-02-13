"""Data loading and parsing for content generation."""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from spanish_flashcard_builder.config import paths
from spanish_flashcard_builder.exceptions import ValidationError

logger = logging.getLogger(__name__)


@dataclass
class DictionaryEntry:
    """Parsed dictionary entry data."""

    word: str
    part_of_speech: str
    definitions: List[str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DictionaryEntry":
        """Create instance from Merriam-Webster dictionary data.

        Args:
            data: Dictionary containing Merriam-Webster API response data

        Raises:
            ValidationError: If required fields are missing or have invalid types
        """
        required_fields = ["meta", "fl", "shortdef"]
        missing = [k for k in required_fields if k not in data]
        if missing:
            raise ValidationError(
                f"Missing required fields in dictionary data: {', '.join(missing)}"
            )

        if "id" not in data["meta"]:
            raise ValidationError("Missing word id in meta data")

        return cls(
            word=data["meta"]["id"],
            part_of_speech=data["fl"],
            definitions=data["shortdef"],
        )


class DictionaryDataLoader:
    """Handles loading and parsing of dictionary data."""

    def load_entry(self, folder_path: Path) -> Optional[DictionaryEntry]:
        """Load and parse dictionary entry from a folder.

        Args:
            folder_path: Path to the folder containing dictionary data

        Returns:
            Parsed dictionary entry or None if loading/parsing fails

        Raises:
            ValidationError: If required data is missing or invalid
        """
        try:
            data = self._load_json(folder_path)
            if not data:
                return None
            return DictionaryEntry.from_dict(data)
        except ValidationError as e:
            logger.error(f"Invalid dictionary entry data: {e}")
            return None
        except (OSError, IOError) as e:
            logger.error(f"IO error loading dictionary entry: {e}")
            return None

    def _load_json(self, folder_path: Path) -> Optional[Dict[str, Any]]:
        """Load JSON data from dictionary file."""
        try:
            file_path = folder_path / paths.dictionary_entry_filename
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    logger.error(
                        f"Invalid JSON structure: expected dict, got {type(data)}"
                    )
                    return None
                return data
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in dictionary entry: {e}")
            return None
        except (OSError, IOError) as e:
            logger.error(f"Error loading dictionary file: {e}")
            return None
