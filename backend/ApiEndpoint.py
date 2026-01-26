from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
# Import your service functions
import agentFunctions
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Pydantic Models (Data Shapes) ---
class ChatRequest(BaseModel):
    language: str
    user_msg: str
    context: List[str] = []  # Context is passed from Client -> Server -> Client


class VocabRequest(BaseModel):
    language: str


class VocabCheckRequest(BaseModel):
    target_word: str
    user_guess: str
    language: str


# Endpoints
@app.post("/api/conversation")
async def conversation_endpoint(request: ChatRequest):
    """
    1. Receives User Message + History
    2. Calls AI to get reply
    3. Returns AI Reply + Updated History
    """
    ai_reply = await agentFunctions.get_chat_reply(
        request.language,
        request.user_msg,
        request.context
    )

    # Update history with the new turn
    new_context = request.context + [f"User: {request.user_msg}", f"Tutor: {ai_reply}"]

    return {"reply": ai_reply, "context": new_context}


@app.post("/api/vocabulary/generate")
async def generate_vocab_endpoint(request: VocabRequest):
    """
    Generates a new word for the user to guess/visualize.
    """
    word = await agentFunctions.get_vocab_word(request.language)
    
    #gets the image
    image_url = await agentFunctions.get_vocab_image(word, request.language)
    return {
        "vocabulary_word": word,
        "image_url": image_url
            }


@app.post("/api/vocabulary/check")
async def check_vocab_endpoint(request: VocabCheckRequest):
    """
    Uses the 2nd AI (Checker) to verify the user's guess.
    """
    result = await agentFunctions.check_vocab_guess(
        request.language,
        request.target_word,
        request.user_guess
    )
    return result