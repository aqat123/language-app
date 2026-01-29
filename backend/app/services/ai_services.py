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
        Call the LLM with the given prompts and return the generated text.

        Args:
            system_prompt: System-level instructions for the LLM
            user_prompt: User input/query
            temperature: Controls randomness (0.0-1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text from the LLM

        Raises:
            LLMError: If the API call fails
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
        """Close the HTTP client."""
        await self.client.aclose()


class CheckerService:
    """Service for validating AI-generated content using LLM as a checker."""

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
        Use LLM to critique/verify generated content.

        Args:
            module: The learning module (e.g., "conversation", "vocabulary")
            original_instruction: The original prompt/instruction
            user_input: User input data as dict
            generated_content: The content to validate

        Returns:
            Dict with keys: is_valid (bool), issues (list), suggested_fix (str or None)
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
