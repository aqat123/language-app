# Language Learning Backend API

A comprehensive FastAPI-based backend for an AI-powered language learning application. This backend provides REST APIs for five learning modules: **Conversation**, **Vocabulary**, **Grammar**, **Writing**, and **Phonetics** (Pronunciation).

## 🌟 Features

### Learning Modules

1. **📱 Conversation Module**
   - Start AI-powered conversation sessions
   - Real-time conversation practice in target language
   - Automatic corrections and learning tips
   - Context-aware responses with chat history

2. **📚 Vocabulary Module**
   - AI-generated flashcards with definitions and examples
   - Multiple-choice vocabulary quizzes
   - Progress tracking and scoring
   - Adaptive difficulty levels

3. **✍️ Grammar Module**
   - Dynamic grammar question generation
   - Multiple-choice format with detailed explanations
   - Topic-specific questions (tenses, articles, etc.)
   - Level-based content

4. **✏️ Writing Module**
   - Detailed feedback on written text
   - Grammar and style corrections
   - Scoring (0-100)
   - Inline explanations of mistakes

5. **🎤 Phonetics (Pronunciation) Module**
   - Speech-to-text transcription
   - Pronunciation scoring and feedback
   - Word-level pronunciation analysis
   - Target phrase comparison

### Core Features

- ✅ **Generate-then-Verify Pattern**: All AI content validated before delivery
- 📊 **Progress Tracking**: Comprehensive tracking across all modules
- 📝 **Content Logging**: All AI interactions logged for improvement
- 🔄 **Flexible LLM Integration**: Supports Gemini and other LLMs
- 🔒 **Type Safety**: Full Pydantic validation
- 💾 **Database Persistence**: PostgreSQL for reliable storage

## 🏗️ Architecture

### System Overview

```
┌──────────────┐
│  Client App  │
│  (Android)   │
└──────┬───────┘
       │ REST API
       ▼
┌──────────────────────────────────┐
│   FastAPI Backend (Port 8000)   │
│                                  │
│  ┌────────────────────────────┐ │
│  │    API Endpoints (v1)      │ │
│  ├────────────────────────────┤ │
│  │   Service Layer            │ │
│  │ - Conversation             │ │
│  │ - Vocabulary               │ │
│  │ - Grammar                  │ │
│  │ - Writing                  │ │
│  │ - Phonetics                │ │
│  ├────────────────────────────┤ │
│  │   AI Services              │ │
│  │ - LLM Client (Gemini)      │ │
│  │ - Checker Service          │ │
│  │ - STT Client (Google)      │ │
│  └────────────────────────────┘ │
└────┬──────────────────────┬────┘
     │                      │
     ▼                      ▼
┌─────────┐          ┌──────────┐
│Gemini   │          │ Google   │
│LLM API  │          │ STT API  │
└─────────┘          └──────────┘
     │
     ▼
┌─────────────┐
│ PostgreSQL  │
│  Database   │
└─────────────┘
```

### Generate-then-Verify Pattern

All AI-generated content goes through validation:

```
Request → LLM Generate → Checker Validate → Is Valid? ─┬─ YES → Return
                                                        └─ NO  → Retry/Fix
```

## 📦 Tech Stack

- **Framework**: FastAPI 0.124.0
- **ORM**: SQLAlchemy 2.0.35
- **Database**: PostgreSQL
- **HTTP Client**: httpx 0.27.0
- **Validation**: Pydantic 2.12.5
- **Server**: Uvicorn 0.38.0
- **AI Services**:
  - Google Gemini API (LLM)
  - Google Speech-to-Text API

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI app initialization
│   ├── core/
│   │   ├── config.py           # Settings & configuration
│   │   └── security.py
│   ├── db/
│   │   ├── database.py         # DB connection & session
│   │   └── models.py           # SQLAlchemy models
│   ├── api/
│   │   └── v1/
│   │       ├── api.py          # Router aggregator
│   │       └── endpoints/
│   │           ├── greeting.py # Health check
│   │           ├── auth.py     # User management
│   │           ├── conversation.py
│   │           ├── vocabulary.py
│   │           ├── grammar.py
│   │           ├── writing.py
│   │           └── phonetics.py
│   ├── schemas/                # Pydantic models
│   │   ├── common.py
│   │   ├── conversation.py
│   │   ├── vocabulary.py
│   │   ├── grammar.py
│   │   ├── writing.py
│   │   └── phonetics.py
│   └── services/               # Business logic
│       ├── ai_services.py      # LLM & checker
│       ├── stt_client.py       # Speech-to-text
│       ├── conversation.py
│       ├── vocabulary.py
│       ├── grammar.py
│       ├── writing.py
│       └── phonetics.py
├── main.py                     # Entry point
├── requirements.txt
├── .env.example
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 12+
- Google Gemini API key
- Google Cloud Speech-to-Text API key

### Installation

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up database**
   ```bash
   # Create PostgreSQL database
   createdb language_app
   ```

5. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

6. **Run the application**
   ```bash
   uvicorn main:app --reload
   ```

