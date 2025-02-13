"""Google Custom Search API client for image search."""

import logging
from dataclasses import dataclass
from typing import Dict, List, Union

import requests
from requests.exceptions import RequestException

from spanish_flashcard_builder.config import api_keys
from spanish_flashcard_builder.exceptions import SpanishFlashcardError


class ImageSearchError(SpanishFlashcardError):
    """Custom exception for errors during image search."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


@dataclass(frozen=True)
class ImageResult:
    """Represents a single image search result."""

    title: str
    thumbnail_url: str
    full_url: str
    width: int
    height: int
    file_format: str


class GoogleImageSearch:
    """Client for Google Custom Search API focused on image search."""

    BASE_URL = "https://customsearch.googleapis.com/customsearch/v1"

    def __init__(self) -> None:
        self.api_key = api_keys.google_search
        self.search_engine_id = api_keys.google_search_engine_id

    def search_images(self, query: str, num_results: int = 10) -> List[ImageResult]:
        """Search for images using the provided query.

        Args:
            query: Search query string
            num_results: Number of results to return (max 10)

        Returns:
            List of ImageResult objects

        Raises:
            ImageSearchError: If the search request fails
        """
        params: Dict[str, Union[str, int]] = {
            "key": self.api_key,
            "cx": self.search_engine_id,
            "q": query,
            "searchType": "image",
            "num": min(num_results, 10),
            "rights": "cc_publicdomain,cc_attribute,cc_sharealike",
            "safe": "active",
            "imgSize": "large",
        }

        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            return [
                ImageResult(
                    title=item.get("title", ""),
                    thumbnail_url=item.get("image", {}).get("thumbnailLink", ""),
                    full_url=item.get("link", ""),
                    width=item.get("image", {}).get("width", 0),
                    height=item.get("image", {}).get("height", 0),
                    file_format=item.get("image", {}).get("mime", "").split("/")[-1],
                )
                for item in data.get("items", [])
            ]

        except RequestException as e:
            logging.error(f"Failed to search for images: {e}")
            raise ImageSearchError(f"Image search failed: {e}") from e

    def download_image(self, url: str) -> bytes:
        """Download an image from a URL.

        Args:
            url: The URL of the image to download.

        Returns:
            The image bytes

        Raises:
            ImageSearchError: If the download fails
        """
        try:
            response = requests.get(url, stream=True, timeout=10)
            response.raise_for_status()
            return response.content

        except RequestException as e:
            logging.error(f"Failed to download image from {url}: {e}")
            raise ImageSearchError(f"Image download failed: {e}") from e
