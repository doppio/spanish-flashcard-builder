# Initialize spaCy
import sys
import spacy

try:
    nlp = spacy.load("es_core_news_md")
except OSError:
    print("Error: Spanish language model not found. Please install it using:")
    print("python -m spacy download es_core_news_md")
    sys.exit(1)

def canonicalize_word(word):
    """
    Convert a word to its canonical form using spaCy lemmatization.
    
    Args:
        word: String containing the word to canonicalize
        
    Returns:
        Lemmatized form of the word if it's a valid part of speech,
        None otherwise
    """
    doc = nlp(word)
    allowed_pos = {"NOUN", "VERB", "ADJ", "ADV"}
    for token in doc:
        if token.pos_ in allowed_pos:
            return token.lemma_
    return None