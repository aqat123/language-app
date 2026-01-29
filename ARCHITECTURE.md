# System Architecture and Design

Comprehensive documentation of the Language Learning Application architecture, design patterns, data flow, and component interactions.

## High-Level System Architecture

```
┌────────────────────────────────────────────────────────┐
│                   Client Layer                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Web Browser Interface (simple-web-interface/)   │  │
│  │  - index.html (UI structure)                     │  │
│  │  - app.js (business logic, API calls)            │  │
│  │  - styles.css (presentation)                     │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────┬───────────────────────────────────────┘
                 │ HTTP/REST (JSON)
                 │
┌────────────────▼──────────────────────────────────────┐
│              FastAPI Backend (Port 8000)              │
│  ┌──────────────────────────────────────────────────┐ │
│  │  API Layer (/app/api/v1/endpoints/)              │ │
│  │  - greeting.py (health check)                    │ │
│  │  - auth.py (user management)                     │ │
│  │  - conversation.py (chat sessions)               │ │
│  │  - vocabulary.py (flashcards)                    │ │
│  │  - grammar.py (exercises)                        │ │
│  │  - writing.py (composition feedback)             │ │
│  │  - phonetics.py (pronunciation)                  │ │
│  └──────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────┐ │
│  │  Service Layer (/app/services/)                  │ │
│  │  - ai_services.py (LLM & checker)                │ │
│  │  - conversation.py (business logic)              │ │
│  │  - vocabulary.py (business logic)                │ │
│  │  - grammar.py (business logic)                   │ │
│  │  - writing.py (business logic)                   │ │
│  │  - phonetics.py (business logic)                 │ │
│  │  - stt_client.py (speech-to-text)                │ │
│  └──────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────┐ │
│  │  Database Layer (/app/db/)                       │ │
│  │  - database.py (SQLAlchemy session)              │ │
│  │  - models.py (ORM schema)                        │ │
│  └──────────────────────────────────────────────────┘ │
└────────┬────────────────────────────────┬─────────────┘
         │                                │
         │ SQL Protocol                   │ HTTPS/REST
         │                                │
    ┌────▼───────┐            ┌────────────▼──────────┐
    │ PostgreSQL │           │  Google Cloud APIs    │
    │ Database   │           │  ├─ Gemini LLM        │
    │            │           │  ├─ Speech-to-Text    │
    │ - users    │           │  └─ Image API         │
    │ - progress │           └───────────────────────┘
    │ - sessions │
    │ - logs     │
    └────────────┘
```

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|----------|
| Backend | FastAPI | 0.124.0+ |
| Database | PostgreSQL | 12+ |
| ORM | SQLAlchemy | 2.0.35+ |
| Validation | Pydantic | 2.12.5+ |
| HTTP Client | httpx | 0.27.0 |
| Server | Uvicorn | 0.38.0 |
| LLM Service | Google Gemini API | Latest |
| Speech Service | Google Cloud Speech-to-Text | Latest |

## Client-Server Communication Flow

### Standard Request/Response Cycle

```
1. Client Action
   └─ User interacts with web interface (clicks button, enters text, etc.)

2. JavaScript Handling
   └─ Event handler triggers, data collected, validation occurs

3. HTTP Request
   ├─ Method: GET, POST, PUT, DELETE
   ├─ URL: http://localhost:8000/api/v1/{module}/{endpoint}
   ├─ Headers: Content-Type: application/json
   └─ Body: JSON serialized request data (if applicable)

4. FastAPI Routing
   ├─ Route matched to endpoint handler
   ├─ Path parameters and query parameters extracted
   ├─ Pydantic validation of input data
   └─ Request object passed to handler function

5. Service Layer Processing
   ├─ Business logic execution
   ├─ Database queries (if needed)
   ├─ AI service calls (if applicable)
   ├─ Data transformation and validation
   └─ Response object prepared

6. HTTP Response
   ├─ Status Code: 200, 201, 400, 404, 500, etc.
   ├─ Headers: Content-Type: application/json
   └─ Body: JSON serialized response data

7. JavaScript Processing
   ├─ Response received and parsed
   ├─ Status code checked for errors
   ├─ Data stored in application state
   └─ DOM updated to reflect new data

8. User Feedback
   └─ UI displays results, errors, or loading states
```

## Learning Modules

All five modules follow the same pattern: receive request → generate with Gemini → validate → save to logs → return response.

| Module | Purpose |
|--------|----------|
| Conversation | Real-world dialogue practice with AI tutor |
| Vocabulary | Flashcard system with adaptive difficulty |
| Grammar | Dynamic exercises with rule-based feedback |
| Writing | Composition analysis and feedback |
| Phonetics | Pronunciation evaluation via speech-to-text |

See [API.md](API.md) for detailed endpoint specifications.

## Generate-then-Verify Pattern

Two-step validation ensures content quality:

1. **Generate** - Gemini creates content (word, question, feedback, etc.)
2. **Validate** - Checker verifies accuracy, appropriateness, and quality
3. **Deliver** - Return if valid; retry if not

For vocabulary example: checker confirms word exists, definition is accurate, and options are plausible.

## Database Schema

