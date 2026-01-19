from fastapi import FastAPI
from agentFunctions import get_reply  # Import the async service function

app = FastAPI()

@app.get("/api/greeting")
def read_greeting():
    return {"message": "Hello from the backend!"}

@app.get("/api/add")
def add(a: int, b: int):
    return {"a": a, "b": b, "sum": a + b}


@app.post("/api/conversation")  # Use POST for sending data like messages
async def conversation_endpoint(language: str, user_msg: str, context: str):
    # 1. Prepare history (Waiter formats the ticket)
    history_list = context.split(",") if context else []

    # 2. Pass to Head Chef (Service Layer)
    ai_reply = await get_reply(language, user_msg, history_list)

    # 3. Return dish to customer
    new_history = history_list + [user_msg, ai_reply]
    return {"reply": ai_reply, "context": new_history}

