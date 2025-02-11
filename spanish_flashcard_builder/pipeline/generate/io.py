"""File I/O utilities for content generation."""

import json
import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

from spanish_flashcard_builder.exceptions import ValidationError

logger = logging.getLogger(__name__)


class JSONFileEditor:
    """Interactive JSON file editor."""

    def __init__(self, editor_cmd: Optional[str] = None) -> None:
        """Initialize the JSON file editor.

        Args:
            editor_cmd: Command to launch the editor. If None, uses EDITOR
                env var or 'vim'.
        """
        editor = editor_cmd or os.environ.get("EDITOR", "vim")
        assert isinstance(editor, str)
        self.editor_cmd: str = editor

    def edit_json_in_editor(self, data: Dict[str, Any]) -> bool:
        """Open JSON data in an editor for user review/modification.

        Args:
            data: Dictionary to edit

        Returns:
            True if the edit was successful and saved, False if cancelled

        Raises:
            ValidationError: If the edited JSON is invalid
        """
        try:
            # Create temp file
            with tempfile.NamedTemporaryFile(
                suffix=".json", mode="w", delete=False
            ) as temp_file:
                # Write initial JSON
                json.dump(data, temp_file, indent=2, ensure_ascii=False)
                temp_path = temp_file.name

            # Get file modification time
            mtime_before = Path(temp_path).stat().st_mtime

            # Open editor
            try:
                subprocess.run([self.editor_cmd, temp_path], check=True)
            except subprocess.CalledProcessError as e:
                logger.error(f"Editor process failed: {e}")
                return False

            # Check if file was modified
            mtime_after = Path(temp_path).stat().st_mtime
            if mtime_after == mtime_before:
                logger.info("No changes made in editor")
                return False

            # Read and validate edited content
            with open(temp_path, encoding="utf-8") as f:
                try:
                    edited_data = json.load(f)
                except json.JSONDecodeError as err:
                    raise ValidationError(f"Invalid JSON: {err}") from err

            # Validate structure
            self._validate_content(edited_data)
            data.clear()
            data.update(edited_data)
            return True

        finally:
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except Exception as e:
                logger.warning(f"Failed to delete temp file {temp_path}: {e}")

    def _validate_content(self, data: Dict[str, Any]) -> None:
        """Validate the structure of edited content.

        Args:
            data: The edited data to validate

        Raises:
            ValidationError: If the content structure is invalid
        """
        required_fields = {
            "term": str,
            "definitions": str,
            "frequency_rating": int,
            "example_sentences": list,
            "image_search_query": str,
            "part_of_speech": str,
        }

        # Check required fields and types
        for field, expected_type in required_fields.items():
            if field not in data:
                raise ValidationError(f"Missing required field: {field}")
            if not isinstance(data[field], expected_type):
                raise ValidationError(
                    f"Invalid type for {field}: expected {expected_type.__name__}, "
                    f"got {type(data[field]).__name__}"
                )

        # Validate example sentences
        for i, sentence in enumerate(data["example_sentences"]):
            if not isinstance(sentence, dict):
                raise ValidationError(
                    f"Example sentence {i} must be a dictionary with 'es' and 'en' keys"
                )
            if "es" not in sentence or "en" not in sentence:
                raise ValidationError(
                    f"Example sentence {i} missing required 'es' or 'en' translation"
                )

        # Validate frequency rating range
        if not 1 <= data["frequency_rating"] <= 10:
            raise ValidationError("Frequency rating must be between 1 and 10")

    def load_json(self, path: str) -> Optional[Dict[str, Any]]:
        """Load and parse JSON from file."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    logging.error(f"Error: Expected dict, got {type(data)}")
                    return None
                return data
        except (IOError, json.JSONDecodeError) as e:
            logging.error(f"Error loading JSON data: {e}")
            return None

    def save_json(self, path: str, data: Dict[str, Any]) -> bool:
        """Save data as formatted JSON to file."""
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            logging.error(f"Error saving JSON data: {e}")
            return False

    def _get_single_keypress(self) -> str:
        """Get a single keypress from the user."""
        try:
            import sys
            import termios
            import tty

            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch
        except (ImportError, termios.error):
            return input(
                "Enter SPACE to accept, 'e' to edit, any other key to reject: "
            ).lower()

    def _edit_in_external_editor(self, data: Dict[str, Any]) -> bool:
        """Edit JSON data in external editor."""
        editor = os.environ.get("EDITOR", "vim")
        with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as tf:
            json.dump(data, tf, indent=2, ensure_ascii=False)
            temp_path = tf.name

        try:
            if subprocess.run([editor, temp_path]).returncode == 0:
                return self._load_and_validate_json(temp_path, data)
            return False
        finally:
            os.unlink(temp_path)

    def _load_and_validate_json(
        self, file_path: str, target_dict: Dict[str, Any]
    ) -> bool:
        """Load and validate JSON from file, updating target dict if valid."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                modified_data = json.load(f)
                if not isinstance(modified_data, dict):
                    print("\nError: Expected dict, got {type(modified_data)}")
                    return False
                target_dict.clear()
                target_dict.update(modified_data)
                return True
        except json.JSONDecodeError as e:
            print(f"\nError: Invalid JSON format after editing: {e}")
            return False
