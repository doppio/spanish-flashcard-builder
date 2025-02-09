import spacy
from spanish_flashcard_builder.config import SPACY_MODEL_NAME

def download_spacy_model():
    print(f"Downloading spaCy model: {SPACY_MODEL_NAME}")
    try:
        spacy.cli.download(SPACY_MODEL_NAME)
        print("Download completed successfully!")
    except Exception as e:
        print(f"Error downloading model: {e}")

if __name__ == "__main__":
    download_spacy_model() 