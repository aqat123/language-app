import json
from typing import Optional
from sqlalchemy.orm import Session
from uuid import uuid4
from app.db.models import User, ContentLog, UserProgress
from app.services.ai_services import get_llm_client, get_checker_service
from app.schemas.grammar import GrammarQuestionResponse, GrammarAnswerRequest, GrammarAnswerResponse


async def get_grammar_question(
    user_id: str,
    target_language: str,
    level: Optional[str],
    topic: Optional[str],
    db: Session
) -> GrammarQuestionResponse:
    """
    Generate a grammar question.

    Args:
        user_id: External user ID
        target_language: Target language
        level: Difficulty level
        topic: Grammar topic (e.g., "past tense", "articles")
        db: Database session

    Returns:
        GrammarQuestionResponse with question and options
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
    topic_info = f" about {topic}" if topic else ""
    prompt = f"""Generate a multiple-choice grammar question for learning {target_language}{level_info}{topic_info}.

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
        max_tokens=512
    )

    # Parse JSON
    cleaned = response.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]

    question_data = json.loads(cleaned.strip())

    # Check content
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
        except:
            pass

    # Generate question ID
    question_id = str(uuid4())
    question_data["question_id"] = question_id

    # Log content
    content_log = ContentLog(
        user_id=user.id,
        module="grammar",
        input_payload={"target_language": target_language, "level": level, "topic": topic},
        generated_content=question_data,
        checker_result=checker_result,
        is_validated=checker_result["is_valid"]
    )
    db.add(content_log)
    db.commit()

    return GrammarQuestionResponse(**question_data)


async def submit_grammar_answer(
    request: GrammarAnswerRequest,
    db: Session
) -> GrammarAnswerResponse:
    """
    Submit a grammar answer and get feedback.

    Args:
        request: Answer submission request
        db: Database session

    Returns:
        GrammarAnswerResponse with correctness and explanation
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
