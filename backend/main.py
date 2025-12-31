from app.main import app

# This file exists for easy import and running
# Run with: uvicorn main:app --reload

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