Visit http://localhost:8000/api/v1/docs for interactive API documentation!

## ⚙️ Configuration

Create a `.env` file in the backend directory:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/language_app

# Google Gemini API
LLM_API_KEY=your_gemini_api_key_here
LLM_API_BASE_URL=https://generativelanguage.googleapis.com/v1beta
LLM_MODEL=gemini-1.5-flash

# Google Speech-to-Text API
STT_API_KEY=your_google_cloud_api_key_here
STT_API_BASE_URL=https://speech.googleapis.com/v1

# Application
ENV=dev
DEBUG=True
API_V1_PREFIX=/api/v1
PROJECT_NAME=Language Learning Backend
BACKEND_CORS_ORIGINS=*
```

### Getting API Keys

**Gemini API Key:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy to `.env` file

**Google Speech-to-Text:**
1. Create project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Speech-to-Text API
3. Create API credentials
4. Copy to `.env` file

## 📚 API Documentation

### Base URL
- Development: `http://localhost:8000/api/v1`
- Swagger Docs: `http://localhost:8000/api/v1/docs`

### Endpoints

#### Health & Users
- `GET /health` - Health check
- `POST /users` - Create user
- `GET /users/{external_id}` - Get user
- `GET /users/{external_id}/progress` - Get progress

#### Conversation
- `POST /conversation/start` - Start session
- `POST /conversation/{session_id}/message` - Send message

#### Vocabulary
- `GET /vocabulary/next` - Get flashcard
- `POST /vocabulary/answer` - Submit answer

#### Grammar
- `GET /grammar/question` - Get question
- `POST /grammar/answer` - Submit answer

#### Writing
- `POST /writing/feedback` - Get feedback

#### Phonetics
- `POST /phonetics/evaluate` - Evaluate pronunciation

### Example Requests

**Start Conversation:**
```bash
curl -X POST "http://localhost:8000/api/v1/conversation/start" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "target_language": "Spanish",
    "level": "A2",
    "topic": "ordering food"
  }'
```

**Get Flashcard:**
```bash
curl "http://localhost:8000/api/v1/vocabulary/next?user_id=user123&target_language=French&level=B1"
```

**Get Writing Feedback:**
```bash
curl -X POST "http://localhost:8000/api/v1/writing/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "target_language": "German",
    "text": "Ich bin gehe zur Schule.",
    "level": "A1"
  }'
```

## 💾 Database Schema

### User
- `id` (UUID) - Primary key
- `external_id` (String) - External user ID
- `target_language` (String) - Learning language
- `level` (String) - Proficiency (A1-C2)

### UserProgress
- `user_id` → User
- `module` (String) - Module name
- `score` (Float) - Current score
- `total_attempts` (Integer)
- `correct_attempts` (Integer)

### ConversationSession
- `user_id` → User
- `context_json` (JSON) - Chat history
- `target_language` (String)
- `is_active` (Boolean)

### ContentLog
- `user_id` → User
- `module` (String)
- `input_payload` (JSON)
- `generated_content` (JSON)
- `checker_result` (JSON)
- `is_validated` (Boolean)

## 🧪 Testing

Access interactive API documentation:
```
http://localhost:8000/api/v1/docs
```

Test endpoints directly in the browser with Swagger UI!

## 🐳 Docker Deployment

```bash
# Build
docker build -t language-backend .

# Run
docker run -p 8000:8000 --env-file .env language-backend
```

## 📊 How It Works

### Conversation Flow
1. User starts session with language/level/topic
2. LLM generates opening message
3. Checker validates content
4. Session stored in database
5. User sends messages
6. LLM generates replies + corrections
7. Progress tracked automatically

### Content Generation Flow
1. User requests content (flashcard/question/feedback)
2. Service builds prompt for LLM
3. LLM generates structured JSON response
4. Checker validates content quality
5. If invalid, retry or use suggested fix
6. Log content and update progress
7. Return validated content to user

## 🔒 Security

- **API Keys**: Never commit to version control
- **CORS**: Configure for production
- **Input Validation**: Pydantic schemas
- **SQL Injection**: Protected by ORM
- **Rate Limiting**: Recommended for production

## 🛠️ Development

```bash
# Activate virtual environment
source venv/bin/activate

# Run with auto-reload
uvicorn main:app --reload

# Add new dependency
pip install package-name
pip freeze > requirements.txt
```

## 📈 Performance

- Async/await throughout
- PostgreSQL connection pooling
- LLM response caching (recommended)
- Rate limiting (recommended)

## 🐛 Troubleshooting

**Port in use:**
```bash
lsof -i :8000
kill -9 <PID>
```

**Import errors:**
```bash
source venv/bin/activate
which python  # Should point to venv
```

**Database connection:**
```bash
# Test connection
psql -U user -d language_app
```

## 📝 License

[Your License Here]

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## 📞 Support

- Issues: GitHub Issues
- Documentation: `/api/v1/docs`

---

Built with ❤️ using FastAPI and Google Gemini AI
