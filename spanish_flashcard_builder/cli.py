import click
from .vocab_selector.__main__ import main as select_main
from .data_cleaner.__main__ import main as clean_main
from .augmentation.__main__ import main as augment_main
from .image_selector.__main__ import main as image_main
from .scripts.display_manifest import main as manifest_main
from .scripts.download_spacy_model import download_spacy_model

@click.group()
def main():
    """Spanish Flashcard Builder CLI"""
    pass

@main.command()
def clean():
    """Clean the vocabulary file"""
    clean_main()

@main.command()
def select():
    """Select new vocabulary words"""
    select_main()

@main.command()
def augment():
    """Augment vocabulary entries with AI-generated content"""
    augment_main()

@main.command()
def images():
    """Select images for vocabulary terms"""
    image_main()

@main.command()
def manifest():
    """Display the current vocabulary manifest"""
    manifest_main()

@main.command()
def setup():
    """Download required spaCy model"""
    download_spacy_model()

if __name__ == '__main__':
    main() 