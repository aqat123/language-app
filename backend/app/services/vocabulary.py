import json
from typing import Optional
from sqlalchemy.orm import Session
from uuid import uuid4
from app.db.models import User, ContentLog, UserProgress
from app.services.ai_services import get_llm_client, get_checker_service
from app.schemas.vocabulary import FlashcardResponse, VocabularyAnswerRequest, VocabularyAnswerResponse


async def get_next_flashcard(
    user_id: str,
    target_language: str,
    level: Optional[str],
    db: Session
) -> FlashcardResponse:
    """
    Generate a vocabulary flashcard.

    Args:
        user_id: External user ID
        target_language: Target language
        level: Difficulty level
        db: Database session

    Returns:
        FlashcardResponse with word, definition, example, and options
    """
    llm = get_llm_client()
    checker = get_checker_service()

    # Find or create user
    user = db.query(User).filter(User.external_id == user_id).first()
    if not user:
        user = User(
            external_id=user_id,
            target_language=target_language,
            level=level
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    level_info = f" at {level} level" if level else ""

    # Last 20 seen words to avoid repetition
    recent_logs = db.query(ContentLog) \
        .filter(ContentLog.user_id == user.id, ContentLog.module == "vocabulary") \
        .order_by(ContentLog.created_at.desc()) \
        .limit(20) \
        .all()

    # Extract just the words
    seen_words = []
    for log in recent_logs:
        if log.generated_content and isinstance(log.generated_content, dict):
            word = log.generated_content.get("word")
            if word:
                seen_words.append(word)

    exclusions = ", ".join(seen_words)

    prompt = f"""Generate a vocabulary flashcard for learning {target_language}{level_info}

        IMPORTANT: Do NOT use any of the following words: {exclusions}.
        Pick a random, unique word that is different from the ones listed above.
        Please provide SHORT example sentences (MAX 12 words) that clearly illustrate the meaning of the word.

        Respond ONLY with valid JSON in this exact format:
        {{
          "word": "word in {target_language}",
          "definition": "definition in English",
          "example_sentence": "example sentence using the word in {target_language}",
          "options": ["option1", "option2", "option3", "option4"],
          "correct_option_index": 0
        }}

        The options should be 4 English definitions (one correct, three plausible distractors)."""

    # Generate flashcard
    response = await llm.generate(
        system_prompt=f"You are a language learning content creator. Always respond with valid JSON only.",
        user_prompt=prompt,
        temperature=0.7,
        max_tokens=1024
    )

    # Parse JSON
    cleaned = response.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]

    flashcard_data = json.loads(cleaned.strip())

    # Check content
    checker_result = await checker.check_content(
        module="vocabulary",
        original_instruction="Generate vocabulary flashcard",
        user_input={"target_language": target_language, "level": level},
        generated_content=json.dumps(flashcard_data)
    )

    # If not valid and has suggested fix, try to use it
    if not checker_result["is_valid"] and checker_result["suggested_fix"]:
        try:
            flashcard_data = json.loads(checker_result["suggested_fix"])
        except (json.JSONDecodeError, TypeError, KeyError):
            pass  # Keep original if parsing fails

    # Log content
    content_log = ContentLog(
        user_id=user.id,
        module="vocabulary",
        input_payload={"target_language": target_language, "level": level},
        generated_content=flashcard_data,
        checker_result=checker_result,
        is_validated=checker_result["is_valid"]
    )
    db.add(content_log)
    db.commit()

    return FlashcardResponse(**flashcard_data)


async def submit_vocabulary_answer(
    request: VocabularyAnswerRequest,
    db: Session
) -> VocabularyAnswerResponse:
    """
    Submit a vocabulary answer and get feedback.


    Args:
        request: Answer submission request
        db: Database session

    Returns:
        VocabularyAnswerResponse with correctness and explanation
    """
    user = db.query(User).filter(User.external_id == request.user_id).first()
    if not user:
        raise ValueError("User not found")

    is_correct = request.selected_option_index == request.correct_option_index

    # Update user progress
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == user.id,
        UserProgress.module == "vocabulary"
    ).first()

    if not progress:
        progress = UserProgress(
            user_id=user.id,
            module="vocabulary",
            total_attempts=1,
            correct_attempts=1 if is_correct else 0
        )
        db.add(progress)
    else:
        progress.total_attempts += 1
        if is_correct:
            progress.correct_attempts += 1

    # Calculate score
    if progress.total_attempts > 0:
        progress.score = (progress.correct_attempts / progress.total_attempts) * 100

    db.commit()

    explanation = "Correct!" if is_correct else f"The correct answer was option {request.correct_option_index}."

    return VocabularyAnswerResponse(
        is_correct=is_correct,
        correct_option_index=request.correct_option_index,
        explanation=explanation
    )
