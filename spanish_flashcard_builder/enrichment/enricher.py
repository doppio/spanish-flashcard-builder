import os
from spanish_flashcard_builder.config import OPENAI_API_KEY, VOCAB_BANK_DIR
from .openai_api import OpenAIClient
from .io import JSONFileEditor

class VocabEnricher:
    def __init__(self, vocab_dir=VOCAB_BANK_DIR):
        self.vocab_dir = vocab_dir
        self.openai_client = OpenAIClient(OPENAI_API_KEY)
        self.json_editor = JSONFileEditor()

    def process_all_pending(self):
        """Enrich all pending vocabulary words that need processing."""
        words_processed = False
        
        # Sort the directory listing alphabetically
        for folder_name in sorted(os.listdir(self.vocab_dir)):
            folder_path = os.path.join(self.vocab_dir, folder_name)
            if self._needs_enrichment(folder_path):
                print(f"\nEnriching word in: {folder_path}")
                words_processed |= self.enrich_word(folder_path)
                
        return words_processed

    def enrich_word(self, folder_path):
        """Enrich a single vocabulary word with additional data."""
        # Load and validate MW data
        mw_data = self.json_editor.load_json(self._get_mw_path(folder_path))

        # Extract word information
        word, pos, definitions = self._parse_mw_data(mw_data)
        if not word:
            return False

        # Generate and save enrichment data
        return self._generate_and_save_enrichment(folder_path, word, pos, definitions)

    def _needs_enrichment(self, folder_path):
        """Check if a word needs enrichment data."""
        if not os.path.isdir(folder_path):
            return False
            
        mw_path = self._get_mw_path(folder_path)
        flashcard_path = self._get_flashcard_path(folder_path)
        return os.path.exists(mw_path) and not os.path.exists(flashcard_path)

    def _parse_mw_data(self, entry):
        """Parse Merriam-Webster API response data."""
        try:
            # First check if the data is actually a string
            if isinstance(entry, str):
                print(f"Unexpected MW data format: {mw_data}")
                return None, None, None
                
            # Verify we have the expected structure before accessing
            if not isinstance(entry, dict) or 'meta' not in entry:
                print(f"Invalid MW entry format: {entry}")
                return None, None, None
                
            return (
                entry['meta']['id'].split(':')[0],  # word
                entry.get('fl', ''),                # part of speech
                entry.get('shortdef', [])           # definitions
            )
        except (IndexError, KeyError, AttributeError) as e:
            print(f"Error parsing MW data: {e}")
            return None, None, None

    def _generate_and_save_enrichment(self, folder_path, word, pos, definitions):
        """Generate AI enrichment data and save after user review."""
        # Get enrichment data from OpenAI
        enrichment_data = self.openai_client.get_enrichment_data(word, pos, definitions)
        
        # Prepare final data
        enrichment_dict = {
            'word': word,
            **enrichment_data.to_dict()
        }

        # Let user edit and save
        if not self.json_editor.edit_json_in_editor(enrichment_dict):
            print("Enrichment data editing was cancelled")
            return False

        return self.json_editor.save_json(
            self._get_flashcard_path(folder_path),
            enrichment_dict
        )

    def _get_mw_path(self, folder_path):
        return os.path.join(folder_path, "mw_entry.json")

    def _get_flashcard_path(self, folder_path):
        return os.path.join(folder_path, "flashcard_data.json")