import os
from spanish_flashcard_builder.config import (
    api_keys,
    paths
)
from .openai_api import OpenAIClient
from .io import JSONFileEditor

class VocabAugmentor:
    def __init__(self, vocab_dir=None):
        self.vocab_dir = vocab_dir or paths.terms_dir
        self.openai_client = OpenAIClient(api_keys.openai)
        self.json_editor = JSONFileEditor()

    def process_all_pending(self):
        """Augment all pending vocabulary words that need processing."""
        words_processed = False
        
        # Sort the directory listing alphabetically
        for folder_name in sorted(os.listdir(self.vocab_dir)):
            folder_path = os.path.join(self.vocab_dir, folder_name)
            if self._needs_augmentation(folder_path):
                print(f"Augmenting word in: {folder_path}")
                words_processed |= self.augment_word(folder_path)
                
        return words_processed

    def augment_word(self, folder_path):
        """Augment a single vocabulary word with additional data."""
        mw_data = self.json_editor.load_json(self._get_mw_path(folder_path))

        word, pos, definitions = self._parse_mw_data(mw_data)
        if not word:
            return False

        return self._generate_augmented_term_file(folder_path, word, pos, definitions)

    def _needs_augmentation(self, folder_path):
        if not os.path.isdir(folder_path):
            return False
            
        mw_path = self._get_mw_path(folder_path)
        flashcard_path = self._get_flashcard_path(folder_path)
        return os.path.exists(mw_path) and not os.path.exists(flashcard_path)

    def _parse_mw_data(self, entry):
        """Parse Merriam-Webster API response data."""
        try:
            if isinstance(entry, str):
                print(f"Unexpected Merriam-Webster entry format: {entry}")
                return None, None, None
                
            # Verify we have the expected structure before accessing
            if not isinstance(entry, dict) or 'meta' not in entry:
                print(f"Invalid Merriam-Webster entry format: {entry}")
                return None, None, None
                
            return (
                entry['meta']['id'].split(':')[0],  # word
                entry.get('fl', ''),                # part of speech
                entry.get('shortdef', [])           # definitions
            )
        except (IndexError, KeyError, AttributeError) as e:
            print(f"Error parsing MW data: {e}")
            return None, None, None

    def _generate_augmented_term_file(self, folder_path, word, pos, definitions):
        """Generate AI-augmented data and save after user review."""
        augmented_data = self.openai_client.augment_term(word, pos, definitions)
        
        augmented_term = {
            'word': word,
            **augmented_data.to_dict()
        }

        # Let user edit and save
        if not self.json_editor.edit_json_in_editor(augmented_term):
            print("Augmented data editing was cancelled")
            return False

        return self.json_editor.save_json(
            self._get_flashcard_path(folder_path),
            augmented_term
        )

    def _get_mw_path(self, folder_path):
        return os.path.join(folder_path, 'merriam_webster_entry.json')

    def _get_flashcard_path(self, folder_path):
        return os.path.join(folder_path, 'augmented_term.json')