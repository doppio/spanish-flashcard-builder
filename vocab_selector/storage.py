import os
import json
import shutil

from .mw_api import download_audio, extract_audio_url

class VocabStorage:
    """Handles file system operations for vocabulary words"""
    def __init__(self, vocab_dir):
        self.vocab_dir = vocab_dir
        os.makedirs(vocab_dir, exist_ok=True)

    def _safe_folder_name(self, word):
        return "".join(c if c.isalnum() else "_" for c in word)

    def _get_word_folder(self, word):
        return os.path.join(self.vocab_dir, self._safe_folder_name(word))

    def exists(self, word):
        return os.path.exists(self._get_word_folder(word))

    def save(self, vocab_word):
        folder = self._get_word_folder(vocab_word.word)
        os.makedirs(folder, exist_ok=True)
        
        # Save MW data
        data_path = os.path.join(folder, "mw_data.json")
        try:
            with open(data_path, "w", encoding="utf-8") as f:
                json.dump(vocab_word.mw_data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving MW data for {vocab_word.word}: {e}")

        # Download audio
        audio_url = extract_audio_url(vocab_word.mw_data)
        download_audio(vocab_word.word, folder, audio_url)

    def remove(self, word):
        folder = self._get_word_folder(word)
        if os.path.exists(folder):
            try:
                shutil.rmtree(folder)
                print(f"Removed folder for '{word}'.")
            except Exception as e:
                print(f"Error removing folder for '{word}': {e}") 