# REST API Reference

Complete reference documentation for all REST API endpoints in the Language Learning Application.

## API Overview

### Base URL

- **Development:** `http://localhost:8000/api/v1`
- **Production:** (To be determined based on deployment configuration)

### API Versioning

The API uses URL-based versioning with the `/api/v1` prefix. This allows for backward-compatible upgrades by introducing `/api/v2` in the future without breaking existing clients.

### Response Format

All API responses use JSON format with standardized structure.

### Content Type

All requests and responses use `Content-Type: application/json`

## Authentication and Headers

### Required Headers

```
Content-Type: application/json
```

### Optional Headers

```
Accept: application/json
Accept-Language: en-US
```

### CORS Configuration

Cross-Origin Resource Sharing (CORS) is enabled to allow frontend applications to make requests from different domains.

**Allowed Origins:** All origins (configured as `*` in development)

## Response Format Standard

### Success Response Structure

All successful responses follow this structure:

```json
{
  "data": {},
  "status": 200,
  "message": "Success"
}
```

For single-resource responses, data is returned directly:

```json
{
  "id": "uuid-123",
  "external_id": "user123",
  "target_language": "Spanish",
  "level": "A1"
}
```

### Error Response Structure

All error responses include status code and error details:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET, PUT, DELETE requests |
| 201 | Created | Successful POST requests creating new resources |
| 400 | Bad Request | Invalid parameters or request body |
| 404 | Not Found | Resource does not exist |
| 422 | Unprocessable Entity | Request validation failed |
| 500 | Internal Server Error | Server error (see error message for details) |

## Endpoint Reference

### Group 1: Health and System Endpoints

#### GET /api/v1/health

Health check endpoint to verify API is running and responsive.

**Description:** Simple health check that returns API status

**Method:** GET

**Parameters:** None

**Request Body:** None

**Response (200 OK):**

```json
{
  "status": "ok"
}
```

**Example curl:**

```bash
curl http://localhost:8000/api/v1/health
```

**Notes:** No authentication required. Use this endpoint to verify API connectivity.

---

### Group 2: User Management Endpoints

#### POST /api/v1/users

Create a new user account.

**Description:** Create a new user with specified language and proficiency level

**Method:** POST

**Parameters:** None

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| external_id | string | Yes | Unique user identifier (username, email, etc.) |
| target_language | string | Yes | Language being learned (Spanish, French, German, etc.) |
| level | string | No | Proficiency level (A1, A2, B1, B2, C1, C2) |

**Request Example:**

```json
{
  "external_id": "user123",
  "target_language": "Spanish",
  "level": "A1"
}
```

**Response (201 Created):**

```json
{
  "id": "abc-123-def-456",
  "external_id": "user123",
  "target_language": "Spanish",
  "level": "A1",
  "created_at": "2026-01-21T10:30:00Z"
}
```

**Error Response (400 Bad Request):**

```json
{
  "detail": "User already exists"
}
```

**Example curl:**

```bash
curl -X POST "http://localhost:8000/api/v1/users" \
  -H "Content-Type: application/json" \
  -d '{
    "external_id": "maria",
    "target_language": "Spanish",
    "level": "A1"
  }'
```

**Notes:**
- `external_id` must be unique
- If user already exists, returns 400 error
- `level` is optional; defaults to A1 if not specified

---

#### GET /api/v1/users/{external_id}

Retrieve user information by external ID.

**Description:** Get user profile and current settings

**Method:** GET

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| external_id | string | Yes | User's external identifier |

**Query Parameters:** None

**Request Body:** None

**Response (200 OK):**

```json
{
  "id": "abc-123-def-456",
  "external_id": "maria",
  "target_language": "Spanish",
  "level": "A1",
  "created_at": "2026-01-21T10:30:00Z"
}
```

**Error Response (404 Not Found):**

```json
{
  "detail": "User not found"
}
```

**Example curl:**

```bash
curl "http://localhost:8000/api/v1/users/maria"
```

**Notes:** Returns complete user profile with all settings.

