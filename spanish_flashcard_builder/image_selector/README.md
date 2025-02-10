# Image selector

This tool provides a GUI for selecting memorable flashcard images. It processes terms from the output dictionary that:
1. Have completed the `augmentation` step (which generates an image search query string)
2. Don't already have an associated image

Using the Google Custom Search API, it searches for images matching the query string and displays them in a grid. The user can then select an image to use for the term's flashcard.

## Usage

Run the image selection tool using the package's CLI:
```bash
sfb images
```