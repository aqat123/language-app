import json
from typing import Optional
from sqlalchemy.orm import Session
from app.db.models import User, ContentLog, UserProgress
from app.services.ai_services import get_llm_client, get_checker_service
from app.schemas.writing import WritingFeedbackRequest, WritingFeedbackResponse


async def get_writing_feedback(
    request: WritingFeedbackRequest,
    db: Session
) -> WritingFeedbackResponse:
    """
    Get feedback on user's writing.

    Args:
        request: Writing feedback request
        db: Database session

    Returns:
        WritingFeedbackResponse with corrections, comments, and score
    """
    llm = get_llm_client()
    checker = get_checker_service()

    # Find or create user
    user = db.query(User).filter(User.external_id == request.user_id).first()
    if not user:
        user = User(
            external_id=request.user_id,
            target_language=request.target_language,
            level=request.level
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    level_info = f" The student's level is {request.level}." if request.level else ""
    prompt = f"""You are a language tutor. The student wrote the following in {request.target_language}:{level_info}

"{request.text}"

Provide detailed feedback. Respond ONLY with valid JSON in this exact format:
{{
  "corrected_text": "The corrected version of the text",
  "overall_comment": "Overall comment about grammar, vocabulary, and style",
  "inline_explanation": "Explanation of main mistakes and corrections",
  "score": 75
}}

The score should be between 0 and 100 based on grammar, vocabulary, and overall quality."""

    # Generate feedback
    response = await llm.generate(
        system_prompt=f"You are a language tutor providing feedback. Always respond with valid JSON only.",
        user_prompt=prompt,
        temperature=0.3,
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

    feedback_data = json.loads(cleaned.strip())

    # Check content
    checker_result = await checker.check_content(
        module="writing",
        original_instruction="Generate writing feedback",
        user_input=request.dict(),
        generated_content=json.dumps(feedback_data)
    )

    # If not valid and has suggested fix, try to use it
    if not checker_result["is_valid"] and checker_result["suggested_fix"]:
        try:
            feedback_data = json.loads(checker_result["suggested_fix"])
        except:
            pass

    # Update user progress with score
    score = feedback_data.get("score", 0)
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == user.id,
        UserProgress.module == "writing"
    ).first()

    if not progress:
        progress = UserProgress(
            user_id=user.id,
            module="writing",
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
        module="writing",
        input_payload=request.dict(),
        generated_content=feedback_data,
        checker_result=checker_result,
        is_validated=checker_result["is_valid"]
    )
    db.add(content_log)
    db.commit()

    return WritingFeedbackResponse(**feedback_data)
