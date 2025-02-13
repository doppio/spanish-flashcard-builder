import json
import logging
import os
import subprocess
import tempfile
from typing import Any, Dict

from spanish_flashcard_builder.utils import get_key_press


class ContentReviewer:
    """Handles user review of generated content."""

    def review_content(self, term_data: Dict[str, Any]) -> bool:
        """Review generated content with user."""
        print("\nGenerated flashcard content:")
        print(json.dumps(term_data, indent=2, ensure_ascii=False))
        print("\nPress SPACE to continue, 'e' to edit, any other key to cancel")

        user_input = get_key_press()
        if user_input == " ":
            return True
        elif user_input == "e":
            logging.info("Opening editor for content review...")
            return self._edit_in_editor(term_data)
        else:
            logging.info("Content generation was cancelled by user")
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
            logging.error(f"Invalid JSON after editing: {e}")
            return False
        finally:
            os.unlink(temp_path)
