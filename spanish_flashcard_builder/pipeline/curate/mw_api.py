import json
import string
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

from spanish_flashcard_builder.config import api_keys, paths

from .models import DictionaryEntry, DictionaryTerm


def _fetch_mw_data(word: str) -> Optional[List[Dict[str, Any]]]:
    """Fetches data from the Merriam-Webster API for a given word."""

    api_url = f"https://www.dictionaryapi.com/api/v3/references/spanish/json/{word}?key={api_keys.merriam_webster}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, list):
            return None
        return data
    except (requests.RequestException, json.JSONDecodeError):
        return None


def look_up(search_word: str) -> Optional[DictionaryTerm]:
    """Gets valid Merriam-Webster data for a search word."""

    data = _fetch_mw_data(search_word)
    if not data or not isinstance(data, list) or not isinstance(data[0], dict):
        return None

    matching_entries = []
    for entry in data:
        if isinstance(entry, dict):
            if entry.get("meta", {}).get("lang") != "es":
                continue

            headword = entry.get("hwi", {}).get("hw", "").replace("*", "")

            if search_word == headword:
                if entry.get("fl") and entry.get("shortdef"):
                    matching_entries.append(entry)

    if not matching_entries:
        return None

    dictionary_entries = [DictionaryEntry(entry) for entry in matching_entries]
    return DictionaryTerm(search_word, dictionary_entries)


def _extract_audio_url(mw_data: Dict) -> Optional[str]:
    """Extracts the audio URL from Merriam-Webster data."""

    if not mw_data:
        return None
    if isinstance(mw_data, dict):
        hwi = mw_data.get("hwi", {})
        prs = hwi.get("prs", [])
        for pr in prs:
            sound = pr.get("sound", {})
            audio = sound.get("audio")
            if audio:
                if audio.startswith("bix"):
                    subdirectory = "bix"
                elif audio.startswith("gg"):
                    subdirectory = "gg"
                elif audio[0].isdigit() or audio[0] in string.punctuation:
                    subdirectory = "number"
                else:
                    subdirectory = audio[0]
                return f"https://media.merriam-webster.com/audio/prons/es/me/mp3/{subdirectory}/{audio}.mp3"
    return None


def download_audio(entry: DictionaryEntry, folder: str) -> None:
    """Downloads pronunciation audio for a word."""

    word = entry.headword
    audio_url = _extract_audio_url(entry.raw_data)
    if not audio_url:
        print(f"No audio found for {word}.")
        return
    try:
        response = requests.get(audio_url)
        response.raise_for_status()
        folder_path = Path(folder)
        audio_path = folder_path / paths.get_pronunciation_filename(folder_path)
        with open(audio_path, "wb") as f:
            f.write(response.content)
        print(f"Downloaded audio for '{word}'")
    except requests.RequestException as e:
        print(f"Error downloading audio for '{word}': {e}")


def log_mw_data_summary(word: str, mw_data: List[Dict]) -> None:
    """Prints a summary of the Merriam-Webster data for a word."""

    print("\n--- Merriam-Webster Data ---")
    if not mw_data:
        print("No data available.")
        return
    entry = mw_data[0] if isinstance(mw_data, list) and mw_data else None
    if entry and isinstance(entry, dict):
        pos = entry.get("fl", "Unknown")
        shortdef = entry.get("shortdef", [])
        print(f"Word: \033[1m{word}\033[0m ({pos})")  # Bold using ANSI escape codes
        if shortdef:
            print("Definitions:")
            for d in shortdef:
                print(f" - {d}")
        else:
            print("No definitions available.")
    else:
        print("No valid entry found.")
    print("----------------------------")
