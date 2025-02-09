import os
import json
import shutil
import logging

from .mw_api import download_audio, extract_audio_url
from .models import DictionaryEntry

class VocabBank:
    """Handles saving dictionary entries and their audio files to disk."""
    
    def __init__(self, base_dir: str) -> None:
        """Initializes with base directory for saving entries."""
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)

    def entry_exists(self, entry_id: str) -> bool:
        """Checks if an entry exists."""
        return os.path.exists(self._get_entry_path(entry_id))

    def delete_entry(self, entry_id: str) -> None:
        """Removes all saved data for an entry."""
        entry_dir = self._get_entry_path(entry_id)
        if os.path.exists(entry_dir):
            try:
                shutil.rmtree(entry_dir)
                logging.info(f"Deleted folder for entry '{entry_id}'")
            except Exception as e:
                logging.error(f"Error deleting folder for entry '{entry_id}': {e}")
        else:
            logging.warning(f"Entry directory '{entry_dir}' does not exist.")

    def save_entry(self, entry: DictionaryEntry) -> None:
        """Saves a dictionary entry using the DictionaryEntry model"""
        entry_dir = self._get_entry_path(entry.id)
        os.makedirs(entry_dir, exist_ok=True)
        
        print(f"Saving entry '{entry.id}'")
        with open(os.path.join(entry_dir, 'mw_entry.json'), 'w') as f:
            json.dump(entry.raw_data, f, indent=2)
            
        audio_url = extract_audio_url([entry.raw_data])
        if audio_url:
            download_audio(entry.headword, entry_dir, audio_url)
        
    def has_entry(self, entry_id: str) -> bool:
        """Checks if an entry ID has already been saved"""
        return os.path.exists(self._get_entry_path(entry_id))

    def _get_entry_path(self, entry_id: str) -> str:
        """Get directory path for a dictionary entry."""
        return os.path.join(self.base_dir, str(entry_id))