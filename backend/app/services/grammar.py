"""
Grammar Module Service Layer.

Handles all business logic for the Grammar learning module:
1. Generate grammar questions with multiple-choice options
2. Create plausible distractors for realistic challenges
3. Validate question quality before showing to users
4. Record user answers and calculate statistics
5. Track progress and avoid question repetition

Key Functions:
    get_grammar_question: Generate new grammar question
    submit_grammar_answer: Record user answer and update progress

Workflow:
    1. Find/create user in database
    2. Get list of recent questions to avoid repetition
    3. Create AI prompt requesting grammar question
    4. Call Gemini to generate JSON question
    5. Parse response (strip markdown code blocks if present)
    6. Validate with checker AI
    7. Save to content_logs for audit
    8. Return question to endpoint

Question Format:
    - Sentence with blank (____)
    - 4 options (1 correct, 3 plausible distractors)
    - Explanation of grammar rule
    
Usage:
    question = await get_grammar_question("maria", "Spanish", "A1", None, db)
    # Returns GrammarQuestionResponse with question and options
    
    result = await submit_grammar_answer(request, db)
    # Records answer and updates user_progress table
"""

import json
from typing import Optional
from sqlalchemy.orm import Session
from uuid import uuid4
from app.db.models import User, ContentLog, UserProgress
from app.services.ai_services import get_llm_client, get_checker_service, get_secondary_validator
from app.schemas.grammar import GrammarQuestionResponse, GrammarAnswerRequest, GrammarAnswerResponse


