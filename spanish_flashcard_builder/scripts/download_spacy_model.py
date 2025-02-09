import spacy
from spanish_flashcard_builder.config import spacy_config

def download_spacy_model():
    print(f"Downloading spaCy model: {spacy_config.model_name}")
    try:
        spacy.cli.download(spacy_config.model_name)
        print("Download completed successfully!")
    except Exception as e:
        print(f"Error downloading model: {e}")

if __name__ == "__main__":
    download_spacy_model() 