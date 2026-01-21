# Backend Feature Testing Guide

## 🎯 Quick Start

### Option 1: Interactive Swagger UI (Recommended)
Open in your browser:
```
http://localhost:8000/api/v1/docs
```
- Click any endpoint
- Click "Try it out"
- Fill in the parameters
- Click "Execute"

### Option 2: Use curl commands (see below)

---

## ✅ Features Working NOW (No API Key Needed)

### 1. Health Check
```bash
curl http://localhost:8000/api/v1/health
```

### 2. Create User
```bash
curl -X POST "http://localhost:8000/api/v1/users" \
  -H "Content-Type: application/json" \
  -d '{
    "external_id": "my-user-456",
    "target_language": "French",
    "level": "A2"
  }'
```

### 3. Get User Info
```bash
curl "http://localhost:8000/api/v1/users/my-user-456"
```

### 4. Get User Progress
```bash
curl "http://localhost:8000/api/v1/users/my-user-456/progress"
```

---

## ⚠️ Features Requiring Gemini API Key

These endpoints are implemented but need a real API key in `.env`:

### 5. Start Conversation
```bash
curl -X POST "http://localhost:8000/api/v1/conversation/start" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "my-user-456",
    "target_language": "French",
    "level": "A2",
    "topic": "travel"
  }'
```

### 6. Send Message
```bash
# Replace {SESSION_ID} with actual session ID from step 5
curl -X POST "http://localhost:8000/api/v1/conversation/{SESSION_ID}/message" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "my-user-456",
    "message": "Bonjour! Comment allez-vous?"
  }'
```

### 7. Get Vocabulary Flashcard
```bash
curl "http://localhost:8000/api/v1/vocabulary/next?user_id=my-user-456&target_language=French&level=A2"
```

### 8. Submit Vocabulary Answer
```bash
curl -X POST "http://localhost:8000/api/v1/vocabulary/answer" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "my-user-456",
    "word": "maison",
    "selected_option_index": 1,
    "correct_option_index": 1
  }'
```

### 9. Get Grammar Question
```bash
curl "http://localhost:8000/api/v1/grammar/question?user_id=my-user-456&target_language=French&level=A2&topic=present_tense"
```

### 10. Submit Grammar Answer
```bash
curl -X POST "http://localhost:8000/api/v1/grammar/answer" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "my-user-456",
    "question_id": "q-123",
    "selected_option_index": 2,
    "correct_option_index": 2
  }'
```

### 11. Get Writing Feedback
```bash
curl -X POST "http://localhost:8000/api/v1/writing/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "my-user-456",
    "target_language": "French",
    "level": "A2",
    "text": "Je suis aller au magasin hier."
  }'
```

### 12. Evaluate Pronunciation (Audio Upload)
```bash
# This endpoint requires an audio file
curl -X POST "http://localhost:8000/api/v1/phonetics/evaluate" \
  -F "user_id=my-user-456" \
  -F "target_language=French" \
  -F "target_phrase=Bonjour tout le monde" \
  -F "audio_file=@/path/to/audio.wav"
```

---

## 🔑 To Enable AI Features

1. Get a Gemini API key from: https://makersuite.google.com/app/apikey

2. Update `.env` file:
```bash
LLM_API_KEY=your-real-gemini-api-key-here
STT_API_KEY=your-google-cloud-stt-key-here  # For phonetics
```

3. Restart the server:
```bash
pkill -f uvicorn
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📊 Test Results

✅ Working:
- Health check
- User management (create, get, progress)
- Database operations
- All API endpoints are accessible

⚠️ Needs API Key:
- Conversation (AI chat tutor)
- Vocabulary (word generation)
- Grammar (question generation)
- Writing (feedback generation)
- Phonetics (speech-to-text evaluation)

---

## 🐛 Troubleshooting

### "Address already in use"
```bash
pkill -f uvicorn
# Or:
lsof -ti:8000 | xargs kill -9
```

### "Module not found"
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Database errors
Delete and recreate:
```bash
rm test_language_app.db
# Restart server to recreate tables
```