async def get_grammar_question(
    user_id: str,
    target_language: str,
    level: Optional[str],
    topic: Optional[str],
    db: Session
) -> GrammarQuestionResponse:
    """
    Generate grammar question for user.

    Complete workflow:
    1. Find or auto-create user
    2. Query recent questions to avoid repetition (last 20)
    3. Create AI prompt with exclusion list and optional topic
    4. Call Gemini to generate JSON question
    5. Parse response and strip markdown code blocks
    6. Validate with checker AI
    7. Save to content_logs for audit
    8. Return question to endpoint

    Args:
        user_id: Unique user identifier
        target_language: Target language (Spanish, French, German, etc.)
        level: CEFR level (A1, A2, B1, B2, C1, C2) or None for default
        topic: Optional grammar topic (past tense, articles, subjunctive, etc.)
        db: SQLAlchemy database session

    Returns:
        GrammarQuestionResponse with:
        - question_text: The grammar question
        - options: List of 4 answer options
        - correct_option_index: Index of correct answer (0-3)
        - explanation: Why the correct answer is correct
        - question_id: Unique ID for tracking

    Raises:
        ValueError: If AI response is not valid JSON
        LLMError: If Gemini API call fails

    Implementation Notes:
        - Options are 4 plausible completions (1 correct, 3 distractors)
        - Distractors target common learner mistakes
        - Explanation teaches the grammar rule
        - temperature=0.7 for variety while maintaining correctness
        - max_tokens=2048 for detailed explanations
        - Topic parameter narrows focus (if provided)

    Example:
        >>> question = await get_grammar_question(
        ...     "maria", "Spanish", "A1", "past tense", db
        ... )
        >>> question.question_text
        'Ayer _____ al parque con mis amigos.'
        >>> question.options
        ['fui', 'voy', 'iré', 'vaya']
        >>> question.correct_option_index
        0
    """
    llm = get_llm_client()
    checker = get_checker_service()
    secondary_validator = get_secondary_validator()

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
    topic_info = f" about {topic}" if topic else ""

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

    prompt = f"""Generate a multiple-choice grammar question for learning {target_language}{level_info}{topic_info}.
    
    IMPORTANT: Do not suggest any sentence that is too similar to: {exclusions}.
    Please provide SHORT example sentences (MAX 12 words) that clearly illustrate the grammar point.

    Respond ONLY with valid JSON in this exact format:
    {{
      "question_text": "The question text",
      "options": ["option1", "option2", "option3", "option4"],
      "correct_option_index": 0,
      "explanation": "Brief explanation in English of why the correct answer is correct"
    }}"""

    # Generate question
    response = await llm.generate(
        system_prompt=f"You are a language learning content creator. Always respond with valid JSON only.",
        user_prompt=prompt,
        temperature=0.7,
        max_tokens=2048
    )

    try:
        cleaned = response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]

        question_data = json.loads(cleaned.strip())
    except (json.JSONDecodeError, ValueError) as e:
        # Prevent 500 Crash
        print(f"JSON Parse Error: {e}")
        # Return a fallback or re-raise a clean error
        raise ValueError("Failed to generate valid grammar question from AI.")

    # Stage 1: Primary checker - format and basic validation
    checker_result = await checker.check_content(
        module="grammar",
        original_instruction="Generate grammar question",
        user_input={"target_language": target_language, "level": level, "topic": topic},
        generated_content=json.dumps(question_data)
    )

    # If not valid and has suggested fix, try to use it
    if not checker_result["is_valid"] and checker_result["suggested_fix"]:
        try:
            question_data = json.loads(checker_result["suggested_fix"])
        except (TypeError, json.JSONDecodeError, KeyError):
            pass

    # Stage 2: Secondary validation - deep accuracy and quality check
    secondary_validation = await secondary_validator.deep_validate(
        module="grammar",
        user_input={"target_language": target_language, "level": level, "topic": topic},
        generated_content=json.dumps(question_data),
        primary_validation=checker_result
    )

    # If secondary validator suggests improvement and has high confidence, use it
    if (not secondary_validation["is_approved"] and
        secondary_validation["improved_version"] and
        secondary_validation["confidence_score"] > 0.7):
        try:
            improved_data = json.loads(secondary_validation["improved_version"])
            question_data = improved_data
        except (json.JSONDecodeError, TypeError, KeyError):
            pass  # Keep current version if parsing fails

    # Generate question ID
    question_id = str(uuid4())
    question_data["question_id"] = question_id

    # Add validation metadata for frontend display
    question_data["validation"] = {
        "is_validated": checker_result["is_valid"] and secondary_validation["is_approved"],
        "confidence_score": secondary_validation.get("confidence_score"),
        "primary_check_passed": checker_result["is_valid"],
        "secondary_check_passed": secondary_validation["is_approved"]
    }

    # Log content with both validation stages
    content_log = ContentLog(
        user_id=user.id,
        module="grammar",
        input_payload={"target_language": target_language, "level": level, "topic": topic},
        generated_content=question_data,
        checker_result=checker_result,
        secondary_validation=secondary_validation,
        is_validated=checker_result["is_valid"] and secondary_validation["is_approved"]
    )
    db.add(content_log)
    db.commit()

    return GrammarQuestionResponse(**question_data)


async def submit_grammar_answer(
    request: GrammarAnswerRequest,
    db: Session
) -> GrammarAnswerResponse:
    """
    Submit grammar answer and update user progress.

    Records answer correctness and updates user statistics.

    Args:
        request: GrammarAnswerRequest with:
            - user_id: User identifier
            - question_id: Question that was answered
            - selected_option_index: Index of selected answer (0-3)
            - correct_option_index: Index of correct answer (0-3)
        db: Database session

    Returns:
        GrammarAnswerResponse with:
        - is_correct: Whether answer was correct (bool)
        - correct_option_index: Index of correct answer
        - explanation: Explanation of the grammar rule

    Raises:
        ValueError: If user not found

    Side Effects:
        Updates user_progress table:
        - Increments total_attempts
        - Increments correct_attempts if correct
        - Recalculates score percentage
        - Updates last_activity_at timestamp

    Example:
        >>> response = await submit_grammar_answer(
        ...     GrammarAnswerRequest(
        ...         user_id="maria",
        ...         question_id="q123",
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
        UserProgress.module == "grammar"
    ).first()

    if not progress:
        progress = UserProgress(
            user_id=user.id,
            module="grammar",
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

    explanation = request.explanation or ("Correct!" if is_correct else f"The correct answer was option {request.correct_option_index}.")

    return GrammarAnswerResponse(
        is_correct=is_correct,
        correct_option_index=request.correct_option_index,
        explanation=explanation
    )
