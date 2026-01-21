from google import genai
from google.genai import types
import logging
import json

# load config which is in thw lower directory
from app.core.config import settings

# set up a logger
logger = logging.getLogger(__name__)


class AIOrchestrator:
    """
    Enables two fundamental AI interactions for the chosen model in our app:
    1. Generating content (chat replies, vocab words, etc.)
    2. Verifying content (safety, correctness, helpfulness)
    """
    def __init__(self):
        # initialize Gemini with API Key from environment variables
        if not settings.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY not found in SETTINGS.")

        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

        # define two models: one for generation and one for checking (AI cross-check)
        # we use a lower temperature for the 'checker' to be more analytical
        self.model_name = "gemini-2.5-flash"

    async def generate_reply(self, system_prompt: str, user_message: str, history: list) -> str:
        """
        Orchestrates the generation and verification process for chat.
        """
        try:
            # Convert simple list history to Gemini's format if needed, else directly use it

            # constructing a stateless prompt chain
            full_prompt = f"{system_prompt}\n\nChat History:\n"
            # append context (linked list of strings)
            for msg in history:
                full_prompt += f"- {msg}\n"
            # append the new user message at the end
            full_prompt += f"\nUser: {user_message}\nTutor:"

            config = types.GenerateContentConfig(
                temperature=0.7
            )

            # Generate the raw response
            response =  self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config=config
            )
            raw_reply = response.text

            # verification, call it the oracle
            # we ask the AI to review its own output before sending it to the user.
            validated_reply = await self.verify_response(user_message, raw_reply)

            return validated_reply

        except Exception as e:
            logger.error(f"AI Generation Error: {str(e)}")
            return "I'm having trouble connecting to my brain right now. Can we try again?"

    async def verify_response(self, user_input: str, ai_reply: str) -> str:
        """
        For naive recursive prompting verification.  Uses a second model call to verify the first response.
        1. Checks for safety and appropriateness.
        2. Checks for grammatical correctness.
        3. Checks for helpfulness.
        """
        checker_prompt = (
            f"You are a strict language education supervisor.\n"
            f"Student said: '{user_input}'\n"
            f"Tutor proposed reply: '{ai_reply}'\n\n"
            f"Task: Verify if the Tutor's reply is:\n"
            f"1. Safe and appropriate.\n"
            f"2. Grammatically correct in the target language.\n"
            f"3. Helpful for a learner.\n\n"
            f"If it is good, strictly output: 'VALID'\n"
            f"If it contains errors or hallucinations, output a CORRECTED version only."
        )

        try:
            config = types.GenerateContentConfig(
                temperature=0.1
            )
            # run the checker (low temp)
            check_response = self.client.models.generate_content(
                model=self.model_name,
                contents=checker_prompt,
                config=config
            )
            checked_text = check_response.text.strip()

            return ai_reply if "VALID" in checked_text else checked_text

        except Exception as e:
            logger.error(f"Checker Error: {str(e)}")
            return ai_reply

    async def validate_vocabulary_match(self, language: str, target: str, guess: str) -> dict:
        """
        Validates if the user's guess matches the target word.
        Returns JSON: { "is_correct": bool, "feedback": str }
        """
        checker_prompt = (
            f"You are a strict language teacher.\n"
            f"Target Word ({language}): {target}\n"
            f"Student Guess: {guess}\n\n"
            "Task: Determine if the guess is a valid translation or description of the target word.\n"
            "Respond in JSON format only: {{ \"is_correct\": boolean, \"feedback\": \"string\" }}"
        )

        try:
            config = types.GenerateContentConfig(
                temperature=0.1
            )

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=checker_prompt,
                config=config
            )
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"Vocab Check Error: {e}")
            return {"is_correct": False, "feedback": "Error validating answer."}


# Singleton instance to be imported elsewhere
ai_orchestrator = AIOrchestrator()