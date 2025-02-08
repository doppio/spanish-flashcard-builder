# config.py
import os
from dotenv import load_dotenv
import sys

# Load environment variables from the .env file
load_dotenv(override=True)

# Retrieve the API keys
MERRIAM_WEBSTER_API_KEY = os.getenv("MERRIAM_WEBSTER_API_KEY")
BING_API_KEY = os.getenv("BING_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

DATA_DIR = os.path.join('data')

RAW_SEARCH_WORD_FILE = os.path.join(DATA_DIR, 'raw_vocab.txt')
CLEANED_SEARCH_WORD_FILE = os.path.join(DATA_DIR, 'cleaned_vocab.txt')
SELECTOR_HISTORY_FILE = os.path.join(DATA_DIR, 'vocab_selector_history.json')
VOCAB_BANK_DIR = os.path.join(DATA_DIR, 'vocab_entries')

DECK_NAME = "Spanish Vocabulary"
DECK_ID = 7262245122  # Unique integer for the deck

def validate_config():
    required_vars = {
        "MERRIAM_WEBSTER_API_KEY": MERRIAM_WEBSTER_API_KEY,
        "BING_API_KEY": BING_API_KEY,
        "OPENAI_API_KEY": OPENAI_API_KEY
    }
    
    missing = [k for k, v in required_vars.items() if not v]
    if missing:
        print(f"Error: Missing required environment variables: {', '.join(missing)}")
        print("Please check your .env file")
        sys.exit(1)

validate_config()