### Tables

#### users Table

Stores user account information and learning context.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID (String) | Primary key, unique identifier |
| external_id | String (unique) | User's public ID (can be username, email, etc.) |
| target_language | String | Language being learned (Spanish, French, etc.) |
| level | String | Proficiency level (A1, A2, B1, B2, C1, C2) |
| created_at | Timestamp | Account creation timestamp |

#### user_progress Table

Tracks performance across all modules. One record per user per module.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID (String) | Primary key |
| user_id | UUID (FK) | Reference to users table |
| module | String | Module name (vocabulary, conversation, etc.) |
| score | Float | Percentage score (0-100) |
| total_attempts | Integer | Total exercises attempted in module |
| correct_attempts | Integer | Number of correct responses |
| last_updated | Timestamp | Last activity timestamp |

#### conversation_sessions Table

Maintains context for ongoing conversation sessions.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID (String) | Primary key, session identifier |
| user_id | UUID (FK) | Reference to users table |
| topic | String | Conversation topic (ordering, travel, etc.) |
| target_language | String | Language for this conversation |
| level | String | Proficiency level |
| conversation_history | JSON | Array of message objects with role and content |
| created_at | Timestamp | Session start time |
| last_updated | Timestamp | Last message timestamp |

#### content_logs Table

Permanent audit trail of all AI-generated content.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID (String) | Primary key |
| user_id | UUID (FK) | Reference to users table |
| module | String | Module that generated content |
| input_payload | JSON | User input and parameters |
| generated_content | JSON | Raw AI output (before validation) |
| checker_result | JSON | Validation results and metadata |
| is_validated | Boolean | Whether content passed validation |
| created_at | Timestamp | Creation timestamp |

## External Services

**Gemini LLM** - Generates educational content
- Used by all modules for words, questions, feedback, corrections

**Google Cloud Speech-to-Text** - Transcribes audio
- Used by Phonetics module and conversation voice input

**Checker Service** - Validates AI content
- Checks accuracy, completeness, appropriateness, quality, format

## Security and Data Handling

### API Key Management

**Best Practices:**

1. **Environment Variables** - Store all API keys in `.env` file
2. **Never Log Keys** - Never print or log sensitive credentials
3. **Access Control** - Restrict API key usage to minimum necessary scope
4. **Rotation** - Regenerate keys periodically
5. **Monitoring** - Track API usage and costs

**Implementation:**

```python
# Correct
api_key = os.getenv("LLM_API_KEY")
if not api_key:
    raise ValueError("LLM_API_KEY not configured")

# Incorrect
print(f"Using API key: {api_key}")  # Never do this
```

### Database Credential Handling

**Best Practices:**

1. **Connection Strings** - Store DATABASE_URL in environment variables
2. **Connection Pooling** - Use SQLAlchemy session pooling for efficiency
3. **Timeout Configuration** - Set connection timeouts to prevent hangs
4. **SSL/TLS** - Use encrypted connections in production

### User Data Privacy

**Data Collection:**

The application collects:

- **User Profile** - Name, target language, proficiency level
- **Usage Data** - Module usage, attempt history, scores
- **Content Interaction** - Generated content and student responses
- **Audio Data** (Phonetics only) - Speech recordings for analysis

**Data Protection:**

1. **Encryption** - Sensitive data encrypted in transit and at rest
2. **Retention** - Content logs retained for improvement purposes
3. **Access Control** - Only authorized users access their own data
4. **Compliance** - Design follows data protection principles

**User Rights:**

Users should be able to:

- View their own data and progress
- Request data deletion
- Understand what data is collected
- Know how data is used

## Request/Response Example: Vocabulary Module Execution

### Step 1: User Initiates Request

