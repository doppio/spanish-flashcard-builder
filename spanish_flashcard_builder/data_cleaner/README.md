# Data cleaner

This component of the pipeline preprocesses and cleans raw vocabulary input files. It uses spaCy to convert words to their base forms (e.g. conjugated verbs to their infinitive forms), remove duplicates, and filter out non-Spanish words. This is an important automation step for very large vocabulary datasets to avoid wasting time on words that would not be useful flashcards.

## Usage

Run the data cleaning tool using the package's CLI:
```bash
sfb clean
```