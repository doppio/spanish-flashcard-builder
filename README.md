# Spanish Flashcard Builder

A tool for creating a personalized Spanish vocabulary flashcard deck for [Anki](https://apps.ankiweb.net/). It helps you select, enrich, and prepare Spanish vocabulary for effective learning using AI-powered content generation and multimedia resources.

The tool is designed as a pipeline of steps that can be run in sequence to produce a final product (the Anki deck). Each step works on data stored in the `output` directory and produces data that can be used in subsequent steps.

## Features

- 🎯 **Word selection**: Iterate over a list of words and select which definitions to include, using integration with the Merriam-Webster Spanish-English dictionary
- 🤖 **AI-assisted content**: Use an OpenAI model to generate natural example sentences, usage frequency ratings, and useful image search query strings for each term
- 🗣️ **Audio pronunciation**: Include pronunciation audio from Merriam-Webster
- 🖼️ **Visual learning**: Select relevant images for each term

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/doppio/spanish-flashcard-builder.git
   cd spanish-flashcard-builder
   ```

2. Install the package:
   ```bash
   pip install .
   ```

3. Set up required API keys in `.env`:
   ```
   MERRIAM_WEBSTER_API_KEY=your_key
   OPENAI_API_KEY=your_key
   GOOGLE_CSE_ID=your_key
   GOOGLE_API_KEY=your_key
   ```

4. Download required language model:
   ```bash
   sfb download-spacy
   ```

## Usage

The tool provides two variants of the command:
- `spanish-flashcard-builder`
- `sfb`

### Basic Workflow

1. Add your vocabulary words to `data/raw_vocab.txt` (one word per line). You can use a public list of Spanish words like [this one](https://github.com/doozan/spanish_data/blob/master/es_merged_50k.txt), or create your own list.
2. Process each word through the pipeline, in order:
   ```bash
   sfb sanitize   # Clean up the vocabulary list
   sfb curate     # Select which dictionary definitions to process
   sfb generate   # Generate AI-assisted flashcard content
   sfb images     # Select an image for each term
   sfb assemble   # Build the final Anki deck
   ```

## Pipeline Steps

### 1. `sfb sanitize`
Sanitizes the raw vocabulary list by removing duplicates, standardizing formatting, converting words to lemma form, and validating Spanish words.
- Input: `data/raw_vocab.txt`
- Output: `data/sanitized_vocab.txt`

### 2. `sfb curate`
Looks up words in the Merriam-Webster Spanish-English dictionary and lets you select which definitions to process as flashcards. As part of this step, the tool will download the audio pronunciation for the word from Merriam-Webster.

This step saves a history of words that have already been processed, so that you can resume the pipeline from where it left off without reprocessing words you have already seen.
- Input: Word list from `data/sanitized_vocab.txt`
- Output: `output/terms/<word>/`
   - `dictionary_entry.json`
   - `<word>.mp3`
- Controls:
  - `y`: Accept word
  - `n`: Reject and see next definition
  - `u`: Undo previous decision
  - `q`: Quit

### 3. `sfb generate`
Enriches vocabulary terms with AI-generated content using OpenAI. The word, part of speech, and definition are passed to the OpenAI API, which returns an object containing example sentences, a usage frequency rating, and a query string for finding a relevant image.
- Input: `output/terms/<word>/dictionary_entry.json`
- Output: `output/terms/<word>/flashcard.json`

### 4. `sfb images`
Provides a GUI for selecting memorable flashcard images. It uses Google Custom Search to find images using the query strings created by the `generate` step, and then allows you to select the best one for each term.
- Input: `output/terms/<word>/flashcard.json`
- Output: `output/terms/<word>/<word>.png`

### 5. `sfb assemble`
Builds the final Anki deck from the data output by previous steps in the pipeline.
- Input: All term data at `output/terms/<word>/`
  - `flashcard.json` (required)
  - `<word>.mp3` (optional)
  - `<word>.png` (optional)
- Output: `output/spanish_vocabulary.apkg`

## Utility Commands

### `sfb manifest`
Displays the current status of your vocabulary pipeline:
```
--------------------------------------------------------------------------------
Found 37 vocabulary entries:
--------------------------------------------------------------------------------
Word                 Dictionary  Flashcard   Audio       Image       
--------------------------------------------------------------------------------
clara                ✅           ✅           ✅           ✅           
menos:3              ✅           ✅           ✅           ❌           
padre:1              ✅           ✅           ✅           ✅
...
```

### `sfb clean <component>`
Removes data for a specific pipeline component for all terms in `output/terms/`:
```bash
sfb clean all
sfb clean audio
sfb clean images
sfb clean dictionary-entry
sfb clean flashcard-data
```

## Configuration

All configurable values are in `config.yml`:
```yaml
anki:
  deck:
    name: "Spanish Vocabulary"
    id: 7262245122
  model_id: 2600788583

openai:
  model: "gpt-4o-mini"
  temperature: 0.7

images:
  max_dimension: 1024
```

## License

This project is licensed under the MIT License.