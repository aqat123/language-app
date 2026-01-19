import google.generativeai as genai
import logging

# load config which is in thw lower directory
from app.core.config import settings

# set up a logger
logger = logging.getLogger(__name__)


class AIOrchestrator:
    def __init__(self):
        # initialize Gemini with API Key from environment variables
        if not settings.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY not found in SETTINGS.")

        genai.configure(api_key=settings.GEMINI_API_KEY)

        # define two models: one for generation and one for checking (AI cross-check)
        # we use a lower temperature for the 'checker' to be more analytical
        self.generator_model = genai.GenerativeModel('gemini-pro')
        self.checker_model = genai.GenerativeModel('gemini-pro')

    async def generate_conversation_reply(self, system_prompt: str, user_message: str, history: list) -> str:
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

            # Generate the raw response
            response = await self.generator_model.generate_content_async(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,  # Creative for conversation
                )
            )
            raw_reply = response.text

            # verification, call it the oracle
            # we ask the AI to review its own output before sending it to the user.
            validated_reply = await self._verify_response(user_message, raw_reply)

            return validated_reply

        except Exception as e:
            logger.error(f"AI Generation Error: {str(e)}")
            return "I'm having trouble connecting to my brain right now. Can we try again?"

    async def _verify_response(self, user_input: str, ai_reply: str) -> str:
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
            # run the checker (low temp)
            check_response = await self.checker_model.generate_content_async(
                checker_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1
                )
            )
            checked_text = check_response.text.strip()

            if "VALID" in checked_text:
                return ai_reply
            else:
                # if the checker rewrote it we replace the original
                logger.info(f"Checker corrected the response. Original: {ai_reply} -> New: {checked_text}")
                return checked_text

        except Exception as e:
            logger.error(f"Checker Error: {str(e)}")
            # Fallback: if checker fails, return original
            return ai_reply


# Singleton instance to be imported elsewhere
ai_orchestrator = AIOrchestrator()