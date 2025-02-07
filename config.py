# config.py
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv(override=True)

# Retrieve the API keys
MERRIAM_WEBSTER_API_KEY = os.getenv("MERRIAM_WEBSTER_API_KEY")
BING_API_KEY = os.getenv("BING_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

VOCAB_FILE = os.path.join('data', 'es_merged_50k.txt')
CHECKPOINT_FILE = os.path.join('data', 'checkpoint.json')
VOCAB_DIR = os.path.join('data', 'vocab_entries')

DECK_NAME = "Spanish Vocabulary"
DECK_ID = 7262245122  # Unique integer for the deck
