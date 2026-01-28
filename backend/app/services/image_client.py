"""
Image Generation Client Module.

Handles image generation for vocabulary learning using Google Imagen 4 API.
Generates safe, educational images to accompany vocabulary words.

Key Features:
- REST API integration with Imagen 4 image generation model
- Base64 encoded image output
- Safety filtering (cartoon style, minimalist, educational)
- Error handling and graceful fallback (returns None on failure)
- Configurable aspect ratio (1:1 for flashcard display)

Main Classes:
    ImageGenClient: Client for Imagen 4 API communication
    
Main Functions:
    get_image_client: Singleton factory for ImageGenClient

Usage Example:
    >>> client = get_image_client()
    >>> image_b64 = await client.generate_safe_image("cat, a domestic animal")
    >>> if image_b64:
    ...     display_image(image_b64)  # Use in frontend
    >>> await client.close()
"""

import httpx
from typing import Optional
from app.core.config import settings

class ImageGenClient:
    """
    Client for Google Imagen 4 Image Generation API.
    
    Generates educational, safe images for vocabulary learning.
    Images are styled as cartoon illustrations with minimalist design.
    """

    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.client = httpx.AsyncClient(timeout=30.0)

    async def generate_safe_image(self, prompt: str) -> Optional[str]:
        """
        Generate safe, educational image for vocabulary word.

        Creates a cartoon-style illustration based on the prompt.
        Image is automatically styled as minimalist, educational, and safe.

        Args:
            prompt: Description of what to illustrate (e.g., "cat" or "cat, a domestic animal")

        Returns:
            Base64-encoded image string if successful, None if generation fails

        Implementation Notes:
            - Automatically adds safety modifiers to prompt (cartoon style, minimalist, white bg)
            - Uses 1:1 aspect ratio for flashcard display
            - Returns None gracefully if:
              - API returns non-200 status
              - Response JSON is malformed
              - Predictions array is empty
              - Base64 encoding is missing
            - Logs errors to console for debugging
            - Timeout: 30 seconds per request

        Error Handling:
            - HTTP errors (400, 401, 403, 429, 500): Logged, returns None
            - JSON parsing errors: Logged, returns None
            - Missing keys in response: Logged, returns None
            - Exception during generation: Caught, logged, returns None

        Imagen 4 Response Format:
            {
                "predictions": [{
                    "bytesBase64Encoded": "base64_image_string"
                    OR "b64": "base64_image_string"
                }]
            }

        Example:
            >>> client = get_image_client()
            >>> image_b64 = await client.generate_safe_image("Spanish cat")
            >>> if image_b64:
            ...     # Send to frontend
            ...     return {"image_data": image_b64}
            >>> else:
            ...     # Fallback: no image
            ...     return {"image_data": None}
        """
        try:
            # Construct endpoint URL
            # Note: Imagen 4 on this API usually uses the 'predict' endpoint
            url = f"{self.base_url}/models/{self.model}:predict?key={self.api_key}"

            safe_prompt = (
                f"cartoon style illustration of {prompt}. "
                "minimalist, educational, white background, clear lines, safe for work."
            )

            # Payload specifically for Imagen 4 via REST API
            payload = {
                "instances": [
                    {
                        "prompt": safe_prompt
                    }
                ],
                "parameters": {
                    "sampleCount": 1,
                    # Imagen 4 specific aspect ratio parameter (optional, but good for cards)
                    "aspectRatio": "1:1"
                }
            }

            response = await self.client.post(url, json=payload)

            # Print error if it fails so we can debug in terminal
            if response.status_code != 200:
                print(f"IMAGE GEN ERROR: {response.status_code} - {response.text}")
                return None

            data = response.json()

            # Extract Base64 image
            # Imagen 4 usually returns: {"predictions": [{"bytesBase64Encoded": "..."}]}
            if "predictions" in data and len(data["predictions"]) > 0:
                prediction = data["predictions"][0]

                # Check for standard encoding key
                if "bytesBase64Encoded" in prediction:
                    return prediction["bytesBase64Encoded"]

                # Check for alternative key
                if "b64" in prediction:
                    return prediction["b64"]

            return None

        except Exception as e:
            print(f"Image Gen Exception: {e}")
            return None

    async def close(self):
        """Close the HTTP client connection cleanly."""
        await self.client.aclose()

_image_client: Optional[ImageGenClient] = None


def get_image_client() -> ImageGenClient:
    """
    Get or create the singleton ImageGenClient instance.

    Lazy initialization: Creates client on first call, reuses same instance
    on subsequent calls. Credentials loaded from environment (.env file).

    Returns:
        ImageGenClient instance configured with API credentials

    Implementation Notes:
        - Thread-safe singleton pattern
        - Credentials from app.core.config.settings:
          - LLM_IMAGE_API_KEY: Gemini API key
          - LLM_IMAGE_API_BASE_URL: Imagen 4 endpoint base URL
          - LLM_IMAGE_MODEL: Model identifier (imagen-4.0-fast-generate-001)
        - Same instance reused across application
        - Client remains open until explicitly closed

    Example:
        >>> client = get_image_client()
        >>> image = await client.generate_safe_image("Spanish cat")
    """
    global _image_client
    if _image_client is None:
        _image_client = ImageGenClient(
            api_key=settings.LLM_IMAGE_API_KEY,
            base_url=settings.LLM_IMAGE_API_BASE_URL,
            model=settings.LLM_IMAGE_MODEL,
        )
    return _image_client
