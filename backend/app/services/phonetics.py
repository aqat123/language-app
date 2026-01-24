import json
from typing import Dict
from sqlalchemy.orm import Session
from uuid import uuid4
from app.db.models import User, ContentLog, UserProgress
from app.services.ai_services import get_llm_client
from app.services.stt_client import get_stt_client
from app.schemas.phonetics import PhoneticsEvaluationResponse, PhoneticsPracticeSession


def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate simple word-level similarity between two texts."""
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
    """Generate a random phrase and session ID."""
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
    Evaluate pronunciation using STT and LLM analysis.

    Args:
        user_id: External user ID
        target_language: Target language code (e.g., "en-US", "es-ES")
        target_phrase: Expected phrase
        audio_bytes: Audio file bytes
        db: Database session

    Returns:
        PhoneticsEvaluationResponse with transcript, score, and feedback
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