---

#### GET /api/v1/users/{external_id}/progress

Retrieve user's progress across all modules.

**Description:** Get performance metrics and progress for each learning module

**Method:** GET

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| external_id | string | Yes | User's external identifier |

**Query Parameters:** None

**Request Body:** None

**Response (200 OK):**

```json
[
  {
    "module": "vocabulary",
    "score": 85.5,
    "total_attempts": 20,
    "correct_attempts": 17,
    "last_updated": "2026-01-21T15:45:00Z"
  },
  {
    "module": "conversation",
    "score": 78.0,
    "total_attempts": 10,
    "correct_attempts": 8,
    "last_updated": "2026-01-21T14:20:00Z"
  }
]
```

**Error Response (404 Not Found):**

```json
{
  "detail": "User not found"
}
```

**Example curl:**

```bash
curl "http://localhost:8000/api/v1/users/maria/progress"
```

**Notes:**
- Returns array of progress objects for each module
- May be empty array if user has not attempted any modules yet
- Score is calculated as (correct_attempts / total_attempts) * 100

---

### Group 3: Conversation Module Endpoints

#### POST /api/v1/conversation/start

Start a new conversation session.

**Description:** Initialize a conversation session with AI tutor on specified topic

**Method:** POST

**Parameters:** None

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| user_id | string | Yes | User's external ID |
| target_language | string | Yes | Language for conversation |
| level | string | No | Proficiency level (A1-C2) |
| topic | string | No | Conversation topic (ordering, travel, etc.) |

**Request Example:**

```json
{
  "user_id": "maria",
  "target_language": "Spanish",
  "level": "A1",
  "topic": "ordering_food"
}
```

**Response (200 OK):**

```json
{
  "session_id": "sess-789-xyz-123",
  "opening_message": "Hola! Bienvenido al restaurante. Que deseas ordenar?",
  "topic": "ordering_food",
  "language": "Spanish"
}
```

**Error Response (500 Server Error - if API key missing):**

```json
{
  "detail": "LLM_API_KEY not configured"
}
```

**Example curl:**

```bash
curl -X POST "http://localhost:8000/api/v1/conversation/start" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "maria",
    "target_language": "Spanish",
    "level": "A1",
    "topic": "ordering_food"
  }'
```

**Notes:**
- Requires Gemini API key configured in .env
- Session maintains conversation history
- Response time typically 2-3 seconds (LLM inference)
- Topic is optional; random topic selected if not specified

---

#### POST /api/v1/conversation/{session_id}/message

Send a message in an active conversation session.

**Description:** Send message to AI tutor and receive contextual response

**Method:** POST

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| session_id | string | Yes | Session ID from /start endpoint |

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| user_id | string | Yes | User's external ID |
| message | string | Yes | User's message in target language |

**Request Example:**

```json
{
  "user_id": "maria",
  "message": "Yo quiero una pizza con pepperoni"
}
```

**Response (200 OK):**

```json
{
  "reply": "Buena eleccion! Que tipo de bebida prefieres?",
  "corrected_user_message": null,
  "tips": "Your grammar is correct!",
  "session_id": "sess-789-xyz-123"
}
```

**Response (200 OK - With Correction):**

```json
{
  "reply": "Excelente! Eso es una buena opcion.",
  "corrected_user_message": "You said: 'Yo quiero una pizza con pepperoni'. This is correct!",
  "tips": "Remember: 'quiero' is the correct conjugation for first person.",
  "session_id": "sess-789-xyz-123"
}
```

**Error Response (404 Not Found):**

```json
{
  "detail": "Session not found"
}
```

**Example curl:**

```bash
curl -X POST "http://localhost:8000/api/v1/conversation/sess-789-xyz-123/message" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "maria",
    "message": "Yo quiero una pizza con pepperoni"
  }'
```

**Notes:**
- Requires valid session_id from /start endpoint
- Response time 2-3 seconds
- `corrected_user_message` only present if grammar errors detected
- Maintains conversation history for context
- May include `tips` field with learning guidance

