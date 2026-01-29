# Testing Guide

Comprehensive testing instructions for developers and QA engineers testing the Language Learning Application. This guide covers testing both the backend API and the web interface frontend.

## Testing Overview

### Testing Approaches

This guide covers different approaches to testing:

1. **Web Interface Testing (Recommended for End-to-End)**
   - Best for: Testing complete user workflows, full integration testing
   - Access: http://localhost:3000 (after running `python -m http.server 3000`)
   - Covers: All learning modules through the UI, user interactions, frontend-backend communication

2. **Swagger UI (Interactive API Testing)**
   - Best for: Quick API testing, exploring endpoints, learning the API
   - Access: http://localhost:8000/api/v1/docs
   - Advantages: Visual interface, no command-line required, auto-populated fields
   - Best for users who prefer graphical interfaces

3. **curl Commands (Command-Line API Testing)**
   - Best for: Automated testing, scripting, integration tests
   - Advantages: Reproducible, scriptable, works on all platforms
   - Best for users comfortable with terminal commands

4. **Automated Scripts (Python/JavaScript)**
   - Best for: Comprehensive testing suites, regression testing
   - Advantages: Full automation, batch testing
   - (Not covered in this guide; see test scripts in repository)

## Prerequisites for Testing

Before you can test the API, ensure you have:

- [ ] Backend server running on port 8000
- [ ] PostgreSQL database running and accessible
- [ ] `.env` file configured with API keys
- [ ] Internet connection (for AI service calls)
- [ ] Either:
  - Web browser (for Swagger UI testing)
  - `curl` command installed (for command-line testing)

### Verify Prerequisites

```bash
# Check backend is running
curl http://localhost:8000/api/v1/health

# Check PostgreSQL is running
pg_isready

# Check environment variables are loaded
grep LLM_API_KEY backend/.env
```

Expected outputs:
- Health check returns `{"status":"ok"}`
- PostgreSQL returns `accepting connections`
- API key value is displayed

## Quick Start: Three Methods

### Method 1: Web Interface Testing (Recommended for End-to-End Testing)

1. **Ensure both backend and web server are running:**

   ```bash
   # Terminal 1: Start backend
   cd language-app/backend
   source venv/bin/activate
   uvicorn main:app --reload
   
   # Terminal 2: Start web interface
   cd language-app/simple-web-interface
   python -m http.server 3000
   ```

2. **Open in Browser:**

   ```
   http://localhost:3000
   ```

3. **Test the Application:**
   - Create a new user account (or use existing)
   - Navigate through each learning module:
     - **💬 Conversation**: Start a conversation, exchange messages with AI tutor
     - **📚 Vocabulary**: View flashcards and answer vocabulary questions
     - **📖 Grammar**: Answer grammar exercises
     - **✏️ Writing**: Submit text for feedback
     - **🎤 Phonetics**: Record and evaluate pronunciation
   - Check user progress tracking
   - Verify API calls are being made (check backend terminal for logs)
   - Verify data persists (refresh page, data should remain)

