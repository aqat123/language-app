# Backend Implementation Guide

**Navigation:**
- [../README.md](../README.md) - Project overview
- [../SETUP.md](../SETUP.md) - Installation & configuration
- [../API.md](../API.md) - API reference
- [../TESTING.md](../TESTING.md) - Testing guide
- [../ARCHITECTURE.md](../ARCHITECTURE.md) - System architecture & design
- [./check.md](./check.md) - Comprehensive backend testing

This guide covers **backend implementation details** for developers modifying FastAPI endpoints, services, and database models.

## Backend Structure

REST APIs with FastAPI for five learning modules:
- **Conversation**: Chat tutoring with AI
- **Vocabulary**: Flashcard system
- **Grammar**: Exercise generation
- **Writing**: Text feedback
- **Phonetics**: Pronunciation evaluation

## Directory Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── core/                # Configuration
│   ├── db/                  # Database (SQLAlchemy)
│   ├── api/v1/              # REST endpoints (/api/v1/*)
│   ├── schemas/             # Pydantic models (request/response)
│   └── services/            # Business logic (LLM, validation, etc.)
├── requirements.txt
├── main.py                  # Application entry point
├── .env.example
└── README.md               # This file
```

**For complete directory tree, see [../README.md#project-structure](../README.md#project-structure)**

## Quick Start

See [../SETUP.md](../SETUP.md) for installation and configuration.

**Run the backend:**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

Access Swagger UI: `http://localhost:8000/api/v1/docs`

## Database Schema

**See [../ARCHITECTURE.md#database-schema](../ARCHITECTURE.md#database-schema) for complete schema details.**

### Quick Reference

**users** - User accounts
- `id`, `external_id` (unique), `target_language`, `level`, `created_at`

**user_progress** - Module performance tracking
- `id`, `user_id`, `module`, `score`, `total_attempts`, `correct_attempts`, `last_updated`

**conversation_sessions** - Chat history
- `id`, `user_id`, `topic`, `target_language`, `level`, `conversation_history` (JSON), `is_active`, `created_at`

**content_logs** - AI generation audit trail
- `id`, `user_id`, `module`, `input_payload`, `generated_content`, `checker_result`, `is_validated`, `created_at`

See [app/db/models.py](app/db/models.py) for SQLAlchemy ORM definitions.

## Testing

- [../TESTING.md](../TESTING.md) - Testing overview & quick start
- [./check.md](./check.md) - Comprehensive backend test examples

Interactive testing: `http://localhost:8000/api/v1/docs`

## Backend Implementation Patterns

**Core Pattern:** Generate-then-Verify
1. LLM generates content (flashcard, question, feedback)
2. Checker validates accuracy and quality
3. Return if valid; retry/fallback if not

See [../ARCHITECTURE.md#generate-then-verify-pattern](../ARCHITECTURE.md#generate-then-verify-pattern) for detailed flow.

## Development

**Backend setup:** See [../SETUP.md](../SETUP.md)

```bash
# Activate environment
source venv/bin/activate

# Run with auto-reload
uvicorn main:app --reload

# Add dependency
pip install package-name
pip freeze > requirements.txt
```

## Code Organization

- **endpoints/** - HTTP layer (route handlers)
- **schemas/** - Pydantic models (request/response validation)
- **services/** - Business logic (LLM calls, validation, DB operations)
- **db/** - Database layer (SQLAlchemy models, sessions)
- **core/** - Configuration and security utilities

See [app/README.md](app/README.md) for detailed code structure.