---

### Group 4: Vocabulary Module Endpoints

#### GET /api/v1/vocabulary/next

Get next vocabulary flashcard.

**Description:** Generate or retrieve next vocabulary flashcard for user

**Method:** GET

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | User's external ID |
| target_language | string | Yes | Language being learned |
| level | string | No | Proficiency level (A1-C2) |

**Request Body:** None

**Response (200 OK):**

```json
{
  "word": "biblioteca",
  "definition": "library",
  "example_sentence": "Voy a la biblioteca para estudiar",
  "options": ["library", "bookstore", "museum", "school"],
  "correct_option_index": 0
}
```

**Example curl:**

```bash
curl "http://localhost:8000/api/v1/vocabulary/next?user_id=maria&target_language=Spanish&level=A1"
```

**Notes:**
- Response time 2-3 seconds (LLM generation + validation)
- Each call generates new random flashcard
- `options` are English definitions
- Difficulty appropriate to specified level

---

#### POST /api/v1/vocabulary/answer

Submit vocabulary answer and get feedback.

**Description:** Evaluate vocabulary answer and update progress

**Method:** POST

**Parameters:** None

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| user_id | string | Yes | User's external ID |
| word | string | Yes | The vocabulary word |
| selected_option_index | number | Yes | Index of selected answer (0-3) |
| correct_option_index | number | Yes | Index of correct answer (0-3) |

**Request Example:**

```json
{
  "user_id": "maria",
  "word": "biblioteca",
  "selected_option_index": 0,
  "correct_option_index": 0
}
```

**Response (200 OK - Correct):**

```json
{
  "is_correct": true,
  "correct_option_index": 0,
  "explanation": "Correct! 'Biblioteca' means library in Spanish."
}
```

**Response (200 OK - Incorrect):**

```json
{
  "is_correct": false,
  "correct_option_index": 0,
  "explanation": "Incorrect. The correct answer is 'library'. 'Bookstore' is 'libreria'."
}
```

**Example curl:**

```bash
curl -X POST "http://localhost:8000/api/v1/vocabulary/answer" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "maria",
    "word": "biblioteca",
    "selected_option_index": 0,
    "correct_option_index": 0
  }'
```

**Notes:**
- Updates user_progress table with attempt
- Calculates cumulative score
- Returns immediate feedback

---

### Group 5: Grammar Module Endpoints

#### GET /api/v1/grammar/question

Get a grammar exercise question.

**Description:** Generate grammar exercise question appropriate to user's level

**Method:** GET

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | User's external ID |
| target_language | string | Yes | Language being learned |
| level | string | No | Proficiency level (A1-C2) |
| topic | string | No | Grammar topic (present_tense, past_tense, etc.) |

**Request Body:** None

**Response (200 OK):**

```json
{
  "question_id": "q-123-abc",
  "instruction": "Choose the correct form of the verb in the present tense",
  "sentence": "Yo _________ al parque cada dia.",
  "options": ["voy", "va", "vas", "vamos"],
  "correct_option_index": 0,
  "explanation_template": "The present tense of 'ir' for first person (yo) is 'voy'"
}
```

**Example curl:**

```bash
curl "http://localhost:8000/api/v1/grammar/question?user_id=maria&target_language=Spanish&level=A1&topic=present_tense"
```

**Notes:**
- Response time 2-3 seconds
- Topic optional; random topic if not specified
- Explanation template not shown initially (reveal on wrong answer)

---

#### POST /api/v1/grammar/answer

Submit grammar answer and receive feedback.

**Description:** Evaluate grammar exercise and provide explanation if incorrect

**Method:** POST

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| user_id | string | Yes | User's external ID |
| question_id | string | Yes | Question ID from /question endpoint |
| selected_option_index | number | Yes | Index of selected answer (0-3) |
| correct_option_index | number | Yes | Index of correct answer (0-3) |

**Request Example:**

