import httpx
from typing import Optional
from app.core.config import settings

class ImageGenClient:
    """Client dedicated to interacting with Image Generation API (Imagen 4)."""

    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.client = httpx.AsyncClient(timeout=30.0)

    async def generate_safe_image(self, prompt: str) -> Optional[str]:
        """
        Generate a safe image based on the prompt using Imagen 4.
        Returns: base64 encoded image string OR None if generation fails.
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
        await self.client.aclose()

_image_client: Optional[ImageGenClient] = None


def get_image_client() -> ImageGenClient:
    """Get singleton ImageGenClient instance."""
    global _image_client
    if _image_client is None:
        _image_client = ImageGenClient(
            api_key=settings.LLM_IMAGE_API_KEY,
            base_url=settings.LLM_IMAGE_API_BASE_URL,
            model=settings.LLM_IMAGE_MODEL,
        )
    return _image_client
