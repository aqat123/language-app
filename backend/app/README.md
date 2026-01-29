# Backend Code Structure Guide (FastAPI)

**For API endpoint specifications, see [../../API.md](../../API.md)**  
**For system architecture patterns, see [../../ARCHITECTURE.md](../../ARCHITECTURE.md)**  
**For comprehensive testing guide, see [../../TESTING.md](../../TESTING.md)**

This document describes the **internal code organization** for developers implementing backend features.

---

## Architectural Goals

- Backend is the **only gateway** to Gemini API and database (Android client does not call Gemini/DB directly).
- All endpoints follow **five-layer architecture**:
  1. **HTTP Layer** (`endpoints/`) – validates input, calls services, returns responses
  2. **Schema Layer** (`schemas/`) – Pydantic models for request/response validation
  3. **Service Layer** (`services/`) – business logic, AI prompt construction, checker integration
  4. **Database Layer** (`db/`) – SQLAlchemy ORM, session management
  5. **Configuration Layer** (`core/`) – settings, security, authentication
- All AI-generated content uses **generate-then-verify pattern** (see [../../ARCHITECTURE.md](../../ARCHITECTURE.md)).

---

## Code Structure: What Each Module Does

### `main.py`

**Role:** application wiring only.

- Creates `FastAPI()` instance
- Adds middleware (CORS)
- Includes the main router
- No business logic here

### `app/api/v1/api.py`

**Role:** router-of-routers.

- Imports each endpoint router and includes them
- Central place to enable/disable modules or add prefixes

### `app/api/deps.py`

**Role:** FastAPI dependencies.

- `get_current_user()` (later JWT verification)
- `get_db()` (later DB session)
- Reusable dependencies for rate limiting / logging context

### `app/api/v1/endpoints/*.py`

**Role:** HTTP layer / controller layer.

**Files:**
- `greeting.py` – health check route
- `vocabulary.py` – flashcards/quiz routes
- `conversation.py` – chat route(s)
- `grammar.py` – question route(s)
- `writing.py` – writing feedback route(s)
- `phonetics.py` – pronunciation route(s)
- `auth.py` – register/login routes

**Pattern:** Endpoints validate input via schemas and call service functions. Never call Gemini logic directly; call `services/`.

### `app/schemas/*.py`

**Role:** Pydantic models (API contracts).

- Request/response types for each module
- Ensures stable JSON shapes for client apps

### `app/services/*.py`

**Role:** Business logic layer.

**Files:**
- `ai_services.py` – Gemini calls + checker integration
- `vocabulary.py` – flashcard logic, personalization, saving results
- `conversation.py` – chat logic, context handling, moderation hooks
- `grammar.py` – question generation + validation
- `writing.py` – correction + structured feedback
- `phonetics.py` – STT integration + scoring rules

**Pattern:** Constructs prompts, calls AI + checker, applies rules/fallbacks, orchestrates DB reads/writes.

### `app/core/config.py`

**Role:** Settings (.env environment config)

- Reads `GEMINI_API_KEY`, `DATABASE_URL`, etc.
- Provides a `settings` object for the app

### `app/core/security.py`

**Role:** Auth utilities

- Password hashing helpers
- JWT creation/verification
- Token expiry rules

### `app/db/database.py`

**Role:** DB session/engine wiring

- SQLAlchemy engine + SessionLocal
- Dependency function `get_db()` (yield session)

### `app/db/models.py`

**Role:** SQLAlchemy ORM models

- User model
- Progress tables (vocab mastery, grammar scores)
- Interaction logs (requests, responses, latency)

### `tests/`

**Role:** Automated tests

- Endpoint tests using FastAPI TestClient
- Unit tests for services (prompt building, checker behavior)
- Integration tests (DB + AI stub)

---

## Design Pattern: Generate-Then-Verify

All AI-generated content follows this pipeline:

1. **Generate:** Call Gemini with a carefully crafted prompt
2. **Verify:** Pass output through a checker (validation rules, AI review)
3. **Fallback:** If verification fails, retry generation or serve cached content

See [../../ARCHITECTURE.md](../../ARCHITECTURE.md) for implementation details.

---

## Error Handling Standards

Use consistent JSON error response:

```json
{ "detail": "Reason here" }
```

**HTTP Status Codes:**
- `400 Bad Request` – Invalid input (schema validation)
- `401 Unauthorized` – Missing/invalid auth token
- `500 Internal Server Error` – Unexpected error
- `502 Bad Gateway` – Gemini API provider error (graceful fallback)

---

## Development Workflow

1. **Design endpoint** in [../../API.md](../../API.md) with request/response schema
2. **Create Pydantic model** in `app/schemas/<module>.py`
3. **Implement service logic** in `app/services/<module>.py`
4. **Create endpoint handler** in `app/api/v1/endpoints/<module>.py`
5. **Write tests** in `tests/test_<module>.py`
6. **Test via Swagger** at `http://localhost:8000/api/v1/docs`

---

## Directory Structure

```
backend/
├── main.py                      # FastAPI app entrypoint
└── app/
    ├── api/                     # HTTP layer & routing
    │   ├── deps.py              # FastAPI dependencies
    │   └── v1/endpoints/        # HTTP route handlers
    ├── schemas/                 # Pydantic request/response models
    ├── services/                # Business logic layer
    ├── db/                      # Database layer (ORM, models, session)
    └── core/                    # Configuration (settings, security, auth)
```
