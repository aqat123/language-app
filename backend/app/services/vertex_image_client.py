"""
Vertex AI Image Generation Client for Imagen
Uses service account authentication for Google Cloud Vertex AI
"""
import base64
import os
from typing import Optional
from google.cloud import aiplatform
from google.oauth2 import service_account
from vertexai.preview.vision_models import ImageGenerationModel


class VertexImageClient:
    """Client for generating images using Vertex AI Imagen."""

    def __init__(
        self,
        credentials_path: str,
        project_id: str,
        location: str = "us-central1"
    ):
        """
        Initialize Vertex AI client.

        Args:
            credentials_path: Path to service account JSON file
            project_id: Google Cloud project ID
            location: GCP region (default: us-central1)
        """
        self.project_id = project_id
        self.location = location

        # Load credentials
        if not os.path.exists(credentials_path):
            raise FileNotFoundError(
                f"Service account credentials not found at: {credentials_path}"
            )

        credentials = service_account.Credentials.from_service_account_file(
            credentials_path
        )

        # Initialize Vertex AI
        aiplatform.init(
            project=project_id,
            location=location,
            credentials=credentials
        )

        # Load the image generation model (using newer Imagen 3)
        # Note: imagegeneration@006 is deprecated, using imagen-3.0-generate-001
        self.model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")

    async def generate_safe_image(self, prompt: str) -> Optional[str]:
        """
        Generate a safe educational image based on the prompt.

        Args:
            prompt: Text description of the image to generate

        Returns:
            Base64 encoded image string or None if generation fails
        """
        try:
            # Create safe educational prompt
            safe_prompt = (
                f"cartoon style illustration of {prompt}. "
                "minimalist, educational, white background, clear lines, "
                "safe for work, appropriate for language learning."
            )

            # Generate image
            response = self.model.generate_images(
                prompt=safe_prompt,
                number_of_images=1,
                aspect_ratio="1:1",
                safety_filter_level="block_some",
                person_generation="allow_adult"
            )

            # Get the first image
            if response.images:
                image = response.images[0]
                # Convert to base64
                image_bytes = image._pil_image
                # Convert PIL image to bytes
                from io import BytesIO
                buffered = BytesIO()
                image_bytes.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                return img_str

            return None

        except Exception as e:
            print(f"Vertex AI Image Generation Error: {e}")
            return None

    async def close(self):
        """Cleanup method (no persistent connections to close)."""
        pass


# Global instance
_vertex_image_client: Optional[VertexImageClient] = None


def get_vertex_image_client(
    credentials_path: str,
    project_id: str,
    location: str = "us-central1"
) -> VertexImageClient:
    """Get or create the global Vertex AI image client instance."""
    global _vertex_image_client
    if _vertex_image_client is None:
        _vertex_image_client = VertexImageClient(
            credentials_path=credentials_path,
            project_id=project_id,
            location=location
        )
    return _vertex_image_client
