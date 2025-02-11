#!/usr/bin/env python3

import sys
from collections import defaultdict
from typing import Optional

import spacy

from spanish_flashcard_builder.config import paths, spacy_config

nlp: Optional[spacy.Language] = None


def load_spacy_model() -> spacy.Language:
    """
    Load the Spanish spaCy model.

    Returns:
        The loaded spaCy model

    Raises:
        SystemExit: If the Spanish language model is not found
    """
    global nlp
    try:
        nlp = spacy.load(spacy_config.model_name)
    except OSError:
        print(f"Error: Spanish language model '{spacy_config.model_name}' not found.")
        response = input("Would you like to download it now? [Y/n] ").strip().lower()
        if response in ("", "y", "yes"):
            from spanish_flashcard_builder.scripts.download_spacy_model import (
                download_spacy_model,
            )

            download_spacy_model()
            return load_spacy_model()
        else:
            print("You can download it later by running: sfb download-spacy")
            sys.exit(1)
    return nlp


def canonicalize_word(word: str) -> Optional[str]:
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


def process_vocab_file() -> None:
    """Process the raw vocabulary file and output cleaned version"""

    lemma_dict = defaultdict(set)
    # Keep track of first occurrence of each lemma
    lemma_order = []

    print("Loading spaCy model...")
    load_spacy_model()
    print("Sanitizing vocabulary file...")

    # First count total lines for progress calculation
    total_lines = sum(1 for _ in open(paths.raw_vocab, "r", encoding="utf-8"))

    # Read and process the raw vocabulary file
    with open(paths.raw_vocab, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            # Show progress every 100 lines
            if i % 100 == 0:
                progress = (i / total_lines) * 100
                print(
                    f"\rProgress: {progress:.1f}% ({i}/{total_lines} words)",
                    end="",
                    flush=True,
                )

            word = line.split()[0].strip().lower()

            if not word:
                continue

            lemma = canonicalize_word(word)
            if lemma is None:
                continue

            if lemma not in lemma_dict:
                lemma_order.append(lemma)
            lemma_dict[lemma].add(word)

    # Clear the progress message
    print("\r" + " " * 50 + "\r", end="", flush=True)
    print("Writing sanitized vocabulary file...")

    # Write the sanitized vocabulary file
    total_lemmas = len(lemma_order)

    with open(paths.sanitized_vocab, "w", encoding="utf-8") as f:
        for i, lemma in enumerate(lemma_order, 1):
            if i % 100 == 0:
                progress = (i / total_lemmas) * 100
                print(
                    f"\rWriting: {progress:.1f}% ({i}/{total_lemmas} lemmas)",
                    end="",
                    flush=True,
                )

            forms = lemma_dict[lemma]
            word_to_write = min(forms, key=len) if forms else lemma
            f.write(f"{word_to_write}\n")

    # Clear the writing progress message
    print("\r" + " " * 50 + "\r", end="", flush=True)
    print(f"Processed {len(lemma_dict)} unique lemmas")
    print(f"Output written to {paths.sanitized_vocab}")


def main() -> None:
    """Main entry point for vocabulary sanitization"""
    process_vocab_file()


if __name__ == "__main__":
    main()
