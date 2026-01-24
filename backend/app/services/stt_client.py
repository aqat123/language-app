import httpx
import base64
import json
from typing import Dict, Any, Optional
from app.core.config import settings


class STTError(Exception):
    """Custom exception for STT-related errors."""
    pass


class STTClient:
    """Client for Speech-to-Text API (Google Speech-to-Text)
    plus Phonetic Analysis, using Gemini 2.5 Flash."""

    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.model = model

    async def analyze_audio(
            self,
            audio_bytes: bytes,
            mime_type: str = "audio/webm",
            target_language: str = "English",
            target_phrase: str = ""
    ) -> Dict[str, Any]:
        """
        Transcribes audio AND provides phonetic feedback in one go.
        """
        try:
            # 1. Encode audio
            b64_audio = base64.b64encode(audio_bytes).decode('utf-8')

            # 2. Endpoint
            url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"

            # 3. The "Super Prompt" for Phonetics
            # We ask for JSON output containing both the text and the critique.
            prompt_text = f"""
            You are a strict {target_language} phonetic expert. 
            The user is trying to say: "{target_phrase}"

            Task 1: Transcribe the audio exactly.
            Task 2: Analyze the user's pronunciation, accent, and fluency.

            Respond ONLY with valid JSON in this format:
            {{
                "transcript": "The exact text spoken",
                "confidence": 0.92,
                "score": 85,
                "feedback": "Overall comment on accent and clarity",
                "word_level_feedback": [
                    {{
                        "word": "word_spoken",
                        "issue": "What was wrong (e.g., 'th' sound was 'z')",
                        "tip": "How to fix it (e.g., 'Place tongue between teeth')"
                    }}
                ]
            }}
            """

            payload = {
                "contents": [{
                    "parts": [
                        {"text": prompt_text},
                        {
                            "inlineData": {
                                "mimeType": mime_type,
                                "data": b64_audio
                            }
                        }
                    ]
                }],
                "generationConfig": {
                    "temperature": 0.2,  # Low temperature for accurate transcription
                    "responseMimeType": "application/json"  # Force JSON mode if available
                }
            }

            # 4. Send Request
            response = await self.client.post(url, json=payload)
            response.raise_for_status()

            data = response.json()

            # 5. Extract and Parse Gemini Response
            if "candidates" in data and len(data["candidates"]) > 0:
                candidate = data["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    raw_text = candidate["content"]["parts"][0]["text"]

                    # Clean up JSON markdown if present
                    clean_json = raw_text.strip()
                    if clean_json.startswith("```json"):
                        clean_json = clean_json[7:]
                    if clean_json.startswith("```"):
                        clean_json = clean_json[3:]
                    if clean_json.endswith("```"):
                        clean_json = clean_json[:-3]

                    parsed_result = json.loads(clean_json)

                    if "confidence" not in parsed_result:
                        parsed_result["confidence"] = 1.0  # Default if AI forgets
                    if "word_level_feedback" not in parsed_result:
                        parsed_result["word_level_feedback"] = []

                    return parsed_result
            raise STTError("No content returned from AI")

        except httpx.HTTPError as e:
            raise STTError(f"HTTP error during STT API call: {str(e)}")
        except json.JSONDecodeError:
            raise STTError("AI returned invalid JSON")
        except Exception as e:
            raise STTError(f"Error during speech transcription: {str(e)}")

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Global STT client instance
_stt_client: Optional[STTClient] = None


def get_stt_client() -> STTClient:
    """Get or create the global STT client instance."""
    global _stt_client
    if _stt_client is None:
        _stt_client = STTClient(
            api_key=settings.STT_API_KEY,
            base_url=settings.STT_API_BASE_URL,
            model =settings.STT_MODEL
        )
    return _stt_client
