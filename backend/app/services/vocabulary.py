"""
Vocabulary Module Service Layer.

Handles all business logic for the Vocabulary learning module:
1. Generate AI flashcards (word + definition + multiple-choice options)
2. Validate content quality before showing to users
3. Record user answers and calculate statistics
4. Track progress and avoid showing repeated words

Key Functions:
    get_next_flashcard: Generate new vocabulary flashcard for user
    submit_vocabulary_answer: Record user answer and update progress

Workflow:
    1. Find/create user in database
    2. Get list of recently shown words to avoid repetition
    3. Create AI prompt with exclusions
    4. Call Gemini to generate flashcard JSON
    5. Parse response (strip markdown code blocks if present)
    6. Validate with checker AI
    7. Save to content_logs for audit
    8. Return flashcard to endpoint

Usage:
    flashcard = await get_next_flashcard("maria", "Spanish", "A1", db)
    # Returns FlashcardResponse with word, options, etc.
    
    answer = await submit_vocabulary_answer(request, db)
    # Records answer and updates user_progress table
"""

import json
from typing import Optional
from sqlalchemy.orm import Session
from uuid import uuid4
from app.db.models import User, ContentLog, UserProgress
from app.services.image_client import get_image_client
from app.core.config import settings

# Conditionally import Vertex AI client
if settings.USE_VERTEX_AI:
    try:
        from app.services.vertex_image_client import get_vertex_image_client
    except ImportError:
        print("Warning: Vertex AI not available. Install google-cloud-aiplatform.")
from app.services.ai_services import get_llm_client, get_checker_service, get_secondary_validator
from app.schemas.vocabulary import FlashcardResponse, VocabularyAnswerRequest, VocabularyAnswerResponse


async def get_next_flashcard(
    user_id: str,
    target_language: str,
    level: Optional[str],
    db: Session
) -> FlashcardResponse:
    """
    Generate next vocabulary flashcard for user.

    Complete workflow:
    1. Find or auto-create user in database
    2. Query recent words to avoid repetition (last 20)
    3. Create AI prompt with exclusion list
    4. Call Gemini to generate JSON flashcard
    5. Parse response and strip markdown code blocks
    6. Validate with checker AI (verify accuracy)
    7. Save to content_logs for audit trail
    8. Return flashcard to endpoint

    Args:
        user_id: Unique user identifier (string from frontend)
        target_language: Target language code (e.g., "Spanish", "French")
        level: CEFR level (A1, A2, B1, B2, C1, C2) or None for default
        db: SQLAlchemy database session

    Returns:
        FlashcardResponse containing:
        - word: Target language vocabulary word
        - definition: English definition
        - example_sentence: Example sentence using word (max 12 words)
        - options: List of 4 English definitions (1 correct, 3 plausible distractors)
        - correct_option_index: Index of correct answer (0-3)

    Raises:
        ValueError: If level is not valid CEFR level
        LLMError: If Gemini API call fails (rate limited, auth error)
        JSONDecodeError: If response is not valid JSON after cleanup

    Implementation Notes:
        - Gemini often wraps JSON in ```json``` markdown blocks
        - We strip these blocks before parsing
        - Checker AI validates that definition matches word
        - content_logs stores generated word for repetition avoidance
        - temperature=0.7 for vocabulary (allows creativity)

    Example:
        >>> flashcard = await get_next_flashcard("maria", "Spanish", "A1", db)
        >>> flashcard.word
        'Gato'
        >>> flashcard.options
        ['Cat', 'Dog', 'Bird', 'Fish']
        >>> flashcard.correct_option_index
        0
    """
    llm = get_llm_client()
    checker = get_checker_service()
    secondary_validator = get_secondary_validator()

    # Use Vertex AI if enabled, otherwise use legacy client
    if settings.USE_VERTEX_AI and settings.VERTEX_AI_PROJECT_ID:
        imm_client = get_vertex_image_client(
            credentials_path=settings.VERTEX_AI_CREDENTIALS_PATH,
            project_id=settings.VERTEX_AI_PROJECT_ID,
            location=settings.VERTEX_AI_LOCATION
        )
    else:
        imm_client = get_image_client()

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

    # Stage 1: Primary checker - format and basic validation
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

    # Stage 2: Secondary validation - deep accuracy and quality check
    secondary_validation = await secondary_validator.deep_validate(
        module="vocabulary",
        user_input={"target_language": target_language, "level": level},
        generated_content=json.dumps(flashcard_data),
        primary_validation=checker_result
    )

    # If secondary validator suggests improvement and has high confidence, use it
    if (not secondary_validation["is_approved"] and
        secondary_validation["improved_version"] and
        secondary_validation["confidence_score"] > 0.7):
        try:
            improved_data = json.loads(secondary_validation["improved_version"])
            flashcard_data = improved_data
        except (json.JSONDecodeError, TypeError, KeyError):
            pass  # Keep current version if parsing fails

    word = flashcard_data.get("word", "")
    definition = flashcard_data.get("definition", "")
    imm_b64 = None

    if word and definition:
        # Generate image
        image_prompt = f"{word}, meaning: {definition}"
        print(f"[DEBUG] Attempting to generate image for: {image_prompt}")
        print(f"[DEBUG] Using Vertex AI: {settings.USE_VERTEX_AI}")
        imm_b64 = await imm_client.generate_safe_image(image_prompt)
        print(f"[DEBUG] Image generated: {imm_b64 is not None}, size: {len(imm_b64) if imm_b64 else 0}")

    # update the field to be seen in the frontend
    flashcard_data["image_data"] = imm_b64

    # Add validation metadata for frontend display
    flashcard_data["validation"] = {
        "is_validated": checker_result["is_valid"] and secondary_validation["is_approved"],
        "confidence_score": secondary_validation.get("confidence_score"),
        "primary_check_passed": checker_result["is_valid"],
        "secondary_check_passed": secondary_validation["is_approved"]
    }

    # Log content with both validation stages
    content_log = ContentLog(
        user_id=user.id,
        module="vocabulary",
        input_payload={"target_language": target_language, "level": level},
        generated_content=flashcard_data,
        checker_result=checker_result,
        secondary_validation=secondary_validation,
        is_validated=checker_result["is_valid"] and secondary_validation["is_approved"]
    )
    db.add(content_log)
    db.commit()

    return FlashcardResponse(**flashcard_data)


async def submit_vocabulary_answer(
    request: VocabularyAnswerRequest,
    db: Session
) -> VocabularyAnswerResponse:
    """
    Submit vocabulary answer and update user progress.

    Records whether the user's answer was correct and updates statistics.

    Args:
        request: VocabularyAnswerRequest with:
            - user_id: User identifier
            - selected_option_index: Index of selected answer (0-3)
            - correct_option_index: Index of correct answer (0-3)
        db: Database session

    Returns:
        VocabularyAnswerResponse with:
        - is_correct: Whether answer was correct (bool)
        - correct_option_index: Index of correct answer
        - explanation: Brief feedback message

    Raises:
        ValueError: If user not found in database

    Side Effects:
        Updates user_progress table:
        - Increments total_attempts
        - Increments correct_attempts if answer is correct
        - Recalculates score percentage

    Example:
        >>> response = await submit_vocabulary_answer(
        ...     VocabularyAnswerRequest(
        ...         user_id="maria",
        ...         selected_option_index=0,
        ...         correct_option_index=0
        ...     ),
        ...     db
        ... )
        >>> response.is_correct
        True
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
