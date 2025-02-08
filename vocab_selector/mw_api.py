import string
import requests
import json
import os

from config import MERRIAM_WEBSTER_API_KEY
from .models import Word, DictionaryEntry

def _fetch_mw_data(word):
    api_url = f"https://www.dictionaryapi.com/api/v3/references/spanish/json/{word}?key={MERRIAM_WEBSTER_API_KEY}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, json.JSONDecodeError):
        return None

def _is_valid_mw_data(mw_data):
    if not mw_data:
        return False
    if isinstance(mw_data, list) and len(mw_data) > 0:
        return isinstance(mw_data[0], dict)
    return False

def look_up(search_word):
    data = _fetch_mw_data(search_word)
    if not _is_valid_mw_data(data):
        return None
        
    # Filter entries to only include those matching our search word exactly
    matching_entries = []
    for entry in data:
        if isinstance(entry, dict):
            # Get the headword from hwi
            hwi = entry.get("hwi", {})
            headword = hwi.get("hw", "").replace("*", "")  # MW uses * for syllable breaks
            
            # Only include entries where the headword matches exactly
            if search_word == headword:
                if entry.get("fl") and entry.get("shortdef"):
                    matching_entries.append(entry)
    
    if not matching_entries:
        return None
        
    # Convert raw entries to DictionaryEntry objects
    dictionary_entries = [DictionaryEntry(entry) for entry in matching_entries]
    return Word(search_word, dictionary_entries)

def extract_audio_url(mw_data):
    if not mw_data:
        return None
    for entry in mw_data:
        if isinstance(entry, dict):
            hwi = entry.get("hwi", {})
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

def download_audio(word, word_folder, audio_url):
    """Download pronunciation audio for a word"""
    if not audio_url:
        print(f"No audio found for {word}.")
        return
    try:
        response = requests.get(audio_url)
        response.raise_for_status()
        audio_path = os.path.join(word_folder, "pronunciation.mp3")
        with open(audio_path, "wb") as f:
            f.write(response.content)
        print(f"Downloaded audio for '{word}'")
    except requests.RequestException as e:
        print(f"Error downloading audio for '{word}': {e}") 
        
def print_mw_summary(word, mw_data):
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