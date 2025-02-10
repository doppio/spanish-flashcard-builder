"""Google Custom Search API client for image search."""

from dataclasses import dataclass
from typing import Dict, List, Optional, Union

import requests

from spanish_flashcard_builder.config import api_keys


@dataclass
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
        """
        Search for images using the provided query.

        Args:
            query: Search query string
            num_results: Number of results to return (max 10)

        Returns:
            List of ImageResult objects
        """
        params: Dict[str, Union[str, int]] = {
            "key": self.api_key,
            "cx": self.search_engine_id,
            "q": query,
            "searchType": "image",
            "num": min(num_results, 10),
            "rights": (
                "cc_publicdomain,cc_attribute,cc_sharealike"  # Free to use images
            ),
            "safe": "active",
            "imgSize": "large",  # Request large images instead of medium
        }

        try:
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data.get("items", []):
                image = item.get("image", {})
                results.append(
                    ImageResult(
                        title=item.get("title", ""),
                        thumbnail_url=item.get("image", {}).get("thumbnailLink", ""),
                        full_url=item.get("link", ""),
                        width=image.get("width", 0),
                        height=image.get("height", 0),
                        file_format=image.get("mime", "").split("/")[-1],
                    )
                )

            return results

        except requests.RequestException as e:
            print(f"Error searching for images: {e}")
            return []

    def download_image(self, url: str) -> Optional[bytes]:
        """
        Download an image from the given URL.

        Args:
            url: URL of the image to download

        Returns:
            Image data as bytes if successful, None otherwise
        """
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            print(f"Error downloading image: {e}")
            return None
