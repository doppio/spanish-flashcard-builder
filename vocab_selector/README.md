# Vocabulary Selector

A component of the Spanish vocabulary pipeline that enables interactive review and selection of Spanish vocabulary words using the Merriam-Webster Spanish-English Dictionary API.

## Overview

The vocabulary selector takes a list of Spanish words and allows users to interactively review each word with its dictionary definitions provided by the Merriam-Webster Spanish-English Dictionary API. Users can accept or reject words based on their learning preferences, with accepted words being saved for use in later pipeline stages.

## Features

- Interactive word-by-word review process
- Real-time dictionary lookups via Merriam-Webster Spanish-English Dictionary API
- Automatic pronunciation audio downloads for accepted words
- Progress tracking with session persistence
- Undo functionality for correcting decisions
- Support for multiple definitions per word

## Component Input

- Text file containing Spanish words (one per line)
- Configuration settings in `config.py`

## Component Output

Selected vocabulary words are saved in a structured format:
```
vocab_bank/
├── {entry_id_1}/
│ ├── entry.json
│ └── pronunciation.mp3
└── {entry_id_2}/
  ├── entry.json
  └── pronunciation.mp3
```

## Usage

During the review process, for each word you can:
- Press `y` to accept
- Press `n` to reject
- Press `u` to undo the previous decision
- Press `q` to save progress and quit

Progress is automatically saved after each action and restored when resuming.

