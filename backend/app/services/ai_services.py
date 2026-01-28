"""
AI Services Module - Gemini API Integration and Content Validation.

This module provides core AI functionality for the Language Learning App:
1. LLMClient: Wrapper for Google Gemini API calls
2. CheckerService: Validates AI-generated content for accuracy

Key Features:
- Async HTTP client for Gemini API communication
- JSON response parsing (handles markdown code block wrapping)
- Content validation using a separate "checker" AI
- Error handling with custom LLMError exception

Main Classes:
    LLMClient: Generate content using Gemini API
    CheckerService: Validate generated content quality
    LLMError: Custom exception for LLM-related errors

Usage Example:
    >>> llm = LLMClient(api_key="...", base_url="...", model="gemini-1.5-flash")
    >>> response = await llm.generate(
    ...     system_prompt="You are a language teacher",
    ...     user_prompt="Generate a Spanish vocabulary word",
    ...     temperature=0.7
    ... )
    >>> await llm.close()
"""

import httpx
import json
from typing import Dict, Any, Optional
from app.core.config import settings


class LLMError(Exception):
    """Custom exception for LLM-related errors."""
    pass


class LLMClient:
    """Client for interacting with LLM API (Gemini)."""

    def __init__(self, api_key: str, base_url: str, model: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.client = httpx.AsyncClient(timeout=30.0)

    async def generate(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 512
    ) -> str:
        """
        Generate content using Google Gemini API.

        Sends a combined prompt to Gemini and returns the raw response text.
        Automatically extracts text from the nested Gemini response structure.

        Args:
            system_prompt: System-level instructions (e.g., "You are a language teacher")
            user_prompt: User input/query (e.g., "Generate a vocabulary word")
            temperature: Creativity level (0.0=deterministic, 1.0=creative)
                        Use 0.3 for grammar (needs accuracy)
                        Use 0.7 for vocabulary (can be creative)
            max_tokens: Maximum response length (prevents long outputs)

        Returns:
            Raw response text from Gemini (may contain markdown code blocks)

        Raises:
            LLMError: If HTTP request fails or response format is unexpected
            
        Note:
            Responses are often wrapped in ```json``` code blocks.
            Caller is responsible for parsing/cleaning the response.
            
        Example:
            >>> response = await llm.generate(
            ...     system_prompt="You are a Spanish teacher",
            ...     user_prompt="Generate an A1 vocabulary word as JSON",
            ...     temperature=0.7,
            ...     max_tokens=512
            ... )
            >>> print(response)
            '```json\\n{"word": "Gato", ...}\\n```'
        """
        try:
            # Combine system and user prompts for Gemini API
            combined_prompt = f"{system_prompt}\n\n{user_prompt}"

            # Gemini API endpoint
            url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"

            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": combined_prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens,
                }
            }

            response = await self.client.post(url, json=payload)
            response.raise_for_status()

            data = response.json()

            # Extract text from Gemini response
            if "candidates" in data and len(data["candidates"]) > 0:
                candidate = data["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]
                    if len(parts) > 0 and "text" in parts[0]:
                        return parts[0]["text"]

            raise LLMError("Unexpected response format from LLM API")

        except httpx.HTTPError as e:
            raise LLMError(f"HTTP error during LLM API call: {str(e)}")
        except Exception as e:
            raise LLMError(f"Error during LLM generation: {str(e)}")

    async def close(self):
        """Close the HTTP client connection."""
        await self.client.aclose()


class CheckerService:
    """
    Content Validation Service using AI.

    Validates AI-generated content to ensure accuracy before showing to users.
    Part of the "Generate then Verify" pattern to prevent AI hallucinations.
    
    This service uses a separate LLM instance to critique content generated
    by the main LLM, providing an additional quality assurance layer.
    """

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    async def check_content(
        self,
        *,
        module: str,
        original_instruction: str,
        user_input: Dict[str, Any],
        generated_content: str
    ) -> Dict[str, Any]:
        """
        Validate AI-generated content using another LLM call.

        Part of "Generate then Verify" pattern:
        1. Generate content (main LLM)
        2. Validate content (checker LLM) <- This function
        3. If valid, use; if invalid, regenerate or use fallback

        Args:
            module: The learning module name (vocabulary, grammar, writing, etc.)
            original_instruction: The prompt used to generate content
            user_input: Input parameters as dict (language, level, topic, etc.)
            generated_content: The content to validate (usually JSON string)

        Returns:
            Dict with keys:
            - is_valid (bool): Whether content passes validation
            - issues (list): List of identified problems (if any)
            - suggested_fix (str or None): Corrected version (if available)

        Raises:
            LLMError: If validation API call fails

        Example:
            >>> result = await checker.check_content(
            ...     module="vocabulary",
            ...     original_instruction="Generate Spanish word",
            ...     user_input={"language": "Spanish", "level": "A1"},
            ...     generated_content='{"word": "Gato", "definition": "Cat"}'
            ... )
            >>> print(result["is_valid"])
            True
        """
        user_input_json = json.dumps(user_input, indent=2)

        checker_prompt = f"""You are a strict language-learning evaluator.

MODULE: {module}
INSTRUCTION: {original_instruction}
USER_INPUT: {user_input_json}
GENERATED_CONTENT: {generated_content}

Your task:
1. Check for factual or grammatical errors.
2. Check if content is appropriate and at the right difficulty for a language learner.
3. If there are issues, explain them and provide a corrected version.

Respond ONLY with valid JSON in this exact format:
{{
  "is_valid": true or false,
  "issues": ["issue 1", "issue 2"],
  "suggested_fix": "corrected version or null"
}}"""

        try:
            response = await self.llm.generate(
                system_prompt="You are a language learning content validator. Always respond with valid JSON only.",
                user_prompt=checker_prompt,
                temperature=0.1,
                max_tokens=1024
            )

            # Try to parse JSON from response
            # Sometimes LLM adds Markdown code blocks, so clean it up
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.startswith("```"):
                cleaned_response = cleaned_response[3:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()

            result = json.loads(cleaned_response)

            # Validate structure
            if "is_valid" not in result:
                result["is_valid"] = True
            if "issues" not in result:
                result["issues"] = []
            if "suggested_fix" not in result:
                result["suggested_fix"] = None

            return result

        except json.JSONDecodeError:
            # If checker fails to return valid JSON, assume content is valid
            return {
                "is_valid": True,
                "issues": ["Checker returned invalid JSON"],
                "suggested_fix": None
            }
        except Exception as e:
            # On any error, assume content is valid to not block the flow
            return {
                "is_valid": True,
                "issues": [f"Checker error: {str(e)}"],
                "suggested_fix": None
            }


class SecondaryValidatorService:
    """
    Secondary AI validator for deeper content verification.
    Performs comprehensive validation for accuracy, educational value, and appropriateness.
    """

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    async def deep_validate(
        self,
        *,
        module: str,
        user_input: Dict[str, Any],
        generated_content: str,
        primary_validation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform deep validation of content after primary check.

        Args:
            module: The learning module
            user_input: User input data
            generated_content: The content to validate
            primary_validation: Results from the primary checker

        Returns:
            Dict with comprehensive validation results
        """
        user_input_json = json.dumps(user_input, indent=2)
        primary_issues = ", ".join(primary_validation.get("issues", [])) or "None"

        validator_prompt = f"""You are an expert language learning content auditor performing a comprehensive review.

MODULE: {module}
USER_INPUT: {user_input_json}
GENERATED_CONTENT: {generated_content}
PRIMARY_CHECKER_ISSUES: {primary_issues}

Perform a deep validation checking:
1. **Accuracy**: Are all language examples, translations, and definitions factually correct?
2. **Educational Value**: Is this content truly helpful for language learning at the specified level?
3. **Cultural Sensitivity**: Is the content culturally appropriate and respectful?
4. **Difficulty Match**: Does the difficulty match the user's specified level?
5. **Pedagogical Quality**: Does this follow best practices in language teaching?
6. **Safety**: Is there any inappropriate, offensive, or harmful content?

Respond ONLY with valid JSON in this exact format:
{{
  "is_approved": true or false,
  "confidence_score": 0.0 to 1.0,
  "validation_details": {{
    "accuracy": "pass/fail with brief note",
    "educational_value": "pass/fail with brief note",
    "cultural_sensitivity": "pass/fail with brief note",
    "difficulty_match": "pass/fail with brief note",
    "pedagogical_quality": "pass/fail with brief note",
    "safety": "pass/fail with brief note"
  }},
  "critical_issues": ["issue 1", "issue 2"],
  "recommendations": ["recommendation 1", "recommendation 2"],
  "improved_version": "improved content or null"
}}"""

        try:
            response = await self.llm.generate(
                system_prompt="You are an expert language learning content auditor. Always respond with valid JSON only.",
                user_prompt=validator_prompt,
                temperature=0.05,  # Very low temperature for consistency
                max_tokens=2048
            )

            # Clean up response
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.startswith("```"):
                cleaned_response = cleaned_response[3:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()

            result = json.loads(cleaned_response)

            # Validate structure
            if "is_approved" not in result:
                result["is_approved"] = True
            if "confidence_score" not in result:
                result["confidence_score"] = 0.8
            if "validation_details" not in result:
                result["validation_details"] = {}
            if "critical_issues" not in result:
                result["critical_issues"] = []
            if "recommendations" not in result:
                result["recommendations"] = []
            if "improved_version" not in result:
                result["improved_version"] = None

            return result

        except json.JSONDecodeError:
            # If validator fails, return permissive result
            return {
                "is_approved": True,
                "confidence_score": 0.5,
                "validation_details": {},
                "critical_issues": ["Secondary validator returned invalid JSON"],
                "recommendations": [],
                "improved_version": None
            }
        except Exception as e:
            # On any error, return permissive result
            return {
                "is_approved": True,
                "confidence_score": 0.5,
                "validation_details": {},
                "critical_issues": [f"Secondary validator error: {str(e)}"],
                "recommendations": [],
                "improved_version": None
            }


# Global LLM client instance
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """Get or create the global LLM client instance."""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_API_BASE_URL,
            model=settings.LLM_MODEL
        )
    return _llm_client


def get_checker_service() -> CheckerService:
    """Get a checker service instance."""
    return CheckerService(get_llm_client())


def get_secondary_validator() -> SecondaryValidatorService:
    """Get a secondary validator service instance."""
    return SecondaryValidatorService(get_llm_client())
