# Initialize spaCy
import sys
import spacy
from spanish_flashcard_builder.config import SPACY_MODEL_NAME

nlp = None

def load_spacy_model():
    """
    Load the Spanish spaCy model.
    
    Returns:
        The loaded spaCy model
    
    Raises:
        SystemExit: If the Spanish language model is not found
    """
    global nlp
    try:
        nlp = spacy.load(SPACY_MODEL_NAME)
    except OSError:
        print(f"Error: Spanish language model '{SPACY_MODEL_NAME}' not found.")
        response = input("Would you like to download it now? [Y/n] ").strip().lower()
        if response in ('', 'y', 'yes'):
            from spanish_flashcard_builder.scripts.download_spacy_model import download_spacy_model
            download_spacy_model()
            return load_spacy_model()
        else:
            print("You can download it later by running: download-spacy-model")
            sys.exit(1)
    return nlp

def canonicalize_word(word):
    """
    Convert a word to its canonical form using spaCy lemmatization.
    Only returns words that exist in the Spanish vocabulary.
    
    Args:
        word: String containing the word to canonicalize
        
    Returns:
        Lemmatized form of the word if it's a valid Spanish word and part of speech,
        None otherwise
    """
    global nlp
    if nlp is None:
        nlp = load_spacy_model()
    
    doc = nlp(word)
    allowed_pos = {"NOUN", "VERB", "ADJ", "ADV"}
    
    for token in doc:
        # Check if the word exists in Spanish vocabulary
        if not token.is_oov and token.pos_ in allowed_pos:
            return token.lemma_
    return None