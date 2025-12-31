import json
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from uuid import uuid4
from app.db.models import User, ConversationSession, ContentLog, UserProgress
from app.services.ai_services import get_llm_client, get_checker_service
from app.schemas.conversation import (
    ConversationStartRequest,
    ConversationStartResponse,
    ConversationMessageRequest,
    ConversationMessageResponse
)


async def start_conversation(
    request: ConversationStartRequest,
    db: Session
) -> ConversationStartResponse:
    """
    Start a new conversation session.

    Args:
        request: Conversation start request
        db: Database session

    Returns:
        ConversationStartResponse with session_id and opening_message
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

    # Create system prompt
    topic_info = f" about {request.topic}" if request.topic else ""
    level_info = f" at {request.level} level" if request.level else ""
    system_prompt = f"""You are a friendly language tutor helping a student practice {request.target_language}{level_info}.
Start a natural conversation{topic_info}. Be encouraging and supportive.
Keep your opening message short (1-2 sentences) and in {request.target_language}."""

    user_prompt = "Generate a friendly opening message to start the conversation."

    # Generate opening message
    opening_message = await llm.generate(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.7,
        max_tokens=256
    )

    # Check content (optional for opening message, but good practice)
    checker_result = await checker.check_content(
        module="conversation",
        original_instruction="Generate opening message",
        user_input=request.dict(),
        generated_content=opening_message
    )

    # If not valid, use suggested fix or regenerate once
    if not checker_result["is_valid"] and checker_result["suggested_fix"]:
        opening_message = checker_result["suggested_fix"]

    # Create conversation session
    session = ConversationSession(
        user_id=user.id,
        target_language=request.target_language,
        context_json={
            "system_prompt": system_prompt,
            "messages": [
                {"role": "assistant", "content": opening_message}
            ],
            "topic": request.topic,
            "level": request.level
        },
        is_active=True
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # Log content
    content_log = ContentLog(
        user_id=user.id,
        module="conversation",
        input_payload=request.dict(),
        generated_content={"opening_message": opening_message},
        checker_result=checker_result,
        is_validated=checker_result["is_valid"]
    )
    db.add(content_log)
    db.commit()

    return ConversationStartResponse(
        session_id=str(session.id),
        opening_message=opening_message
    )


async def send_message(
    session_id: str,
    request: ConversationMessageRequest,
    db: Session
) -> ConversationMessageResponse:
    """
    Send a message in a conversation session.

    Args:
        session_id: Conversation session ID
        request: Message request
        db: Database session

    Returns:
        ConversationMessageResponse with reply and optional corrections/tips
    """
    llm = get_llm_client()
    checker = get_checker_service()

    # Load conversation session
    session = db.query(ConversationSession).filter(
        ConversationSession.id == session_id
    ).first()

    if not session:
        raise ValueError(f"Conversation session {session_id} not found")

    # Verify user
    user = db.query(User).filter(User.external_id == request.user_id).first()
    if not user or str(session.user_id) != str(user.id):
        raise ValueError("Invalid user for this session")

    # Get context
    context = session.context_json
    system_prompt = context.get("system_prompt", "")
    messages = context.get("messages", [])

    # Add user message to context
    messages.append({"role": "user", "content": request.message})

    # Build conversation history for LLM
    conversation_text = "\n".join([
        f"{msg['role'].upper()}: {msg['content']}" for msg in messages
    ])

    user_prompt = f"""{conversation_text}

Now respond as the assistant. Continue the conversation naturally in {session.target_language}.
Keep your response conversational and at an appropriate level for the learner."""

    # Generate reply
    reply = await llm.generate(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.7,
        max_tokens=512
    )

    # Check reply
    checker_result = await checker.check_content(
        module="conversation",
        original_instruction="Generate conversation reply",
        user_input=request.dict(),
        generated_content=reply
    )

    # If not valid, use suggested fix or retry once
    if not checker_result["is_valid"] and checker_result["suggested_fix"]:
        reply = checker_result["suggested_fix"]

    # Generate corrections and tips for user message
    correction_prompt = f"""The student wrote: "{request.message}"

Provide:
1. A corrected version if there are grammatical errors (or null if perfect)
2. Brief helpful tips (1-2 sentences) for improvement

Respond in JSON format:
{{
  "corrected_message": "corrected version or null",
  "tips": "helpful tips or null"
}}"""

    correction_response = await llm.generate(
        system_prompt=f"You are a language tutor providing feedback on {session.target_language} writing.",
        user_prompt=correction_prompt,
        temperature=0.3,
        max_tokens=256
    )

    # Parse corrections
    corrected_user_message = None
    tips = None
    try:
        cleaned = correction_response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        correction_data = json.loads(cleaned.strip())
        corrected_user_message = correction_data.get("corrected_message")
        tips = correction_data.get("tips")
    except:
        pass  # If parsing fails, just skip corrections

    # Update context with new messages
    messages.append({"role": "assistant", "content": reply})
    context["messages"] = messages
    session.context_json = context
    db.commit()

    # Update user progress
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == user.id,
        UserProgress.module == "conversation"
    ).first()

    if not progress:
        progress = UserProgress(
            user_id=user.id,
            module="conversation",
            total_attempts=1
        )
        db.add(progress)
    else:
        progress.total_attempts += 1

    db.commit()

    # Log content
    content_log = ContentLog(
        user_id=user.id,
        module="conversation",
        input_payload=request.dict(),
        generated_content={
            "reply": reply,
            "corrected_user_message": corrected_user_message,
            "tips": tips
        },
        checker_result=checker_result,
        is_validated=checker_result["is_valid"]
    )
    db.add(content_log)
    db.commit()

    return ConversationMessageResponse(
        reply=reply,
        corrected_user_message=corrected_user_message,
        tips=tips,
        session_id=session_id
    )
