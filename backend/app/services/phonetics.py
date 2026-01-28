"""
Phonetics Module Service Layer.

Handles all business logic for the Phonetics (pronunciation) learning module:
1. Generate target phrases for pronunciation practice
2. Process audio files using Speech-to-Text (STT)
3. Compare user's speech to target phrase
4. Provide pronunciation feedback and score
5. Track pronunciation progress

Key Features:
- Speech-to-Text integration (Google Cloud API)
- Word-level similarity comparison
- Pronunciation quality feedback from AI
- Fallback phrases if generation fails
- Error handling for audio processing

Key Functions:
    calculate_similarity: Compare two texts at word level
    generate_target_phrase: Create random phrase for practice
    evaluate_pronunciation: Analyze user's pronunciation

Workflow:
    1. Generate target phrase in target language
    2. User records audio of themselves saying phrase
    3. STT transcribes audio to text
    4. Compare transcribed vs target text
    5. AI provides pronunciation feedback
    6. Calculate similarity score (0-100)
    7. Return feedback and score to user

Usage:
    session = await generate_target_phrase("Spanish", "A1")
    # Returns phrase like: "Hola, ¿cómo estás?"
    
    evaluation = await evaluate_pronunciation(
        "maria", "Spanish", "Hola, ¿cómo estás?", audio_bytes, db
    )
    # Returns score, transcript, feedback
"""

import json
from typing import Dict
from sqlalchemy.orm import Session
from uuid import uuid4
from app.db.models import User, ContentLog, UserProgress
from app.services.ai_services import get_llm_client
from app.services.stt_client import get_stt_client
from app.schemas.phonetics import PhoneticsEvaluationResponse, PhoneticsPracticeSession