```json
{
  "user_id": "maria",
  "question_id": "q-123-abc",
  "selected_option_index": 0,
  "correct_option_index": 0
}
```

**Response (200 OK - Correct):**

```json
{
  "is_correct": true,
  "explanation": "Correct! 'Voy' is the correct present tense form of 'ir' for first person (yo)."
}
```

**Response (200 OK - Incorrect):**

```json
{
  "is_correct": false,
  "correct_option_index": 0,
  "explanation": "Incorrect. The correct answer is 'voy'. Remember: The present tense of 'ir' for first person (yo) is 'voy'."
}
```

**Example curl:**

```bash
curl -X POST "http://localhost:8000/api/v1/grammar/answer" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "maria",
    "question_id": "q-123-abc",
    "selected_option_index": 0,
    "correct_option_index": 0
  }'
```

---

### Group 6: Writing Module Endpoints

#### POST /api/v1/writing/feedback

Get feedback on written text.

**Description:** Analyze student writing for grammar, vocabulary, and style errors

**Method:** POST

**Parameters:** None

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| user_id | string | Yes | User's external ID |
| target_language | string | Yes | Language text is written in |
| level | string | No | Student's proficiency level |
| text | string | Yes | Student's written text to analyze |

**Request Example:**

```json
{
  "user_id": "maria",
  "target_language": "Spanish",
  "level": "A1",
  "text": "Yo voy al parque ayer con mis amigos"
}
```

**Response (200 OK):**

```json
{
  "original_text": "Yo voy al parque ayer con mis amigos",
  "corrected_text": "Fui al parque ayer con mis amigos",
  "errors": [
    {
      "type": "tense",
      "original": "voy",
      "correction": "fui",
      "explanation": "Use past tense (fui) when describing an action that already happened (ayer = yesterday)"
    }
  ],
  "strengths": "Good use of prepositions (al, con)",
  "suggestions": "Try to use the past tense consistently when describing past events"
}
```

**Example curl:**

```bash
curl -X POST "http://localhost:8000/api/v1/writing/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "maria",
    "target_language": "Spanish",
    "level": "A1",
    "text": "Yo voy al parque ayer con mis amigos"
  }'
```

**Notes:**
- Response time 2-3 seconds
- May identify multiple errors
- Includes positive feedback on strengths
- Provides suggestions for improvement
- Response time may be longer for longer texts

---

### Group 7: Phonetics Module Endpoints

#### POST /api/v1/phonetics/evaluate

Evaluate pronunciation attempt.

**Description:** Analyze student audio recording and provide pronunciation feedback

**Method:** POST

**Content-Type:** multipart/form-data

**Form Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | User's external ID |
| target_language | string | Yes | Language being spoken |
| target_phrase | string | Yes | Phrase student should pronounce |
| audio_file | binary | Yes | Audio file (WAV, MP3, etc.) |

**Request Example:**

Using curl with audio file:

```bash
curl -X POST "http://localhost:8000/api/v1/phonetics/evaluate" \
  -F "user_id=maria" \
  -F "target_language=Spanish" \
  -F "target_phrase=Hola, como estoy?" \
  -F "audio_file=@/path/to/recording.wav"
```

**Response (200 OK):**

```json
{
  "target_phrase": "Hola, como estoy?",
  "transcription": "Hola como estoy",
  "confidence": 0.92,
  "is_correct": true,
  "score": 85,
  "feedback": "Good pronunciation! Minor issue: 'como' should have slight stress on first syllable. Overall clear and understandable.",
  "detailed_feedback": {
    "strengths": [
      "Clear vowel pronunciation",
      "Good rhythm and pacing"
    ],
    "improvements": [
      "Stress slightly misplaced on 'como'"
    ]
  }
}
```

**Response (200 OK - Incorrect Pronunciation):**

```json
{
  "target_phrase": "Buenos dias",
  "transcription": "Buenas deas",
  "confidence": 0.75,
  "is_correct": false,
  "score": 45,
  "feedback": "The 'dias' pronunciation needs work. The 'i' should be clearer. Practice the 'ee-ah' sound.",
  "detailed_feedback": {
    "strengths": [
      "Good 'Buenos' pronunciation"
    ],
    "improvements": [
      "Pronunciation of 'dias' unclear",
      "Vowel clarity needs improvement"
    ]
  }
}
```

