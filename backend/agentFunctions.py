import logging
# Import the orchestrator instance
from AIOrchestrator import ai_orchestrator

logger = logging.getLogger(__name__)


async def get_chat_reply(language: str, user_msg: str, context: list) -> str:
    """Standard Chat Logic"""
    system_instruction = (
        f"You are a friendly {language} tutor. "
        "Keep responses concise. Correct grammar mistakes gently at the end."
    )

    # Call Orchestrator (Generation + Safety Check)
    reply = await ai_orchestrator.generate_reply(system_prompt=system_instruction, user_message=user_msg,
                                                 history=context)
    return reply


async def get_vocab_word(language: str) -> str:
    """Generates a single vocabulary word"""
    system_instruction = (
        f"Provide a single {language} vocabulary word suitable for a beginner. "
        "It must be a concrete noun that is easy to visualize (e.g., Apple, Dog, Car). "
        "Output ONLY the word, no punctuation."
    )

    # We pass an empty history since vocab generation is stateless
    word = await ai_orchestrator.generate_reply(system_prompt=system_instruction, user_message="Generate Word",
                                                history=[])
    return word.strip()


async def check_vocab_guess(language: str, target_word: str, user_guess: str) -> dict:
    """
    USES THE CROSS-CHECKER AI to validate the guess.
    """
    # We ask the Orchestrator specifically to judge correctness
    verdict = await ai_orchestrator.validate_vocabulary_match(
        language=language,
        target=target_word,
        guess=user_guess
    )
    return verdict

async def get_vocab_image(word: str, language: str) -> str:
    """
    Creates a simple prompt for the external image generator.
    """
    #prompt to make sure style consistency
    prompt = (
        f"A high-quality, 3D render style educational illustration of a '{word}' "
        f"(the {language} word). "
        "Isolated on a clean white background. "
        "Bright lighting, friendly style suitable for a language learning application. "
        "No text or letters inside the image."
    ) 
    
    return await ai_orchestrator.generate_image(prompt)