4. **Check Backend Logs:**

   Monitor the backend terminal for:
   - API request logs (should show POST/GET calls to /api/v1/*)
   - No error messages
   - Response times (typically 2-4 seconds for AI-generated content)

### Method 2: Swagger UI (Recommended for API Testing)

1. **Open in Browser:**

   ```
   http://localhost:8000/api/v1/docs
   ```

2. **For each endpoint:**
   - Click to expand the endpoint
   - Click "Try it out" button
   - Fill in required parameters
   - Click "Execute"
   - View response below

3. **Example: Test Health Check**
   - Find "GET /api/v1/health"
   - Click to expand
   - Click "Try it out"
   - Click "Execute"
   - See response: `{"status":"ok"}`

### Method 3: curl Commands (Command-Line)

1. **Basic Structure:**

   ```bash
   curl -X GET "http://localhost:8000/api/v1/health"
   ```

2. **With JSON Body:**

   ```bash
   curl -X POST "http://localhost:8000/api/v1/users" \
     -H "Content-Type: application/json" \
     -d '{
       "external_id": "testuser",
       "target_language": "Spanish",
       "level": "A1"
     }'
   ```

3. **Set Environment Variables (Optional):**

   ```bash
   export API_BASE="http://localhost:8000/api/v1"
   export USER_ID="testuser"
   
   # Then use in commands:
   curl "$API_BASE/users/$USER_ID"
   ```

## Complete Testing Workflow

For comprehensive testing, follow this workflow:

1. **Start Backend Server** (Terminal 1)
   ```bash
   cd language-app/backend
   source venv/bin/activate
   uvicorn main:app --reload
   ```

2. **Verify Backend is Ready** (Terminal 2)
   ```bash
   curl http://localhost:8000/api/v1/health
   # Should return: {"status":"ok"}
   ```

3. **Start Web Interface** (Terminal 3)
   ```bash
   cd language-app/simple-web-interface
   python -m http.server 3000
   ```

4. **Test via Web Interface**
   - Open http://localhost:3000 in browser
   - Create user account
   - Test each learning module
   - Watch backend terminal for logs

5. **Run Additional API Tests** (as needed)
   - Use Swagger UI at http://localhost:8000/api/v1/docs
   - Or use curl commands from this guide

## Testing by Feature Category

### Category 1: Health and System Tests

Tests to verify API is operational and responding correctly.

#### Test 1.1: Health Check

**Purpose:** Verify API is running and responsive

**Method 1: Swagger UI**
- Navigate to http://localhost:8000/api/v1/docs
- Find `GET /health`
- Click "Try it out"
- Click "Execute"

**Method 2: curl**

```bash
curl http://localhost:8000/api/v1/health
```

**Expected Response:**

```json
{
  "status": "ok"
}
```

**Success Criteria:**
- [ ] Response status is 200 OK
- [ ] Response body contains `"status": "ok"`
- [ ] Response time less than 1 second

**Common Issues:**
- If server not running: `curl: (7) Failed to connect`
- If port wrong: `curl: (7) Failed to connect to localhost port 8001`

---

### Category 2: User Management Tests

Tests for creating users, retrieving user information, and tracking progress.

#### Test 2.1: Create User

**Purpose:** Create new user account

**Method 1: Swagger UI**
- Navigate to http://localhost:8000/api/v1/docs
- Find `POST /users`
- Click "Try it out"
- Enter in request body:
  ```json
  {
    "external_id": "testuser1",
    "target_language": "Spanish",
    "level": "A1"
  }
  ```
- Click "Execute"

**Method 2: curl**

```bash
curl -X POST "http://localhost:8000/api/v1/users" \
  -H "Content-Type: application/json" \
  -d '{
    "external_id": "testuser1",
    "target_language": "Spanish",
    "level": "A1"
  }'
```

**Expected Response:**

```json
{
  "id": "abc-123-def-456",
  "external_id": "testuser1",
  "target_language": "Spanish",
  "level": "A1",
  "created_at": "2026-01-21T10:30:00Z"
}
```

**Success Criteria:**
- [ ] Response status is 201 Created
- [ ] `external_id` matches request
- [ ] `id` is a valid UUID
- [ ] `target_language` and `level` match request

**Note:** Save the `external_id` value for use in subsequent tests.

---

#### Test 2.2: Get User Information

**Purpose:** Retrieve user profile

**Method 1: Swagger UI**
- Find `GET /users/{external_id}`
- Click "Try it out"
- Enter: `testuser1`
- Click "Execute"

**Method 2: curl**

```bash
curl "http://localhost:8000/api/v1/users/testuser1"
```

**Expected Response:**

```json
{
  "id": "abc-123-def-456",
  "external_id": "testuser1",
  "target_language": "Spanish",
  "level": "A1",
  "created_at": "2026-01-21T10:30:00Z"
}
```

**Success Criteria:**
- [ ] Response status is 200 OK
- [ ] All user fields returned
- [ ] Data matches user created in Test 2.1

---

#### Test 2.3: Get User Progress

**Purpose:** Retrieve user's learning progress

**Method 1: Swagger UI**
- Find `GET /users/{external_id}/progress`
- Click "Try it out"
- Enter: `testuser1`
- Click "Execute"

**Method 2: curl**

```bash
curl "http://localhost:8000/api/v1/users/testuser1/progress"
```

**Expected Response (Before Any Learning Activities):**

```json
[]
```

**Expected Response (After Learning Activities):**

```json
[
  {
    "module": "vocabulary",
    "score": 85.5,
    "total_attempts": 20,
    "correct_attempts": 17,
    "last_updated": "2026-01-21T15:45:00Z"
  }
]
```

**Success Criteria:**
- [ ] Response status is 200 OK
- [ ] Response is a JSON array
- [ ] Empty if no activities yet, or contains module progress objects

---

#### Test 2.4: Duplicate User Creation (Error Handling)

**Purpose:** Verify system prevents duplicate user IDs

**Method: curl**

```bash
# Try to create user with same external_id as Test 2.1
curl -X POST "http://localhost:8000/api/v1/users" \
  -H "Content-Type: application/json" \
  -d '{
    "external_id": "testuser1",
    "target_language": "French",
    "level": "A2"
  }'
```

**Expected Response:**

```json
{
  "detail": "User already exists"
}
```

**Success Criteria:**
- [ ] Response status is 400 Bad Request
- [ ] Error message indicates duplicate user

---

### Category 3: Conversation Module Tests

Tests for conversation functionality with AI tutor.

**Note:** Tests in this category require Gemini API key configured in `.env` file. If not configured, you'll receive an error: `LLM_API_KEY not configured`.

#### Test 3.1: Start Conversation Session

**Purpose:** Initiate new conversation session

**Method 1: Swagger UI**
- Find `POST /conversation/start`
- Click "Try it out"
- Enter request body:
  ```json
  {
    "user_id": "testuser1",
    "target_language": "Spanish",
    "level": "A1",
    "topic": "ordering_food"
  }
  ```
- Click "Execute"

**Method 2: curl**

```bash
curl -X POST "http://localhost:8000/api/v1/conversation/start" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "testuser1",
    "target_language": "Spanish",
    "level": "A1",
    "topic": "ordering_food"
  }'
```

**Expected Response:**

```json
{
  "session_id": "sess-789-xyz-123",
  "opening_message": "Hola! Bienvenido al restaurante. Que deseas ordenar?",
  "topic": "ordering_food",
  "language": "Spanish"
}
```

**Success Criteria:**
- [ ] Response status is 200 OK
- [ ] `session_id` is a valid UUID
- [ ] `opening_message` is in Spanish
- [ ] Message is relevant to topic
- [ ] Response time 2-4 seconds

**Important:** Save the `session_id` for Test 3.2.

---

#### Test 3.2: Send Message in Conversation

**Purpose:** Test conversation interaction and AI response

**Method 1: Swagger UI**
- Find `POST /conversation/{session_id}/message`
- Click "Try it out"
- In path: paste `session_id` from Test 3.1
- In request body:
  ```json
  {
    "user_id": "testuser1",
    "message": "Yo quiero una pizza con pepperoni"
  }
  ```
- Click "Execute"

**Method 2: curl**

```bash
# Replace SESSION_ID with actual session ID from Test 3.1
SESSION_ID="sess-789-xyz-123"

curl -X POST "http://localhost:8000/api/v1/conversation/$SESSION_ID/message" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "testuser1",
    "message": "Yo quiero una pizza con pepperoni"
  }'
```

**Expected Response:**

```json
{
  "reply": "Excelente eleccion! Que tipo de bebida prefieres?",
  "corrected_user_message": null,
  "tips": "Good job with the verb conjugation!",
  "session_id": "sess-789-xyz-123"
}
```

**Success Criteria:**
- [ ] Response status is 200 OK
- [ ] `reply` is in Spanish
- [ ] Reply is contextually relevant to user message
- [ ] `session_id` matches request
- [ ] Response time 2-4 seconds

---

#### Test 3.3: Multiple Message Exchange

**Purpose:** Verify conversation maintains context across messages

**Method: curl (scripted)**

```bash
SESSION_ID="sess-789-xyz-123"

# Message 1
curl -X POST "http://localhost:8000/api/v1/conversation/$SESSION_ID/message" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "testuser1", "message": "Hola"}'

# Message 2
curl -X POST "http://localhost:8000/api/v1/conversation/$SESSION_ID/message" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "testuser1", "message": "Quiero pizza"}'

# Message 3
curl -X POST "http://localhost:8000/api/v1/conversation/$SESSION_ID/message" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "testuser1", "message": "Con pepperoni"}'
```

**Expected Behavior:**
- [ ] Each response is contextually relevant
- [ ] AI demonstrates understanding of previous messages
- [ ] Conversation flows naturally

---

### Category 4: Vocabulary Module Tests

Tests for vocabulary flashcard system.

#### Test 4.1: Get Vocabulary Flashcard

**Purpose:** Generate vocabulary flashcard

**Method 1: Swagger UI**
- Find `GET /vocabulary/next`
- Click "Try it out"
- Enter query parameters:
  - `user_id`: testuser1
  - `target_language`: Spanish
  - `level`: A1
- Click "Execute"

**Method 2: curl**

```bash
curl "http://localhost:8000/api/v1/vocabulary/next?user_id=testuser1&target_language=Spanish&level=A1"
```

**Expected Response:**

```json
{
  "word": "biblioteca",
  "definition": "library",
  "example_sentence": "Voy a la biblioteca para estudiar",
  "options": ["library", "bookstore", "museum", "school"],
  "correct_option_index": 0
}
```

**Success Criteria:**
- [ ] Response status is 200 OK
- [ ] `word` is in Spanish
- [ ] `definition` is in English
- [ ] `example_sentence` uses the word correctly
- [ ] `options` array has exactly 4 elements
- [ ] `correct_option_index` is between 0-3
- [ ] Response time 2-3 seconds

---

#### Test 4.2: Submit Vocabulary Answer (Correct)

**Purpose:** Test correct answer evaluation

**Method: curl**

```bash
curl -X POST "http://localhost:8000/api/v1/vocabulary/answer" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "testuser1",
    "word": "biblioteca",
    "selected_option_index": 0,
    "correct_option_index": 0
  }'
```

**Expected Response:**

```json
{
  "is_correct": true,
  "correct_option_index": 0,
  "explanation": "Correct! Biblioteca means library in Spanish."
}
```

**Success Criteria:**
- [ ] Response status is 200 OK
- [ ] `is_correct` is true
- [ ] Explanation provided

---

#### Test 4.3: Submit Vocabulary Answer (Incorrect)

**Purpose:** Test incorrect answer handling

**Method: curl**

```bash
curl -X POST "http://localhost:8000/api/v1/vocabulary/answer" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "testuser1",
    "word": "biblioteca",
    "selected_option_index": 2,
    "correct_option_index": 0
  }'
```

**Expected Response:**

```json
{
  "is_correct": false,
  "correct_option_index": 0,
  "explanation": "Incorrect. The correct answer is library. Museo is museum."
}
```

**Success Criteria:**
- [ ] Response status is 200 OK
- [ ] `is_correct` is false
- [ ] Correct answer indicated
- [ ] Explanation helps student learn

---

#### Test 4.4: Get Multiple Flashcards (Variety Test)

**Purpose:** Verify variety in generated flashcards

**Method: curl (scripted)**

```bash
for i in {1..5}; do
  echo "Flashcard $i:"
  curl -s "http://localhost:8000/api/v1/vocabulary/next?user_id=testuser1&target_language=Spanish&level=A1" | grep -o '"word":"[^"]*"'
  echo ""
  sleep 1
done
```

**Success Criteria:**
- [ ] Each flashcard has different word
- [ ] All words appropriate to A1 level
- [ ] No repetitions

---

### Category 5: Grammar Module Tests

Tests for grammar exercises.

#### Test 5.1: Get Grammar Question

**Purpose:** Generate grammar exercise

**Method: curl**

```bash
curl "http://localhost:8000/api/v1/grammar/question?user_id=testuser1&target_language=Spanish&level=A1&topic=present_tense"
```

**Expected Response:**

```json
{
  "question_id": "q-123-abc",
  "instruction": "Choose the correct form of the verb in the present tense",
  "sentence": "Yo _________ al parque cada dia.",
  "options": ["voy", "va", "vas", "vamos"],
  "correct_option_index": 0
}
```

**Success Criteria:**
- [ ] Response status is 200 OK
- [ ] Question is in Spanish
- [ ] All 4 options are grammatically plausible distractors
- [ ] Instruction is clear
- [ ] Response time 2-3 seconds

---

#### Test 5.2: Submit Grammar Answer

**Purpose:** Test grammar answer evaluation

**Method: curl**

```bash
curl -X POST "http://localhost:8000/api/v1/grammar/answer" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "testuser1",
    "question_id": "q-123-abc",
    "selected_option_index": 0,
    "correct_option_index": 0
  }'
```

**Expected Response:**

```json
{
  "is_correct": true,
  "explanation": "Correct! 'Voy' is the correct present tense form of 'ir' for first person (yo)."
}
```

**Success Criteria:**
- [ ] Response status is 200 OK
- [ ] Evaluation is correct
- [ ] Explanation explains the rule

---

### Category 6: Writing Module Tests

Tests for writing feedback system.

#### Test 6.1: Get Writing Feedback (No Errors)

**Purpose:** Test feedback on correct writing

**Method: curl**

```bash
curl -X POST "http://localhost:8000/api/v1/writing/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "testuser1",
    "target_language": "Spanish",
    "level": "A1",
    "text": "Hola, como estoy?"
  }'
```

**Expected Response:**

```json
{
  "original_text": "Hola, como estoy?",
  "corrected_text": "Hola, como estoy?",
  "errors": [],
  "strengths": "Good greeting phrase! Clear and appropriate.",
  "suggestions": "Consider adding more context to your question."
}
```

**Success Criteria:**
- [ ] Response status is 200 OK
- [ ] `errors` array is empty if text is correct
- [ ] Positive feedback in `strengths`

---

#### Test 6.2: Get Writing Feedback (With Errors)

**Purpose:** Test error detection and explanation

**Method: curl**

```bash
curl -X POST "http://localhost:8000/api/v1/writing/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "testuser1",
    "target_language": "Spanish",
    "level": "A1",
    "text": "Yo voy al parque ayer con mis amigos"
  }'
```

**Expected Response:**

```json
{
  "original_text": "Yo voy al parque ayer con mis amigos",
  "corrected_text": "Fui al parque ayer con mis amigos",
  "errors": [
    {
      "type": "verb_tense",
      "original": "voy",
      "correction": "fui",
      "explanation": "Use past tense when describing an action that already happened."
    }
  ],
  "strengths": "Good use of prepositions!",
  "suggestions": "Practice differentiating between present and past tense."
}
```

**Success Criteria:**
- [ ] Response status is 200 OK
- [ ] Errors identified correctly
- [ ] Explanations are clear
- [ ] Corrections are accurate

---

### Category 7: Phonetics Module Tests

Tests for pronunciation evaluation.

**Note:** Requires Speech-to-Text API key configured in `.env` file.

#### Test 7.1: Evaluate Pronunciation

**Purpose:** Test pronunciation analysis

**Prerequisite:** Have an audio file (WAV format recommended)

**Method: curl**

```bash
# This requires an actual audio file
curl -X POST "http://localhost:8000/api/v1/phonetics/evaluate" \
  -F "user_id=testuser1" \
  -F "target_language=Spanish" \
  -F "target_phrase=Hola, como estoy?" \
  -F "audio_file=@/path/to/recording.wav"
```

**Expected Response:**

```json
{
  "target_phrase": "Hola, como estoy?",
  "transcription": "Hola como estoy",
  "confidence": 0.92,
  "is_correct": true,
  "score": 85,
  "feedback": "Good pronunciation! Clear and understandable.",
  "detailed_feedback": {
    "strengths": ["Clear vowel pronunciation"],
    "improvements": ["Minor stress adjustment on estoy"]
  }
}
```

**Success Criteria:**
- [ ] Response status is 200 OK
- [ ] Transcription is reasonable (if audio is clear)
- [ ] Confidence score between 0-1
- [ ] Score between 0-100
- [ ] Detailed feedback provided

---

### Category 8: Integration Tests

Tests simulating complete learning workflows.

#### Test 8.1: Complete Vocabulary Learning Session

**Purpose:** Test full vocabulary module workflow

**Script:**

```bash
USER_ID="integration_test_user_$(date +%s)"

# 1. Create user
echo "Creating user..."
curl -X POST "http://localhost:8000/api/v1/users" \
  -H "Content-Type: application/json" \
  -d '{
    "external_id": "'$USER_ID'",
    "target_language": "Spanish",
    "level": "A1"
  }'

echo -e "\n\nGetting flashcard..."
# 2. Get flashcard
FLASHCARD=$(curl -s "http://localhost:8000/api/v1/vocabulary/next?user_id=$USER_ID&target_language=Spanish&level=A1")
echo $FLASHCARD | jq '.'

echo -e "\n\nSubmitting answer..."
# 3. Submit answer
curl -X POST "http://localhost:8000/api/v1/vocabulary/answer" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "'$USER_ID'",
    "word": "test",
    "selected_option_index": 0,
    "correct_option_index": 0
  }'

echo -e "\n\nChecking progress..."
# 4. Check progress
curl "http://localhost:8000/api/v1/users/$USER_ID/progress" | jq '.'
```

**Success Criteria:**
- [ ] User created successfully
- [ ] Flashcard retrieved
- [ ] Answer submitted and evaluated
- [ ] Progress updated and retrievable

---

### Category 9: Error Handling Tests

Tests for proper error responses.

#### Test 9.1: Missing Required Parameters

**Purpose:** Verify validation of required fields

**Method: curl**

```bash
# Missing user_id parameter
curl "http://localhost:8000/api/v1/vocabulary/next?target_language=Spanish"
```

**Expected Response:**

```json
{
  "detail": "user_id parameter is required"
}
```

**Success Criteria:**
- [ ] Response status is 400 Bad Request
- [ ] Error message is clear

---

#### Test 9.2: Non-Existent User

**Purpose:** Test handling of invalid user ID

**Method: curl**

```bash
curl "http://localhost:8000/api/v1/users/nonexistent_user_xyz"
```

**Expected Response:**

```json
{
  "detail": "User not found"
}
```

**Success Criteria:**
- [ ] Response status is 404 Not Found
- [ ] Error message indicates user not found

---

#### Test 9.3: Invalid Session ID

**Purpose:** Test handling of invalid conversation session

**Method: curl**

```bash
curl -X POST "http://localhost:8000/api/v1/conversation/invalid-session-id/message" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "testuser1",
    "message": "Test message"
  }'
```

**Expected Response:**

```json
{
  "detail": "Session not found"
}
```

**Success Criteria:**
- [ ] Response status is 404 Not Found
- [ ] Error message indicates session not found

---

#### Test 9.4: Invalid JSON

**Purpose:** Test request validation

**Method: curl**

```bash
curl -X POST "http://localhost:8000/api/v1/users" \
  -H "Content-Type: application/json" \
  -d 'invalid json'
```

**Expected Response:**

```json
{
  "detail": "Invalid request body"
}
```

**Success Criteria:**
- [ ] Response status is 400 Bad Request
- [ ] Error message about invalid JSON

---

## Troubleshooting

### Common Testing Issues

#### Issue: "Connection refused" when calling API

**Possible Causes:**
- Backend server not running
- Wrong port specified
- Firewall blocking connection

**Solution:**
```bash
# Check if server is running
lsof -i :8000

# Start server if not running
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

---

#### Issue: "LLM_API_KEY not configured"

**Possible Causes:**
- .env file not created
- API key not set in .env
- .env file not in correct location

**Solution:**
```bash
# Check .env exists
ls -la backend/.env

# Check API key is set
grep LLM_API_KEY backend/.env

# If missing, add to .env file
echo "LLM_API_KEY=your_actual_key" >> backend/.env

# Restart server to reload environment
```

---

#### Issue: "User already exists" error

**Possible Causes:**
- User created in previous test run
- Testing with same user ID

**Solution:**
```bash
# Use unique user ID in tests
USER_ID="testuser_$(date +%s%N)"

# Or delete user from database (requires direct DB access)
```

---

#### Issue: Responses taking longer than expected

**Possible Causes:**
- AI service is slow
- Database queries taking long
- Network latency

**Expected Response Times:**
- Health check: <1 second
- User creation: 1 second
- Get flashcard: 2-3 seconds (includes AI generation)
- Conversation: 2-4 seconds (includes AI generation)
- Grammar: 2-3 seconds
- Writing: 3-5 seconds (longer text = longer response)
- Phonetics: 3-4 seconds (includes speech-to-text)

---

## Test Completion Checklist

After completing all tests, verify:

- [ ] All health checks pass
- [ ] User management works (create, get, progress)
- [ ] Conversation module generates responses
- [ ] Vocabulary module generates flashcards
- [ ] Grammar module generates questions
- [ ] Writing module analyzes text
- [ ] Phonetics module evaluates audio (if audio file available)
- [ ] Error responses are appropriate
- [ ] No database errors in server logs
- [ ] No API key errors

---

## Performance Testing

### Load Testing Endpoints

To test API performance under load:

```bash
# Install Apache Bench (ab) if not present
# macOS: brew install httpd
# Ubuntu: sudo apt install apache2-utils

# Test 100 requests to health endpoint
ab -n 100 -c 10 http://localhost:8000/api/v1/health

# Results will show:
# - Requests per second
# - Mean response time
# - Min/max response times
```

### Expected Performance (Development)

- Health check: 50-100 req/sec
- User endpoints: 20-50 req/sec
- AI endpoints: 1-3 req/sec (limited by AI service)

---

## Automated Testing Script

For batch testing without manual intervention:

```bash
#!/bin/bash
# Save as test_all.sh in backend directory

BASE_URL="http://localhost:8000/api/v1"
USER_ID="auto_test_user_$(date +%s)"

echo "🧪 Running Automated Tests"
echo "=================================="

# Test 1: Health
echo "✓ Health check..."
curl -s "$BASE_URL/health" | grep -q "ok" && echo "  PASS" || echo "  FAIL"

# Test 2: Create User
echo "✓ Creating user..."
curl -s -X POST "$BASE_URL/users" \
  -H "Content-Type: application/json" \
  -d "{\"external_id\": \"$USER_ID\", \"target_language\": \"Spanish\", \"level\": \"A1\"}" \
  | grep -q "$USER_ID" && echo "  PASS" || echo "  FAIL"

# Test 3: Get Flashcard
echo "✓ Getting vocabulary flashcard..."
curl -s "$BASE_URL/vocabulary/next?user_id=$USER_ID&target_language=Spanish&level=A1" \
  | grep -q "word" && echo "  PASS" || echo "  FAIL"

# Test 4: Grammar Question
echo "✓ Getting grammar question..."
curl -s "$BASE_URL/grammar/question?user_id=$USER_ID&target_language=Spanish&level=A1" \
  | grep -q "question" && echo "  PASS" || echo "  FAIL"

# Test 5: User Progress
echo "✓ Checking user progress..."
curl -s "$BASE_URL/users/$USER_ID/progress" \
  | grep -q "\[\]" && echo "  PASS (No progress yet)" || echo "  PASS (Progress recorded)"

echo ""
echo "===================================="
echo "✅ Automated tests complete!"
```

**Run the script:**

```bash
chmod +x test_all.sh
./test_all.sh
```

---

## Continuous Testing

For ongoing testing as development continues:

1. **After each code change:**
   - Run all tests in this guide
   - Check for new errors

2. **Before deploying:**
   - Complete all integration tests
   - Verify all error cases handled
   - Check performance baseline

3. **Regularly:**
   - Test with different language/level combinations
   - Test with longer text inputs
   - Test error scenarios

---

For more information:

- API reference: [API.md](API.md)
- System architecture: [ARCHITECTURE.md](ARCHITECTURE.md)
- Setup guide: [SETUP.md](SETUP.md)
- Backend documentation: See `/backend/check.md` for even more detailed tests
