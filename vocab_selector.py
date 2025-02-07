#!/usr/bin/env python3
import os
import json
import requests
import string
import sys
import spacy
from config import MERRIAM_WEBSTER_API_KEY, VOCAB_FILE, VOCAB_DIR, CHECKPOINT_FILE

nlp = spacy.load("es_core_news_md")

def load_vocab_list():
    vocab_list = []
    try:
        with open(VOCAB_FILE, encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split()
                if parts:
                    word = parts[0]
                    vocab_list.append(word)
    except IOError as e:
        print(f"Error loading vocabulary file: {e}")
        sys.exit(1)
    return vocab_list

def load_checkpoint():
    try:
        if os.path.exists(CHECKPOINT_FILE):
            with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {'current_index': 0, 'decisions': {}}
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error loading checkpoint: {e}")
        return {'current_index': 0, 'decisions': {}}

def save_checkpoint(checkpoint):
    try:
        with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
            json.dump(checkpoint, f, indent=2)
    except IOError as e:
        print(f"Error saving checkpoint: {e}")

def fetch_mw_data(word):
    api_url = f"https://www.dictionaryapi.com/api/v3/references/spanish/json/{word}?key={MERRIAM_WEBSTER_API_KEY}"
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return None
    except json.JSONDecodeError as e:
        return None

def display_mw_summary(word, mw_data):
    print("\n--- Merriam-Webster Data ---")
    if not mw_data:
        print("No data available.")
        return
    entry = mw_data[0] if mw_data and isinstance(mw_data, list) and len(mw_data) > 0 else None
    if entry and isinstance(entry, dict):
        part_of_speech = entry.get("fl", "Unknown")
        shortdef = entry.get("shortdef", [])
        print(f"Word: {word}")
        print(f"Part of Speech: {part_of_speech}")
        if shortdef:
            print("Definitions:")
            for d in shortdef:
                print(f" - {d}")
        else:
            print("No definitions available.")
    else:
        print("No valid entry found.")
    print("----------------------------\n")

def safe_folder_name(word):
    return "".join(c if c.isalnum() else "_" for c in word)

def extract_audio_url(mw_data):
    if not mw_data:
        return None
    for entry in mw_data:
        if isinstance(entry, dict):
            hwi = entry.get('hwi', {})
            prs = hwi.get('prs', [])
            if prs and isinstance(prs, list):
                for pr in prs:
                    sound = pr.get('sound', {})
                    audio = sound.get('audio')
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

def save_mw_data(word_folder, mw_data):
    data_path = os.path.join(word_folder, 'mw_data.json')
    try:
        with open(data_path, 'w', encoding='utf-8') as f:
            json.dump(mw_data, f, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"Error saving MW data: {e}")

def download_audio(word, word_folder, audio_url):
    if not audio_url:
        print(f"No audio found for {word}.")
        return
    try:
        audio_response = requests.get(audio_url)
        audio_response.raise_for_status()
        audio_path = os.path.join(word_folder, 'pronunciation.mp3')
        with open(audio_path, 'wb') as f:
            f.write(audio_response.content)
        print(f"Downloaded audio for {word}.")
    except requests.RequestException as e:
        print(f"Error downloading audio for {word}: {e}")

def process_accepted_word(word, mw_data):
    folder_name = safe_folder_name(word)
    word_folder = os.path.join(VOCAB_DIR, folder_name)
    os.makedirs(word_folder, exist_ok=True)
    
    save_mw_data(word_folder, mw_data)
    audio_url = extract_audio_url(mw_data)
    download_audio(word, word_folder, audio_url)

def get_key_press():
    if os.name == 'nt':
        import msvcrt
        return msvcrt.getch().decode().lower()
    else:
        import tty
        import termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch.lower()

def process_word(word):
    doc = nlp(word)
    for token in doc:
        if token.pos_ in ['VERB', 'NOUN', 'ADJ', 'ADV', 'AUX']:
          return token.lemma_, token.pos_
    return None, token.pos_

def handle_choice(choice, processed_word, current_index, checkpoint, vocab_list):
    if choice == 'u':
        if current_index > 0:
            current_index -= 1
            undone_word = vocab_list[current_index]
            checkpoint['decisions'].pop(undone_word, None)
            print("\nUndid the previous decision.")
        else:
            print("\nNo previous entry to undo.")
    elif choice == 'n':
        checkpoint['decisions'][processed_word] = 'n'
        current_index += 1
    elif choice == 'm':
        mw_data = fetch_mw_data(processed_word)
        display_mw_summary(processed_word, mw_data)
        print("Do you want to learn this word? (y/n)")
        sub_choice = get_key_press()
        if sub_choice == 'y':
            process_accepted_word(processed_word, mw_data)
            checkpoint['decisions'][processed_word] = 'y'
        else:
            checkpoint['decisions'][processed_word] = 'n'
        current_index += 1
    elif choice == 'y':
        mw_data = fetch_mw_data(processed_word)
        process_accepted_word(processed_word, mw_data)
        checkpoint['decisions'][processed_word] = 'y'
        current_index += 1
    else:
        print("\nInvalid input. Please press y, n, m, or u.")
    return current_index
        
def interactive_loop():
    vocab_list = load_vocab_list()
    checkpoint = load_checkpoint()
    current_index = checkpoint.get('current_index', 0)
    os.makedirs(VOCAB_DIR, exist_ok=True)
    
    print("Press 'q' at any time to quit.")
    
    while current_index < len(vocab_list):
        original_word = vocab_list[current_index]
        processed_word, word_type = process_word(original_word)
        
        if not processed_word:
            print(f"\nSkipping '{original_word}': {word_type} is not a type of content word.")
            current_index += 1
            continue
        
        if processed_word in checkpoint['decisions']:
            print(f"\nSkipping '{processed_word}': Already processed.")
            current_index += 1
            continue
        
        print("Do you want to learn this word? (y/n/m/u)")
        print(processed_word)
        
        choice = get_key_press()
        
        if choice == 'q':
            print("\nQuitting...")
            break
        
        current_index = handle_choice(choice, processed_word, current_index, checkpoint, vocab_list)
        checkpoint['current_index'] = current_index
        save_checkpoint(checkpoint)
    
    print("\nCompleted processing the vocabulary list.")

if __name__ == '__main__':
    interactive_loop()
