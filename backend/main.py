from fastapi import FastAPI

app = FastAPI()

@app.get("/api/greeting")
def read_greeting():
    return {"message": "Hello from the backend!"}