def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate word-level similarity between two texts.

    Compares how many words from text1 appear in text2.
    Uses AI for more accurate comparison than simple word matching.

    Args:
        text1: First text (user's transcription)
        text2: Second text (target phrase)

    Returns:
        Similarity percentage (0-100)

    Implementation Notes:
        - Returns 0 if either text is empty
        - Uses Gemini API for accurate comparison
        - temperature=0.0 for deterministic results
        - Handles parsing errors gracefully (returns 0)
        - Returns clamped value [0, 100]

    Example:
        >>> similarity = calculate_similarity(
        ...     "Hola como estás",
        ...     "Hola, ¿cómo estás?"
        ... )
        >>> similarity
        100.0
    """
    words1 = text1.lower().split()
    words2 = text2.lower().split()

    llm = get_llm_client()

    if not words1 or not words2:
        return 0.0
    else:
        comp_prompt = f"""
        You are a text comparison AI. Given two texts, calculate the percentage of words in the first text that appear in the second text.
        Text 1: "{text1}"
        Text 2: "{text2}"
        Respond ONLY with a number between 0 and 100 representing the percentage.
        """
        response = llm.generate(
            system_prompt="You are a precise text comparison AI. Respond ONLY with a number.",
            user_prompt=comp_prompt,
            temperature=0.0,
            max_tokens=10
        )
        try:
            similarity = float(response.strip())
            return max(0.0, min(100.0, similarity))
        except (TypeError, ValueError):
            return 0.0


async def generate_target_phrase(
        target_language: str,
        level: str
) -> PhoneticsPracticeSession:
    """
    Generate random phrase for pronunciation practice.

    Creates a short, natural sentence at appropriate level for student
    to practice speaking aloud.

    Args:
        target_language: Language code (Spanish, French, German, etc.)
        level: CEFR level (A1, A2, B1, B2, C1, C2)

    Returns:
        PhoneticsPracticeSession with:
        - session_id: Unique ID for this practice session
        - target_phrase: The phrase to pronounce

    Implementation Notes:
        - Phrase length: 5-10 words (manageable for learners)
        - No complex punctuation
        - Natural, conversational sentences
        - Uses fallback if generation fails
        - temperature=0.9 for variety

    Example:
        >>> session = await generate_target_phrase("Spanish", "A1")
        >>> session.target_phrase
        'Hola, ¿cómo estás hoy?'
    """
    llm = get_llm_client()

    prompt = f"""Generate a single, simple, natural sentence for pronunciation practice in {target_language} for a {level} level student.

    Rules:
    1. Length: 5-10 words.
    2. No complex punctuation.
    3. Respond ONLY with the sentence text. No quotes, no translations."""

    phrase_text = "Hola, ¿cómo estás hoy?"  # Default fallback

    try:
        response = await llm.generate(
            system_prompt="You are a language teacher.",
            user_prompt=prompt,
            temperature=0.9,
            max_tokens=512
        )
        phrase_text = response.strip().replace('"', '')
    except (ValueError, TypeError):
        print("[DEBUG] LLM phrase generation failed, using fallback.")

    # Generate the ID *after* the try/except block
    session_id = str(uuid4())

    # Return the full object
    return PhoneticsPracticeSession(
        session_id=session_id,
        target_phrase=phrase_text
    )

async def evaluate_pronunciation(
    user_id: str,
    target_language: str,
    target_phrase: str,
    audio_bytes: bytes,
    db: Session
) -> PhoneticsEvaluationResponse:
    """
    Evaluate user's pronunciation using STT and AI analysis.

    Complete workflow:
    1. Transcribe audio using Google Speech-to-Text
    2. Compare transcription with target phrase
    3. Use AI to evaluate pronunciation quality
    4. Calculate similarity score
    5. Save results to database
    6. Return feedback

    Args:
        user_id: Unique user identifier
        target_language: Target language code (es-ES, fr-FR, de-DE, etc.)
        target_phrase: The phrase user should pronounce
        audio_bytes: Audio file as bytes (WAV, MP3, etc.)
        db: SQLAlchemy database session

    Returns:
        PhoneticsEvaluationResponse with:
        - transcribed_text: What STT heard
        - similarity_score: Match percentage (0-100)
        - feedback: Pronunciation tips and improvements
        - suggestions: List of things to work on

    Raises:
        ValueError: If audio cannot be transcribed
        LLMError: If Gemini API call fails

    Side Effects:
        - Creates User record if not exists
        - Logs evaluation in content_logs
        - Updates user_progress phonetics stats

    Implementation Notes:
        - STT may have errors with accents/dialects
        - Similarity calculated word-by-word
        - AI feedback focuses on pronunciation patterns
        - temperature=0.5 for balanced feedback
        - Stores both transcription and target for audit
        - Similarity clamped to [0, 100]

    Example:
        >>> evaluation = await evaluate_pronunciation(
        ...     "maria",
        ...     "Spanish",
        ...     "Hola, ¿cómo estás?",
        ...     audio_file_bytes,
        ...     db
        ... )
        >>> evaluation.similarity_score
        85.5
        >>> evaluation.transcribed_text
        'Hola como estás'
    """
    stt = get_stt_client()

    # Find or create user
    user = db.query(User).filter(User.external_id == user_id).first()
    if not user:
        user = User(external_id=user_id)
        db.add(user)
        db.commit()
        db.refresh(user)

    # Transcribe audio
    analysis_result = await stt.analyze_audio(audio_bytes,
    target_language=target_language,
    target_phrase=target_phrase
    )

    transcript = analysis_result.get("transcript", "")
    stt_confidence = analysis_result.get("confidence", 0.0)
    score = analysis_result.get("score", 0.0)
    feedback = analysis_result.get("feedback", "No feedback provided.")
    word_level_feedback = analysis_result.get("word_level_feedback", [])

    # Voice recording error handling
    if stt_confidence < 0.6:
        feedback = f"⚠️ Low audio quality. Please try speaking again. (AI heard: '{transcript}')"
        score = max(score, 10.0)

    progress = db.query(UserProgress).filter(
        UserProgress.user_id == user.id,
        UserProgress.module == "phonetics"
    ).first()

    if not progress:
        progress = UserProgress(
            user_id=user.id,
            module="phonetics",
            total_attempts=1,
            score=score
        )
        db.add(progress)
    else:
        progress.total_attempts += 1
        if progress.score is not None:
            progress.score = (progress.score + score) / 2
        else:
            progress.score = score

    db.commit()

    # Log content
    content_log = ContentLog(
        user_id=user.id,
        module="phonetics",
        input_payload={
            "target_language": target_language,
            "target_phrase": target_phrase
        },
        generated_content=analysis_result,
        checker_result=None,
        is_validated=True
    )
    db.add(content_log)
    db.commit()

    return PhoneticsEvaluationResponse(
        transcript=transcript,
        stt_confidence=stt_confidence,
        score=score,
        feedback=feedback,
        word_level_feedback=word_level_feedback
    )
