#!/usr/bin/env python3

from collections import defaultdict
from spanish_flashcard_builder.config import paths
from .spacy import load_spacy_model, canonicalize_word

def process_vocab_file():
    """Process the raw vocabulary file and output cleaned version"""
    
    lemma_dict = defaultdict(set)
    # Keep track of first occurrence of each lemma
    lemma_order = []
    
    print("Loading spaCy model...")
    load_spacy_model()
    print("Processing vocabulary file...")
    
    # First count total lines for progress calculation
    total_lines = sum(1 for _ in open(paths.raw_vocab, 'r', encoding='utf-8'))
    
    # Read and process the raw vocabulary file
    with open(paths.raw_vocab, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            # Show progress every 100 lines
            if i % 100 == 0:
                progress = (i / total_lines) * 100
                print(f"\rProgress: {progress:.1f}% ({i}/{total_lines} words)", end='', flush=True)
            
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
    print("\r" + " " * 50 + "\r", end='', flush=True)
    print("Writing cleaned vocabulary file...")
    
    # Write the cleaned vocabulary file
    total_lemmas = len(lemma_order)
    
    with open(paths.cleaned_vocab, 'w', encoding='utf-8') as f:
        for i, lemma in enumerate(lemma_order, 1):
            if i % 100 == 0:
                progress = (i / total_lemmas) * 100
                print(f"\rWriting: {progress:.1f}% ({i}/{total_lemmas} lemmas)", end='', flush=True)
            
            forms = lemma_dict[lemma]
            word_to_write = min(forms, key=len) if forms else lemma
            f.write(f"{word_to_write}\n")
    
    # Clear the writing progress message
    print("\r" + " " * 50 + "\r", end='', flush=True)
    print(f"Processed {len(lemma_dict)} unique lemmas")
    print(f"Output written to {paths.cleaned_vocab}")

def main():
    """Main entry point for data cleaning functionality"""
    process_vocab_file()
