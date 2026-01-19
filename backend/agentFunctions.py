# libraries to enable agent

# tell we are usign the other class
import logging
import AIOrchestrator

# we use a logger for debugging and info
logger = logging.getLogger(__name__)

# contains the app backend logic (manages it)
async def get_reply(language: str, user_msg: str, context: list):
    """
        Business logic to handle conversation flow.

        Args:
            :param language: The target language (e.g., "German", "Spanish")
            :param context: List of previous message strings (history).
            :param user_msg: The latest user message string.
        """

    # instructs the AI on how to behave specifically for these type of requests (role prompt)
    system_instruction = (
        f"You are a friendly and patient {language} language tutor. "
        f"Your goal is to help the user practice {language} conversation. "
        "Keep your responses concise (1-3 sentences) to keep the conversation flowing. "
        "If the user makes a grammar mistake, gently correct them at the end of your response "
        "inside parentheses like this: (Correction: ...). "
        "Do not switch to English unless the user is completely stuck."
    )

    # log request
    logger.info(f"Conversation Request - Lang: {language}, User: {user_msg}")

    # call the AI Orchestrator
    reply = await AIOrchestrator.ai_orchestrator.generate_conversation_reply(
        system_prompt=system_instruction,
        user_message=user_msg,
        history=context
    )

    return reply