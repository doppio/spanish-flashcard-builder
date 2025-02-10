# Image Selector Module

This step of the pipeline provides a GUI for selecting appropriate flashcard images.

## Features

- Searches for relevant images using Google Custom Search API
- Displays a grid of image options for each vocabulary term
- Supports selection by number key or by clicking the image
- Automatically resizes and optimizes selected images for flashcard use

## Usage

The step of the pipeline can be run using package's CLI:
```bash
sfb images
```

This will process all vocabulary terms that don't yet have associated images, allowing you to interactively select a memorable image for each term's flashcard.
