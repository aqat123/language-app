import json
from typing import Dict
from sqlalchemy.orm import Session
from app.db.models import User, ContentLog, UserProgress
from app.services.ai_services import get_llm_client
from app.services.stt_client import get_stt_client
from app.schemas.phonetics import PhoneticsEvaluationResponse


def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate simple word-level similarity between two texts."""
    words1 = text1.lower().split()
    words2 = text2.lower().split()

    if not words1 or not words2:
        return 0.0

    matches = sum(1 for w in words1 if w in words2)
    return (matches / max(len(words1), len(words2))) * 100


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
    llm = get_llm_client()

    # Find or create user
    user = db.query(User).filter(User.external_id == user_id).first()
    if not user:
        user = User(external_id=user_id)
        db.add(user)
        db.commit()
        db.refresh(user)

    # Transcribe audio
    stt_result = await stt.transcribe(audio_bytes, language_code=target_language)
    transcript = stt_result["transcript"]
    stt_confidence = stt_result["confidence"]

    # Calculate basic similarity score
    similarity = calculate_similarity(target_phrase, transcript)

    # Get detailed feedback from LLM
    feedback_prompt = f"""The target phrase is: "{target_phrase}"
The student's pronunciation was transcribed as: "{transcript}"
ASR confidence: {stt_confidence:.2f}

Analyze the pronunciation differences and provide specific feedback.
Give a pronunciation score between 0 and 100 (100 is perfect).
Optionally provide word-level feedback if there are specific pronunciation issues.

Respond ONLY with valid JSON in this exact format:
{{
  "score": 85,
  "feedback": "Detailed feedback on pronunciation quality",
  "word_level_feedback": {{"word1": "feedback", "word2": "feedback"}}
}}

If there are no significant word-level issues, set word_level_feedback to null."""

    feedback_response = await llm.generate(
        system_prompt="You are a pronunciation coach. Always respond with valid JSON only.",
        user_prompt=feedback_prompt,
        temperature=0.3,
        max_tokens=512
    )

    # Parse feedback
    cleaned = feedback_response.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]

    try:
        feedback_data = json.loads(cleaned.strip())
        score = feedback_data.get("score", similarity)
        feedback = feedback_data.get("feedback", "Good effort!")
        word_level_feedback = feedback_data.get("word_level_feedback")
    except:
        # Fallback to simple scoring if LLM parsing fails
        score = similarity
        feedback = f"Your pronunciation was {similarity:.0f}% accurate."
        word_level_feedback = None

    # Update user progress
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
        # Update average score
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
        generated_content={
            "transcript": transcript,
            "score": score,
            "feedback": feedback,
            "word_level_feedback": word_level_feedback
        },
        checker_result=None,  # No checker for this module
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
