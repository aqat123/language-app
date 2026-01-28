"""
Speech-to-Text and Phonetic Analysis Client Module.

Handles audio transcription and pronunciation analysis for the Phonetics module.
Uses Google Gemini 2.5 Flash to transcribe audio and provide detailed phonetic feedback.

Key Features:
- Audio transcription (Speech-to-Text)
- Phonetic analysis and feedback
- Word-level pronunciation issues with correction tips
- Confidence scoring
- Base64 audio encoding for API transmission
- JSON structured output for phonetic feedback

Main Classes:
    STTClient: Client for speech-to-text and phonetic analysis
    STTError: Custom exception for STT-related errors

Main Functions:
    get_stt_client: Singleton factory for STTClient

Workflow:
    1. Receive audio bytes from frontend
    2. Base64 encode audio for API transmission
    3. Send to Gemini with target phrase and language context
    4. Gemini transcribes and analyzes pronunciation
    5. Parse JSON response with transcript and feedback
    6. Return to phonetics module for score calculation

Usage Example:
    >>> stt = get_stt_client()
    >>> result = await stt.analyze_audio(
    ...     audio_bytes=audio_file_bytes,
    ...     mime_type="audio/webm",
    ...     target_language="Spanish",
    ...     target_phrase="Hola, ¿cómo estás?"
    ... )
    >>> print(result["transcript"])
    'Hola como estás'
    >>> print(result["score"])
    85
    >>> await stt.close()
"""

import httpx
import base64
import json
from typing import Dict, Any, Optional
from app.core.config import settings


class STTError(Exception):
    """Custom exception for STT-related errors."""
    pass


class STTClient:
    """
    Speech-to-Text and Phonetic Analysis Client.

    Uses Google Gemini 2.5 Flash to:
    1. Transcribe audio to text
    2. Analyze pronunciation quality
    3. Identify phonetic errors
    4. Provide correction tips

    Handles audio in various formats (webm, mp3, wav, etc.) via MIME types.
    """

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
        Transcribe audio and analyze pronunciation.

        Complete workflow:
        1. Base64 encode audio bytes
        2. Send to Gemini with target phrase and language context
        3. Gemini transcribes audio
        4. Gemini analyzes pronunciation quality
        5. Parse JSON response with structured feedback
        6. Return results to phonetics module

        Args:
            audio_bytes: Raw audio file bytes
            mime_type: Audio format MIME type (audio/webm, audio/mp3, audio/wav, etc.)
                      Default: "audio/webm"
            target_language: Language being analyzed (Spanish, French, German, etc.)
            target_phrase: Exact phrase user was supposed to say
                          Used as reference for phonetic analysis

        Returns:
            Dict containing:
            - transcript (str): Transcribed text (what STT heard)
            - confidence (float): Confidence score (0.0-1.0)
            - score (int): Pronunciation quality score (0-100)
            - feedback (str): Overall assessment of pronunciation
            - word_level_feedback (list): Array of word-specific feedback:
              [{
                "word": "word_that_was_spoken",
                "issue": "What was wrong (e.g., 'th' sound was 'z')",
                "tip": "How to fix (e.g., 'Place tongue between teeth')"
              }]

        Raises:
            STTError:
            - If HTTP request fails (network, auth, server error)
            - If response JSON is malformed
            - If Gemini returns unexpected response format
            - If no content in Gemini response

        Implementation Notes:
            - Base64 encodes audio for API transmission
            - Uses Gemini 2.5 Flash model for fast processing
            - temperature=0.2 for accurate transcription (low creativity)
            - Sets responseMimeType to "application/json" for structured output
            - Cleans markdown code blocks from JSON response (if present)
            - Defaults confidence to 1.0 if AI doesn't provide
            - Defaults word_level_feedback to empty array if missing
            - Timeout: 30 seconds

        Error Handling:
            - Catches httpx.HTTPError: Network/HTTP level errors
            - Catches json.JSONDecodeError: Invalid JSON from AI
            - Catches general Exception: Unexpected errors

        Gemini 2.5 Flash Integration:
            - Accepts both text prompts and audio inlineData
            - Analyzes phonetics as well as transcription
            - Returns structured JSON with pronunciation feedback
            - Provides word-level corrections and tips

        Example:
            >>> stt = get_stt_client()
            >>> result = await stt.analyze_audio(
            ...     audio_bytes=audio_file_content,
            ...     mime_type="audio/webm",
            ...     target_language="Spanish",
            ...     target_phrase="Hola, ¿cómo estás?"
            ... )
            >>> print(result["transcript"])
            'Hola como estás'
            >>> print(result["score"])
            85
            >>> print(result["word_level_feedback"])
            [
                {
                    "word": "estás",
                    "issue": "Accent on wrong syllable",
                    "tip": "es-TÁS (stress on second syllable)"
                }
            ]
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
        """Close the HTTP client connection cleanly."""
        await self.client.aclose()


# Global STT client instance
_stt_client: Optional[STTClient] = None


def get_stt_client() -> STTClient:
    """
    Get or create the singleton STTClient instance.

    Lazy initialization: Creates client on first call, reuses same instance
    on subsequent calls. Credentials loaded from environment (.env file).

    Returns:
        STTClient instance configured with API credentials

    Implementation Notes:
        - Thread-safe singleton pattern
        - Credentials from app.core.config.settings:
          - STT_API_KEY: Gemini API key
          - STT_API_BASE_URL: Gemini API endpoint base URL
          - STT_MODEL: Model identifier (gemini-2.5-flash)
        - Same instance reused across application
        - Client remains open until explicitly closed

    Example:
        >>> stt = get_stt_client()
        >>> result = await stt.analyze_audio(audio_bytes, "audio/webm", "Spanish", "Hola")
    """
    global _stt_client
    if _stt_client is None:
        _stt_client = STTClient(
            api_key=settings.STT_API_KEY,
            base_url=settings.STT_API_BASE_URL,
            model =settings.STT_MODEL
        )
    return _stt_client
