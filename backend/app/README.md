# Backend API & Code Structure Guide (FastAPI)

This document describes:
1) what each API endpoint does (now + what it should evolve into),
2) request/response shapes,
3) error handling + auth expectations,
4) what each Python file/module is responsible for.

---

## High-level goals

- **Android app calls backend only** (no direct calls to Gemini / DB from client).
- Backend provides **module endpoints** for:
  - phonetics (audio → STT → scoring/feedback)
  - vocabulary (flashcards, quizzes)
  - conversation (chat tutoring with context)
  - writing (corrections + feedback)
  - grammar (questions + explanations)
- All AI-generated content goes through a **generate → verify** (“checker”) pipeline before returning to client.
- Persist user progress + logs in DB (PostgreSQL later).

---

## Base URL / Versioning

- Base prefix: `/api`
- Recommended versioning style: `/api/v1/...` (you can add later)
- Current scaffold uses `/api/...` directly.

---

## Endpoint List (MVP)

### 1) Greeting / Health

#### `GET /api/greeting`
**Purpose:** sanity check that backend is running + reachable.

**Response (200)**
```json
{ "message": "Hello from the backend!" }
````

**Notes**

* Keep this extremely simple; do not require auth.

---

### 2) Vocabulary

#### `GET /api/vocabulary`

**Purpose:** module health / discovery endpoint.

**Response (200)**

```json
{ "status": "ok", "hint": "POST /api/vocabulary/generate" }
```

#### `POST /api/vocabulary/generate`

**Purpose:** generate a flashcard (or later: a quiz item) for a language + level + topic.

**Request body**

```json
{
  "language": "French",
  "level": "beginner",
  "topic": "greetings"
}
```

**Response (200)**

```json
{
  "language": "French",
  "level": "beginner",
  "topic": "greetings",
  "flashcard": {
    "word": "bonjour",
    "meaning": "hello",
    "example": "Bonjour ! Comment ça va ?"
  }
}
```

**What it should evolve into**

* Call `services/ai_services.generate_then_check()` with a “flashcard prompt”.
* Checker validates:

    * definition correctness
    * example sentence naturalness + level-appropriateness
    * no unsafe/offensive content
* Optional: dictionary cross-check (later).
* Add personalization:

    * exclude words the user already mastered
    * adjust difficulty based on DB progress
* Record to DB:

    * content served, topic, result correctness (if quiz), response time.

**Common errors**

* `400 Bad Request` invalid input (empty topic, level out of range)
* `429 Too Many Requests` (later: rate limiting)
* `500` / `502` AI provider error (with graceful fallback content)

---

### 3) Conversation (Chat Tutor)

#### `POST /api/conversation`

**Purpose:** chat with AI tutor, maintain short context window.

**Request body**

```json
{
  "language": "Spanish",
  "user_message": "Hola, ¿cómo estás?",
  "context": []
}
```

**Response (200)**

```json
{
  "reply": "(mock tutor in Spanish) You said: Hola, ¿cómo estás?",
  "context": [
    "Hola, ¿cómo estás?",
    "(mock tutor in Spanish) You said: Hola, ¿cómo estás?"
  ]
}
```

**What it should evolve into**

* Use a “tutor system prompt” per language + level.
* Maintain context server-side (recommended) instead of client passing it forever:

    * client sends `conversation_id`
    * backend stores messages (DB) and returns next response
* Checker validates:

    * stays on-topic as language tutor
    * safe content
    * language correctness (as much as feasible)
* Optionally return “teaching metadata”:

    * corrected version
    * vocabulary highlights
    * brief explanation

**Common errors**

* `401` if endpoint becomes protected (optional)
* `400` missing user_message
* `500` AI error → fallback (“Please try again”)

---

### 4) Grammar

#### `GET /api/grammar/next-question`

**Purpose:** provide a grammar question + options + correct answer + explanation.

**Response (200)**

```json
{
  "topic": "present tense",
  "question": "Choose the correct form of \"to be\" for: I ___ a student.",
  "options": ["am", "is", "are", "be"],
  "answer_index": 0,
  "explanation": "With \"I\" we use \"am\" in the present tense."
}
```

**What it should evolve into**

* Support query parameters:

    * `language`, `level`, `topic`
* Generate with AI, then checker verifies:

    * exactly one correct option
    * explanation matches answer
* Add `POST /api/grammar/submit` to record answer correctness + update progress.

---

### 5) Writing

#### `POST /api/writing`

**Purpose:** accept user writing and return corrections + feedback.

**Request body**

```json
{
  "language": "German",
  "text": "Ich bin Student und ich gehen zur Uni."
}
```

**Response (200)**

```json
{
  "corrected_text": "Ich bin Student und ich gehe zur Uni.",
  "feedback": [
    "Verb agreement: 'ich gehe' not 'ich gehen'.",
    "Good sentence structure overall."
  ]
}
```

**What it should evolve into**

* Provide structured feedback types:

    * grammar issues (with location ranges)
    * style suggestions
    * vocabulary upgrades
* Checker validates:

    * correction is truly correct
    * feedback aligns with correction
* Optional: integrate grammar API as extra check (later).

---

### 6) Phonetics (Pronunciation)

#### `POST /api/phonetics`

**Purpose (MVP):** evaluate pronunciation attempt against target phrase.

**Request body (MVP placeholder)**

```json
{
  "language": "English",
  "target_phrase": "through the door"
}
```

**Response (200)**

```json
{
  "transcript": "through the door",
  "score": 0.95,
  "feedback": ["Nice pronunciation. Keep steady rhythm."]
}
```

**What it should evolve into**

* Switch to file upload:

    * `multipart/form-data` with `audio` as `UploadFile`
    * include `language`, `target_phrase`, optionally `phoneme_focus`
* Backend does:

    1. STT transcription + confidence
    2. compare transcript vs target
    3. scoring rules (edit distance + confidence)
    4. optional AI feedback prompt (“explain likely pronunciation issues”)
* Checker ensures feedback is consistent with actual mismatch.

**Common errors**

* `415 Unsupported Media Type` (if wrong upload)
* `400` missing audio/target phrase

---

### 7) Authentication

#### `POST /api/auth/register`

**Purpose:** create account (MVP uses in-memory store; later DB).

**Request**

```json
{ "email": "test@example.com", "password": "secret" }
```

**Response (200)**

```json
{ "status": "ok" }
```

#### `POST /api/auth/login`

**Purpose:** authenticate and return token.

**Request**

```json
{ "email": "test@example.com", "password": "secret" }
```

**Response (200)**

```json
{ "access_token": "....", "token_type": "bearer" }
```

**What it should evolve into**

* Use proper password hashing (bcrypt/passlib)
* JWT signing/verification with expiry
* Protect endpoints requiring user identity:

    * progress
    * saved wordlists
    * conversation history
* Add:

    * `GET /api/me` to return user profile
    * refresh token flow (optional)

---

## Suggested “next endpoints” (after MVP)

### Progress & analytics

* `GET /api/progress` (summary)
* `POST /api/progress/vocabulary` (submit quiz result)
* `POST /api/progress/grammar` (submit answer)
* `GET /api/history/conversation/{conversation_id}`

### Admin / diagnostics

* `GET /api/health` (db + ai provider status)
* `GET /api/metrics` (latency counters; later)

---

# Code Structure: What each Python file does

Below is the recommended structure used by the scaffold.

## `main.py`

**Role:** application wiring only.

* creates `FastAPI()`
* adds middleware (CORS)
* includes the main router (the “router of routers”)
* no business logic here

## `app/api/v1/api.py`

**Role:** router-of-routers.

* imports each endpoint router and includes them
* central place to enable/disable modules or add prefixes

## `app/api/deps.py`

**Role:** FastAPI dependencies.

* `get_current_user()` (later JWT verification)
* `get_db()` (later DB session)
* reusable dependencies for rate limiting / logging context

## `app/api/v1/endpoints/*.py`

**Role:** HTTP layer / controller layer.

* defines API routes with `APIRouter`
* validates input via schemas
* calls service functions
* returns response models

Files:

* `greeting.py` – health route
* `vocabulary.py` – flashcards/quiz routes
* `conversation.py` – chat route(s)
* `grammar.py` – question route(s)
* `writing.py` – writing feedback route(s)
* `phonetics.py` – pronunciation route(s)
* `auth.py` – register/login routes

**Rule:** endpoints should NOT contain Gemini logic directly; they call `services`.

## `app/schemas/*.py`

**Role:** Pydantic models (API contracts).

* request/response types for each module
* ensures stable JSON shapes for Android Retrofit/Ktor

## `app/services/*.py`

**Role:** business logic layer.

* constructs prompts
* calls AI + checker
* applies rules/fallbacks
* orchestrates DB reads/writes

Files:

* `ai_services.py` – the one place that knows how to call Gemini + run checker
* `vocabulary.py` – flashcard logic, personalization, saving results
* `conversation.py` – chat logic, context handling, moderation hooks
* `grammar.py` – question generation + validation
* `writing.py` – correction + structured feedback
* `phonetics.py` – STT integration + scoring rules

## `app/core/config.py`

**Role:** settings (.env environment config)

* reads `GEMINI_API_KEY`, `DATABASE_URL`, etc.
* provides a `settings` object for the app

## `app/core/security.py`

**Role:** auth utilities

* password hashing helpers
* JWT creation/verification
* token expiry rules

## `app/db/database.py`

**Role:** DB session/engine wiring (later)

* SQLAlchemy engine + SessionLocal
* dependency function `get_db()` (yield session)

## `app/db/models.py`

**Role:** SQLAlchemy ORM models (later)

* User
* Progress tables (vocab mastery, grammar scores)
* Interaction logs (requests, responses, latency)

## `tests/`

**Role:** automated tests (later)

* endpoint tests using FastAPI TestClient
* unit tests for services (prompt building, checker behavior)
* integration tests (DB + AI stub)

---

# Conventions & expectations

## Error handling (recommended)

* Use consistent JSON error shape:

```json
{ "detail": "Reason here" }
```

* Map AI failures to:

    * `502 Bad Gateway` (provider down)
    * `500` (unexpected)
* Include request IDs for logs (later)

## Auth strategy (recommended)

* Keep module endpoints public during early dev
* Protect progress/history endpoints first
* Use `Authorization: Bearer <token>` for protected routes

## AI “generate then check” pattern (recommended)

* `generate_content(prompt)` → candidate output
* `check_content(output)` → pass/fail + notes
* If fail: regenerate up to N times, else fallback

---

# Quick manual test checklist

* `GET /api/greeting` returns hello JSON
* `POST /api/vocabulary/generate` returns flashcard JSON
* `POST /api/conversation` returns reply + context
* `GET /api/grammar/next-question` returns MCQ + explanation
* `POST /api/writing` returns corrected text + feedback
* `POST /api/phonetics` returns transcript + score + feedback
* `POST /api/auth/register` then `POST /api/auth/login` returns token

Open Swagger UI at:

* `/docs`

---

# Implementation order (recommended)

1. Mock endpoints + schemas (fast UI integration)
2. Wire Android → backend (Retrofit/Ktor)
3. Implement Gemini + checker for ONE module (Vocabulary)
4. Add DB (users + progress + logs)
5. Add JWT auth + protect progress routes
6. Expand remaining modules with AI + checker
7. Tests + Docker + deployment

```

If you want, I can tailor this doc to **your exact JSON contract** for Android (e.g., “flashcard always includes `id`, `choices`, `correct_index`”) and add a “Request/Response examples” section per module that matches what your UI screens will need.
```
