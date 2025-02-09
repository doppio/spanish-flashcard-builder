# Spanish Vocabulary Pipeline (WIP)

**Note: This is a work in progress. Everything is subject to change.**

A system for building personalized Spanish vocabulary study materials. The pipeline helps select, enrich, and prepare Spanish words for study.

## Status

### Done
- Word selection with Merriam-Webster dictionary
- Audio pronunciation downloads
- AI-powered example sentences and usage notes
- Pipeline status tracking (`display_manifest.py`)

### TODO
- Image selection/download system
- Anki flashcard generation
- Documentation
- Testing

## Setup

Requires API keys in `.env`:
```
MERRIAM_WEBSTER_API_KEY=your_key
BING_API_KEY=your_key
OPENAI_API_KEY=your_key
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/doppio/spanish-vocab-builder.git
   cd spanish-vocab-builder
   ```

2. Install the package:
   ```bash
   pip install .
   ```

3. Download the required spaCy model:
   ```bash
   sfb setup 
   ```

## Usage
TODO