**Error Response (400 Bad Request - No Audio):**

```json
{
  "detail": "Audio file is required"
}
```

**Notes:**
- Requires speech-to-text API key configured
- Response time 3-4 seconds (transcription + analysis)
- Confidence score indicates transcription certainty (0-1)
- Score (0-100) indicates pronunciation quality
- `is_correct` based on transcription match with target phrase
- Designed for native-like pronunciation evaluation

---

## Common Error Responses

### 400 Bad Request

Occurs when request validation fails:

```json
{
  "detail": "Invalid request format or missing required fields"
}
```

Common causes:
- Missing required query parameters
- Invalid JSON in request body
- Invalid data types

### 404 Not Found

Occurs when resource does not exist:

```json
{
  "detail": "Resource not found"
}
```

Common causes:
- User does not exist
- Session ID invalid or expired
- Question ID not found

### 422 Unprocessable Entity

Occurs when request data fails validation:

```json
{
  "detail": [
    {
      "loc": ["body", "level"],
      "msg": "value is not a valid enumeration member",
      "type": "type_error.enum"
    }
  ]
}
```

### 500 Internal Server Error

Occurs when server encounters an error:

```json
{
  "detail": "Internal server error"
}
```

Common causes:
- API key not configured
- Database connection error
- AI service unavailable
- Unexpected exception in code

---

## Rate Limiting

Current implementation does not have rate limiting. For production deployment, consider:

- Rate limits per user (e.g., 100 requests/minute)
- Rate limits per endpoint (e.g., /api/v1/vocabulary/next: 30 requests/minute)
- Rate limits per API key

---

## API Usage Examples

### Complete Vocabulary Learning Session

```bash
# 1. Create user
USER_ID="maria"
curl -X POST "http://localhost:8000/api/v1/users" \
  -H "Content-Type: application/json" \
  -d '{
    "external_id": "'$USER_ID'",
    "target_language": "Spanish",
    "level": "A1"
  }'

# 2. Get flashcard
FLASHCARD=$(curl -s "http://localhost:8000/api/v1/vocabulary/next?user_id=$USER_ID&target_language=Spanish&level=A1")
echo $FLASHCARD

# 3. Submit answer
curl -X POST "http://localhost:8000/api/v1/vocabulary/answer" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "'$USER_ID'",
    "word": "biblioteca",
    "selected_option_index": 0,
    "correct_option_index": 0
  }'

# 4. Check progress
curl "http://localhost:8000/api/v1/users/$USER_ID/progress"
```

### Complete Conversation Session

```bash
USER_ID="maria"

# 1. Start conversation
SESSION=$(curl -s -X POST "http://localhost:8000/api/v1/conversation/start" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "'$USER_ID'",
    "target_language": "Spanish",
    "level": "A1",
    "topic": "ordering_food"
  }')

SESSION_ID=$(echo $SESSION | grep -o '"session_id":"[^"]*"' | cut -d'"' -f4)
echo "Session: $SESSION_ID"

# 2. Send message
curl -s -X POST "http://localhost:8000/api/v1/conversation/$SESSION_ID/message" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "'$USER_ID'",
    "message": "Hola, yo quiero una pizza"
  }'
```

---

## API Documentation Tools

### Swagger UI

Interactive API documentation available at:

```
http://localhost:8000/api/v1/docs
```

Features:
- Click any endpoint to see full documentation
- Click "Try it out" to test endpoints
- Auto-populated request examples
- Response schema visualization

### ReDoc

Alternative documentation interface available at:

```
http://localhost:8000/api/v1/redoc
```

---

For additional information on system design and architecture, see [ARCHITECTURE.md](ARCHITECTURE.md).

For testing procedures, see [TESTING.md](TESTING.md).
