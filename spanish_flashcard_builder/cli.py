import click

# Pipeline commands
from .pipeline.assemble.__main__ import main as assemble_main
from .pipeline.curate.__main__ import main as curate_main
from .pipeline.generate.__main__ import main as generate_main
from .pipeline.images.__main__ import main as image_main

# Utility scripts
from .scripts.clean import TARGETS
from .scripts.clean import clean as clean_files
from .scripts.download_spacy_model import download_spacy_model
from .scripts.manifest import main as manifest_main
from .scripts.sanitize import main as sanitize_main


@click.group()
def main() -> None:
    """Spanish Flashcard Builder CLI"""
    pass


# Setup Commands
@main.command()
def download_spacy() -> None:
    """Download required spaCy model"""
    download_spacy_model()


# Data Management Commands
@main.command()
def manifest() -> None:
    """Display the current vocabulary manifest"""
    manifest_main()


@main.command()
def sanitize() -> None:
    """Sanitize the vocabulary file"""
    sanitize_main()


@main.command()
@click.argument(
    "component",
    type=click.Choice(list(TARGETS.keys())),
)
@click.option("--force", "-f", is_flag=True, help="Skip confirmation prompt")
def clean(component: str, force: bool) -> None:
    """Remove component data"""
    if force or click.confirm(
        f"This will remove all {component} files. Are you sure?", default=False
    ):
        clean_files(component)
    else:
        click.echo("Operation cancelled")


# Flashcard Generation Pipeline Commands
@main.command()
def curate() -> None:
    """Curate new vocabulary words"""
    curate_main()


@main.command()
def generate() -> None:
    """Generate AI content for vocabulary terms"""
    generate_main()


@main.command()
def images() -> None:
    """Select images for vocabulary terms"""
    image_main()


@main.command()
def assemble() -> None:
    """Assemble Anki deck from processed vocabulary terms"""
    assemble_main()


if __name__ == "__main__":
    main()
