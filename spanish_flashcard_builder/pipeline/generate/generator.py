"""Content generation for vocabulary terms."""

import json
import logging
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, cast

from spanish_flashcard_builder.config import paths
from spanish_flashcard_builder.exceptions import ContentGenerationError

from .data_loader import DictionaryDataLoader
from .openai_api import OpenAIClient
from .persistence import ContentPersistence

logger = logging.getLogger(__name__)


def get_key_press() -> str:
    """Gets single keypress from the user."""
    if os.name == "nt":
        import msvcrt

        msvcrt_any = cast(Any, msvcrt)  # Cast to Any to handle missing type hints
        return cast(str, msvcrt_any.getch().decode())
    else:
        import termios
        import tty

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class ContentGenerator:
    """Generates AI content for vocabulary terms."""

    def __init__(self) -> None:
        self.openai_client = OpenAIClient()
        self.data_loader = DictionaryDataLoader()
        self.persistence = ContentPersistence()

    def process_all_pending(self) -> bool:
        """Generate content for all pending vocabulary words."""
        terms_dir = Path(paths.terms_dir)
        if not terms_dir.exists():
            logger.error(f"Terms directory not found: {terms_dir}")
            return False

        words_processed = False
        for folder_path in self._get_pending_folders(terms_dir):
            logger.info(f"Generating content for: {folder_path.name}")
            try:
                words_processed |= self.generate_word(folder_path)
            except ContentGenerationError as e:
                logger.error(f"Failed to generate content for {folder_path}: {e}")
                continue

        return words_processed

    def generate_word(self, folder_path: Path) -> bool:
        """Generate content for a single vocabulary word."""
        print(f"Generating content for '{folder_path.name}'...")
        try:
            entry = self.data_loader.load_entry(folder_path)
            if not entry:
                raise ContentGenerationError("Failed to load dictionary entry")

            generated_data = self.openai_client.generate_term(
                entry.word, entry.part_of_speech, entry.definitions
            )
            term_dict = generated_data.to_dict()

            content_accepted = self.review_content(term_dict)
            if not content_accepted:
                return False

            return self.persistence.save_content(folder_path, term_dict)

        except Exception as e:
            logger.exception(f"Unexpected error generating content for '{folder_path}'")
            raise ContentGenerationError(str(e)) from e

    def review_content(self, term_data: Dict[str, Any]) -> bool:
        """Review generated content with user.

        Returns:
            True if content was approved, False if cancelled
        """
        print("\nGenerated flashcard content:")
        print(json.dumps(term_data, indent=2, ensure_ascii=False))
        print("\nPress SPACE to continue, 'e' to edit, any other key to cancel")

        user_input = get_key_press()
        if user_input == " ":
            return True
        elif user_input == "e":
            logger.info("Opening editor for content review...")
            return self._edit_in_editor(term_data)
        else:
            logger.info("Content generation was cancelled by user")
            return False

    def _edit_in_editor(self, data: Dict[str, Any]) -> bool:
        """Edit JSON data in external editor."""
        editor = os.environ.get("EDITOR", "vim")

        with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as tf:
            json.dump(data, tf, indent=2, ensure_ascii=False)
            temp_path = tf.name

        try:
            if subprocess.run([editor, temp_path]).returncode == 0:
                with open(temp_path, encoding="utf-8") as f:
                    edited_data = json.load(f)
                data.clear()
                data.update(edited_data)
                return True
            return False
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON after editing: {e}")
            return False
        finally:
            os.unlink(temp_path)

    def _get_pending_folders(self, terms_dir: Path) -> list[Path]:
        """Get list of folders that need content generation."""
        return [
            path
            for path in sorted(terms_dir.iterdir())
            if path.is_dir() and self.persistence.needs_generation(path)
        ]
