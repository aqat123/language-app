from fastapi import FastAPI

app = FastAPI()

@app.get("/api/greeting")
def read_greeting():
    return {"message": "Hello from the backend!"}

@app.get("/api/add")
def add(a: int, b: int):
    return {"a": a, "b": b, "sum": a + b}