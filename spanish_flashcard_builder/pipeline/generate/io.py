import json
import logging
import os
import subprocess
import tempfile
from typing import Any, Dict, Optional


class JSONFileEditor:
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

    def edit_json_in_editor(self, data: Dict[str, Any]) -> bool:
        """Open system text editor for JSON modification."""
        # First display the content
        print("\nGenerated content:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print("\nPress SPACE to accept, 'e' to edit, any other key to reject")

        ch = self._get_single_keypress()

        if ch == " ":  # Space to accept
            return True
        elif ch.lower() == "e":  # 'e' to edit
            return self._edit_in_external_editor(data)
        else:  # Any other key to reject
            return False
