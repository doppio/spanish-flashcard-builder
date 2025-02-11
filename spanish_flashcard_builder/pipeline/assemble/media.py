"""Media handling for Anki deck generation."""

from pathlib import Path
from typing import List, Optional

from spanish_flashcard_builder.config import paths
from spanish_flashcard_builder.exceptions import MediaProcessingError
from spanish_flashcard_builder.pipeline.generate.models import GeneratedTerm


class AnkiMediaHandler:
    """Handles media file operations for Anki deck generation."""

    def __init__(self) -> None:
        self.media_files: List[str] = []

    def get_media_paths(
        self, term_dir: Path, term: GeneratedTerm
    ) -> Optional[tuple[Path, Path]]:
        """Get and validate image and audio paths for a term.

        Args:
            term_dir: Directory containing the term's files
            term: The term data

        Returns:
            Tuple of (image_path, audio_path) if both exist, None otherwise

        Raises:
            MediaProcessingError: If media files are missing or invalid
        """
        image_path = term_dir / paths.get_image_filename(term_dir)
        audio_path = term_dir / paths.get_pronunciation_filename(term_dir)

        if not image_path.exists():
            raise MediaProcessingError(f"Image file missing: {image_path}")
        if not audio_path.exists():
            raise MediaProcessingError(f"Audio file missing: {audio_path}")

        # Track media files
        self.media_files.extend(map(str, [image_path, audio_path]))
        return image_path, audio_path

    def get_tracked_media(self) -> List[str]:
        """Get list of tracked media files."""
        return self.media_files
