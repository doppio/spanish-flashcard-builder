import os
import json
import tempfile
import subprocess

class JSONFileEditor:
    def load_json(self, path):
        """Load and parse JSON from file."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading JSON data: {e}")
            return None

    def save_json(self, path, data):
        """Save data as formatted JSON to file."""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error saving JSON data: {e}")
            return False

    def edit_json_in_editor(self, data):
        """Open system text editor for JSON modification."""
        editor = os.environ.get('EDITOR', 'vim')
        
        with tempfile.NamedTemporaryFile(suffix='.json', mode='w', delete=False) as tf:
            json.dump(data, tf, indent=2, ensure_ascii=False)
            temp_path = tf.name

        try:
            if subprocess.run([editor, temp_path]).returncode == 0:
                with open(temp_path, 'r', encoding='utf-8') as f:
                    try:
                        modified_data = json.load(f)
                        data.clear()
                        data.update(modified_data)
                        return True
                    except json.JSONDecodeError as e:
                        print(f"Error: Invalid JSON format after editing: {e}")
                        return False
            return False
        finally:
            os.unlink(temp_path)