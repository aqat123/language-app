import httpx
import base64
from typing import Dict, Any
from app.core.config import settings


class STTError(Exception):
    """Custom exception for STT-related errors."""
    pass


class STTClient:
    """Client for Speech-to-Text API (Google Speech-to-Text)."""

    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def transcribe(
        self,
        audio_bytes: bytes,
        language_code: str = "en-US"
    ) -> Dict[str, Any]:
        """
        Transcribe audio to text using Speech-to-Text API.

        Args:
            audio_bytes: Audio file bytes
            language_code: Language code (e.g., "en-US", "es-ES", "fr-FR")

        Returns:
            Dict with keys: transcript, confidence, raw

        Raises:
            STTError: If the API call fails
        """
        try:
            # Encode audio to base64
            audio_content = base64.b64encode(audio_bytes).decode('utf-8')

            # Google Speech-to-Text API endpoint
            url = f"{self.base_url}/speech:recognize?key={self.api_key}"

            payload = {
                "config": {
                    "encoding": "LINEAR16",
                    "sampleRateHertz": 16000,
                    "languageCode": language_code,
                    "enableAutomaticPunctuation": True,
                },
                "audio": {
                    "content": audio_content
                }
            }

            response = await self.client.post(url, json=payload)
            response.raise_for_status()

            data = response.json()

            # Extract transcript and confidence
            if "results" in data and len(data["results"]) > 0:
                result = data["results"][0]
                if "alternatives" in result and len(result["alternatives"]) > 0:
                    alternative = result["alternatives"][0]
                    transcript = alternative.get("transcript", "")
                    confidence = alternative.get("confidence", 0.0)

                    return {
                        "transcript": transcript,
                        "confidence": confidence,
                        "raw": data
                    }

            # No results found
            return {
                "transcript": "",
                "confidence": 0.0,
                "raw": data
            }

        except httpx.HTTPError as e:
            raise STTError(f"HTTP error during STT API call: {str(e)}")
        except Exception as e:
            raise STTError(f"Error during speech transcription: {str(e)}")

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Global STT client instance
_stt_client: STTClient = None


def get_stt_client() -> STTClient:
    """Get or create the global STT client instance."""
    global _stt_client
    if _stt_client is None:
        _stt_client = STTClient(
            api_key=settings.STT_API_KEY,
            base_url=settings.STT_API_BASE_URL
        )
    return _stt_client