**Browser (index.html):**
```javascript
// User clicks "Vocabulary" button
async function startVocabulary() {
    document.getElementById('flashcard').innerHTML = '<div class="loading">Loading...</div>';
    
    const response = await fetch(
        `http://localhost:8000/api/v1/vocabulary/next?user_id=maria&target_language=Spanish&level=A1`
    );
    
    currentFlashcard = await response.json();
    displayFlashcard();
}
```

**HTTP Request:**
```http
GET /api/v1/vocabulary/next?user_id=maria&target_language=Spanish&level=A1
```

### Step 2: Backend Receives and Routes Request

**Backend (app/api/v1/endpoints/vocabulary.py):**
```python
@router.get("/next", response_model=FlashcardResponse)
async def get_flashcard(
    user_id: str = Query(...),
    target_language: str = Query(...),
    level: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    # Pydantic validates parameters
    # Database session created
    # Call service layer
    return await get_next_flashcard(user_id, target_language, level, db)
```

### Step 3: Service Layer Generates Content

**Backend (app/services/vocabulary.py):**
```python
async def get_next_flashcard(
    user_id: str,
    target_language: str,
    level: Optional[str],
    db: Session
) -> FlashcardResponse:
    # 1. Find or create user
    user = db.query(User).filter(User.external_id == user_id).first()
    if not user:
        user = User(external_id=user_id, target_language=target_language, level=level)
        db.add(user)
        db.commit()
    
    # 2. Create AI prompt
    prompt = f"""Generate a vocabulary flashcard for learning {target_language} at {level} level.
    
Respond ONLY with valid JSON:
{{
  "word": "word in {target_language}",
  "definition": "definition in English",
  "example_sentence": "example in {target_language}",
  "options": ["def1", "def2", "def3", "def4"],
  "correct_option_index": 0
}}"""
    
    # 3. Call Gemini LLM
    response = await llm.generate(prompt, temperature=0.7, max_tokens=512)
    flashcard_data = json.loads(response.strip())
    
    # 4. Validate with checker
    checker_result = await checker.check_content(
        module="vocabulary",
        generated_content=json.dumps(flashcard_data)
    )
    
    # 5. Save to audit log
    content_log = ContentLog(
        user_id=user.id,
        module="vocabulary",
        input_payload={"target_language": target_language, "level": level},
        generated_content=flashcard_data,
        checker_result=checker_result,
        is_validated=checker_result["is_valid"]
    )
    db.add(content_log)
    db.commit()
    
    return FlashcardResponse(**flashcard_data)
```

### Step 4: Gemini AI Generates Content

**Google Gemini API processes prompt (~1-2 seconds):**
```json
{
  "word": "Gato",
  "definition": "Cat",
  "example_sentence": "El gato es muy bonito.",
  "options": ["Cat", "Dog", "Bird", "Fish"],
  "correct_option_index": 0
}
```

### Step 5: Response Returned to Frontend

**HTTP Response:**
```json
{
  "word": "Gato",
  "definition": "Cat",
  "example_sentence": "El gato es muy bonito.",
  "options": ["Cat", "Dog", "Bird", "Fish"],
  "correct_option_index": 0
}
```

### Step 6: Frontend Displays Flashcard

**Browser (app.js):**
```javascript
function displayFlashcard() {
    const flashcardHtml = `
        <div class="word">${currentFlashcard.word}</div>
        <div class="example">"${currentFlashcard.example_sentence}"</div>
        <div class="definition-label">What does this mean?</div>
    `;
    document.getElementById('flashcard').innerHTML = flashcardHtml;
    
    const optionsHtml = currentFlashcard.options.map((option, index) => `
        <div class="option" onclick="selectOption(${index})">
            ${option}
        </div>
    `).join('');
    document.getElementById('options-container').innerHTML = optionsHtml;
}
```

### Step 7: User Submits Answer

**User clicks "Cat" (index 0):**
```javascript
async function selectOption(selectedIndex) {
    const response = await fetch(`${API_BASE_URL}/vocabulary/answer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            user_id: currentUser.id,
            word: currentFlashcard.word,
            selected_option_index: selectedIndex,
            correct_option_index: currentFlashcard.correct_option_index
        })
    });
    
    const result = await response.json();
    showFeedback(result.is_correct, result.explanation);
}
```

**HTTP Request:**
```http
POST /api/v1/vocabulary/answer
Content-Type: application/json

{
  "user_id": "maria",
  "word": "Gato",
  "selected_option_index": 0,
  "correct_option_index": 0
}
```

### Step 8: Backend Updates Progress

**Backend (app/services/vocabulary.py):**
```python
async def submit_vocabulary_answer(request: VocabularyAnswerRequest, db: Session):
    # 1. Find user
    user = db.query(User).filter(User.external_id == request.user_id).first()
    
    # 2. Check correctness
    is_correct = request.selected_option_index == request.correct_option_index
    
    # 3. Update or create progress record
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == user.id,
        UserProgress.module == "vocabulary"
    ).first()
    
    if progress:
        progress.total_attempts += 1
        if is_correct:
            progress.correct_attempts += 1
    else:
        progress = UserProgress(
            user_id=user.id,
            module="vocabulary",
            total_attempts=1,
            correct_attempts=1 if is_correct else 0
        )
        db.add(progress)
    
    # 4. Calculate score
    progress.score = (progress.correct_attempts / progress.total_attempts) * 100
    db.commit()
    
    return VocabularyAnswerResponse(
        is_correct=is_correct,
        explanation="Correct!" if is_correct else "The correct answer was Cat."
    )
```

### Step 9: Frontend Shows Feedback

**HTTP Response:**
```json
{
  "is_correct": true,
  "correct_option_index": 0,
  "explanation": "Correct! 'Gato' means 'Cat' in Spanish."
}
```

**Browser displays:**
```
✅ Correct!
Great job! You've answered 1 out of 1 correctly (100%).
[Next Word]
```

---

## Key Patterns

- **Async/Await** for non-blocking I/O
- **Pydantic validation** of all requests
- **Service layer** separates business logic from endpoints
- **Two-step validation** ensures content quality
- **Audit logging** in content_logs table
- **Error handling** converts exceptions to HTTP responses

---

## Quick Reference

**Most Important Files:**

- Backend API: `/backend/app/api/v1/endpoints/`
- Business Logic: `/backend/app/services/`
- Database Models: `/backend/app/db/models.py`
- Frontend: `/simple-web-interface/app.js`

For detailed implementation, see [API.md](API.md), [SETUP.md](SETUP.md), and [TESTING.md](TESTING.md).
