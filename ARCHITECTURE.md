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

#### `users` Table

Stores user account information and learning context.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID (String) | Primary key, unique identifier |
| external_id | String (unique) | User's public ID (can be username, email, etc.) |
| target_language | String | Language being learned (Spanish, French, etc.) |
| level | String | Proficiency level (A1, A2, B1, B2, C1, C2) |
| created_at | Timestamp | Account creation timestamp |

#### `user_progress` Table

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

#### `conversation_sessions` Table

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

#### `content_logs` Table

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

Complete walkthrough of a user requesting and answering a vocabulary flashcard.

### Step 1: User Clicks "Vocabulary" Button

**Browser (index.html):**
```html
<div class="module-card" onclick="startVocabulary()">
    <div class="module-icon">📚</div>
    <h3>Vocabulary</h3>
    <p>Learn new words with flashcards</p>
</div>
```

### Step 2: JavaScript Function Runs

**File: `simple-web-interface/app.js`**
```javascript
async function startVocabulary() {
    // 1. Switch to vocabulary screen
    showSection('vocabulary-section');
    
    // 2. Show loading message
    document.getElementById('flashcard').innerHTML = 
        '<div class="loading">Loading flashcard...</div>';
    
    // 3. Make API call to backend
    const response = await fetch(
        `http://localhost:8000/api/v1/vocabulary/next?user_id=maria&target_language=Spanish&level=A1`
    );
    
    // 4. Get the JSON response
    currentFlashcard = await response.json();
    
    // 5. Display it on screen
    displayFlashcard();
}
```

### Step 3: HTTP Request Goes to Backend

**Request Details:**
```http
GET http://localhost:8000/api/v1/vocabulary/next?user_id=maria&target_language=Spanish&level=A1
```

**Query Parameters:**
- `user_id`: "maria"
- `target_language`: "Spanish"
- `level`: "A1"

### Step 4: Backend Receives Request

**File: `backend/app/api/v1/endpoints/vocabulary.py`**
```python
@router.get("/next", response_model=FlashcardResponse)
async def get_flashcard(
    user_id: str = Query(...),
    target_language: str = Query(...),
    level: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get next vocabulary flashcard."""
    try:
        # Calls the service layer
        return await get_next_flashcard(user_id, target_language, level, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**What happens:**
- FastAPI validates the parameters
- Creates a database session
- Calls the service function

### Step 5: Service Layer Generates Content

**File: `backend/app/services/vocabulary.py`**
```python
async def get_next_flashcard(
    user_id: str,
    target_language: str,
    level: Optional[str],
    db: Session
) -> FlashcardResponse:
    # 1. Get AI client
    llm = get_llm_client()
    checker = get_checker_service()
    
    # 2. Find or create user in database
    user = db.query(User).filter(User.external_id == user_id).first()
    if not user:
        user = User(
            external_id=user_id,
            target_language=target_language,
            level=level
        )
        db.add(user)
        db.commit()
    
    # 3. Create AI prompt
    level_info = f" at {level} level" if level else ""
    prompt = f"""Generate a vocabulary flashcard for learning {target_language}{level_info}.

Respond ONLY with valid JSON in this exact format:
{{
  "word": "word in {target_language}",
  "definition": "definition in English",
  "example_sentence": "example sentence using the word in {target_language}",
  "options": ["option1", "option2", "option3", "option4"],
  "correct_option_index": 0
}}

The options should be 4 English definitions (one correct, three plausible distractors)."""
    
    # 4. Call Gemini AI
    response = await llm.generate(
        system_prompt="You are a language learning content creator. Always respond with valid JSON only.",
        user_prompt=prompt,
        temperature=0.7,
        max_tokens=512
    )
    
    # 5. Parse JSON response
    cleaned = response.strip()
    # Remove markdown code blocks if present
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    
    flashcard_data = json.loads(cleaned.strip())
    
    # 6. Validate with checker AI
    checker_result = await checker.check_content(
        module="vocabulary",
        original_instruction="Generate vocabulary flashcard",
        user_input={"target_language": target_language, "level": level},
        generated_content=json.dumps(flashcard_data)
    )
    
    # 7. Save to database
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
    
    # 8. Return flashcard
    return FlashcardResponse(**flashcard_data)
```

**Result Example:**
```json
{
  "word": "Gato",
  "definition": "Cat",
  "example_sentence": "El gato es muy bonito.",
  "options": ["Cat", "Dog", "Bird", "Fish"],
  "correct_option_index": 0
}
```

### Step 6: Gemini AI Processes Request

**What happens at Google Cloud:**

```
Backend sends HTTP POST to:
https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent

Payload:
{
  "contents": [{
    "parts": [{"text": "Generate a vocabulary flashcard..."}]
  }],
  "generationConfig": {
    "temperature": 0.7,
    "maxOutputTokens": 512
  }
}

Gemini AI:
- Processes the prompt
- Generates appropriate Spanish word for A1 level
- Creates 4 multiple choice options
- Returns JSON response
```

### Step 7: Response Travels Back to Web App

**HTTP Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "word": "Gato",
  "definition": "Cat",
  "example_sentence": "El gato es muy bonito.",
  "options": ["Cat", "Dog", "Bird", "Fish"],
  "correct_option_index": 0
}
```

### Step 8: JavaScript Displays the Flashcard

**File: `simple-web-interface/app.js`**
```javascript
function displayFlashcard() {
    // Build HTML for the word and example
    const flashcardHtml = `
        <div class="word">${currentFlashcard.word}</div>
        <div class="example">"${currentFlashcard.example_sentence}"</div>
        <div class="definition-label">What does this mean?</div>
    `;
    document.getElementById('flashcard').innerHTML = flashcardHtml;

    // Build HTML for the 4 options
    const optionsHtml = currentFlashcard.options.map((option, index) => `
        <div class="option" onclick="selectOption(${index})">
            ${option}
        </div>
    `).join('');
    
    document.getElementById('options-container').innerHTML = optionsHtml;
    document.getElementById('options-container').classList.remove('hidden');
}
```

### Step 9: User Sees Flashcard on Screen

```
┌──────────────────────────────────┐
│   📚 Vocabulary Practice         │
├──────────────────────────────────┤
│                                  │
│            Gato                  │
│   "El gato es muy bonito."       │
│                                  │
│   What does this mean?           │
│                                  │
│   ┌──────┐  ┌──────┐            │
│   │ Cat  │  │ Dog  │            │
│   └──────┘  └──────┘            │
│   ┌──────┐  ┌──────┐            │
│   │ Bird │  │ Fish │            │
│   └──────┘  └──────┘            │
│                                  │
│   [Back to Modules]              │
└──────────────────────────────────┘
```

### Step 10: User Clicks "Cat" (Correct Answer)

**File: `simple-web-interface/app.js`**
```javascript
async function selectOption(selectedIndex) {
    const options = document.querySelectorAll('.option');
    const correctIndex = currentFlashcard.correct_option_index;

    // Disable all options
    options.forEach(opt => opt.style.pointerEvents = 'none');

    // Mark selected and correct answers
    options[selectedIndex].classList.add('selected');
    options[correctIndex].classList.add('correct');  // Turns green

    if (selectedIndex !== correctIndex) {
        options[selectedIndex].classList.add('incorrect');  // Would turn red
    }

    // Submit answer to backend
    const response = await fetch(`${API_BASE_URL}/vocabulary/answer`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            user_id: currentUser.id,
            word: currentFlashcard.word,
            selected_option_index: selectedIndex,
            correct_option_index: correctIndex
        })
    });

    const result = await response.json();

    // Show feedback
    const feedbackDiv = document.getElementById('feedback');
    const isCorrect = result.is_correct;
    feedbackDiv.className = 'feedback ' + (isCorrect ? 'correct' : 'incorrect');
    feedbackDiv.innerHTML = `
        <div class="feedback-text">${isCorrect ? '✅ Correct!' : '❌ Incorrect'}</div>
        <div class="feedback-explanation">${result.explanation}</div>
        <button onclick="startVocabulary()" class="btn btn-primary" style="margin-top: 15px;">Next Word</button>
    `;
    feedbackDiv.classList.remove('hidden');
}
```

### Step 11: Backend Updates Progress

**File: `backend/app/services/vocabulary.py`**
```python
async def submit_vocabulary_answer(
    request: VocabularyAnswerRequest,
    db: Session
) -> VocabularyAnswerResponse:
    # 1. Find user
    user = db.query(User).filter(User.external_id == request.user_id).first()
    if not user:
        raise ValueError("User not found")

    # 2. Check if answer is correct
    is_correct = request.selected_option_index == request.correct_option_index

    # 3. Find or create progress record
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == user.id,
        UserProgress.module == "vocabulary"
    ).first()

    if not progress:
        # Create new progress record
        progress = UserProgress(
            user_id=user.id,
            module="vocabulary",
            total_attempts=1,
            correct_attempts=1 if is_correct else 0
        )
        db.add(progress)
    else:
        # Update existing progress
        progress.total_attempts += 1
        if is_correct:
            progress.correct_attempts += 1

    # 4. Calculate score percentage
    if progress.total_attempts > 0:
        progress.score = (progress.correct_attempts / progress.total_attempts) * 100

    db.commit()

    # 5. Return feedback
    explanation = "Correct!" if is_correct else f"The correct answer was option {request.correct_option_index}."

    return VocabularyAnswerResponse(
        is_correct=is_correct,
        correct_option_index=request.correct_option_index,
        explanation=explanation
    )
```

### Step 12: Web Shows Feedback

```
┌──────────────────────────────────┐
│   📚 Vocabulary Practice         │
├──────────────────────────────────┤
│                                  │
│            Gato                  │
│   "El gato es muy bonito."       │
│                                  │
│   What does this mean?           │
│                                  │
│   ┌──────┐  ┌──────┐            │
│   │ Cat ✓│  │ Dog  │            │
│   └──────┘  └──────┘            │
│   ┌──────┐  ┌──────┐            │
│   │ Bird │  │ Fish │            │
│   └──────┘  └──────┘            │
│                                  │
│  ┌────────────────────────────┐ │
│  │  ✅ Correct!               │ │
│  │  Great job!                │ │
│  │  [Next Word]               │ │
│  └────────────────────────────┘ │
└──────────────────────────────────┘
```

### Database Storage After Interaction

**`users` Table:**

| id | external_id | target_language | level | created_at |
|---|---|---|---|---|
| abc-123-def-456... | maria | Spanish | A1 | 2026-01-21... |

**`user_progress` Table:**

| id | user_id | module | score | total_attempts | correct_attempts |
|---|---|---|---|---|---|
| xyz-789... | abc-123... | vocabulary | 100.0 | 1 | 1 |

**`content_logs` Table:**

| id | user_id | module | generated_content | is_validated |
|---|---|---|---|---|
| qwe-456... | abc-123... | vocabulary | {"word":"Gato","definition":"Cat",...} | true |

---

## Request/Response Examples

### **Vocabulary Request**
```http
GET /api/v1/vocabulary/next?user_id=maria&target_language=Spanish&level=A1
```

### **Vocabulary Response**
```json
{
  "word": "Gato",
  "definition": "Cat",
  "example_sentence": "El gato es muy bonito.",
  "options": ["Cat", "Dog", "Bird", "Fish"],
  "correct_option_index": 0
}
```

### **Answer Submission**
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

### **Answer Response**
```json
{
  "is_correct": true,
  "correct_option_index": 0,
  "explanation": "Correct!"
}
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
