# Backend Testing Guide - check.md

A comprehensive guide to test all features of the Language Learning Backend API.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Setup for Testing](#setup-for-testing)
- [Testing Strategy](#testing-strategy)
- [1. Health & System Tests](#1-health--system-tests)
- [2. User Management Tests](#2-user-management-tests)
- [3. Conversation Module Tests](#3-conversation-module-tests)
- [4. Vocabulary Module Tests](#4-vocabulary-module-tests)
- [5. Grammar Module Tests](#5-grammar-module-tests)
- [6. Writing Module Tests](#6-writing-module-tests)
- [7. Phonetics Module Tests](#7-phonetics-module-tests)
- [8. Progress Tracking Tests](#8-progress-tracking-tests)
- [9. Error Handling Tests](#9-error-handling-tests)
- [10. Integration Tests](#10-integration-tests)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before testing, ensure you have:

- [x] Backend server running (`uvicorn main:app --reload`)
- [x] PostgreSQL database created and running
- [x] `.env` file configured with valid API keys
- [x] `curl` installed (or use Swagger UI, Postman, etc.)
- [x] Server accessible at `http://localhost:8000`

---

## Setup for Testing

### 1. Start the Server

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 2. Verify Server is Running

Open browser to: `http://localhost:8000/api/v1/docs`

You should see the Swagger UI with all endpoints.

### 3. Set Test Variables

```bash
export BASE_URL="http://localhost:8000/api/v1"
export TEST_USER_ID="test_user_$(date +%s)"
```

---

## Testing Strategy

### Three Ways to Test:

1. **Swagger UI (Recommended for Beginners)** - Interactive browser testing
2. **curl Commands** - Command-line testing (examples below)
3. **Automated Scripts** - For comprehensive testing

We'll provide examples for all three methods.

---

## 1. Health & System Tests

### Test 1.1: Health Check

**Purpose:** Verify the API is running

**Method 1: curl**
```bash
curl http://localhost:8000/api/v1/health
```

**Expected Response:**
```json
{
  "status": "ok"
}
```

**Method 2: Swagger UI**
- Go to `http://localhost:8000/api/v1/docs`
- Find `GET /health` endpoint
- Click "Try it out"
- Click "Execute"

**✅ Success Criteria:**
- Returns 200 OK
- Response contains `"status": "ok"`

---

### Test 1.2: Root Endpoint

**Purpose:** Verify API information endpoint

```bash
curl http://localhost:8000/api/v1/
```

**Expected Response:**
```json
{
  "message": "Hello from the Language Learning Backend!"
}
```

**✅ Success Criteria:**
- Returns 200 OK
- Contains greeting message

---

## 2. User Management Tests

### Test 2.1: Create a New User

**Purpose:** Create a test user for subsequent tests

**curl Command:**
```bash
curl -X POST "http://localhost:8000/api/v1/users" \
  -H "Content-Type: application/json" \
  -d '{
    "external_id": "test_user_12345",
    "target_language": "Spanish",
    "level": "A2"
  }'
```

**Expected Response:**
```json
{
  "id": "uuid-here",
  "external_id": "test_user_12345",
  "target_language": "Spanish",
  "level": "A2"
}
```

**✅ Success Criteria:**
- Returns 200 OK
- Response contains UUID
- `external_id` matches request

**📝 Note:** Save the `external_id` for use in other tests!

---

### Test 2.2: Get User by External ID

**Purpose:** Retrieve user information

```bash
curl http://localhost:8000/api/v1/users/test_user_12345
```

**Expected Response:**
```json
{
  "id": "uuid-here",
  "external_id": "test_user_12345",
  "target_language": "Spanish",
  "level": "A2"
}
```

**✅ Success Criteria:**
- Returns 200 OK
- User data matches created user

---

### Test 2.3: Duplicate User Creation (Error Test)

**Purpose:** Verify duplicate prevention

```bash
curl -X POST "http://localhost:8000/api/v1/users" \
  -H "Content-Type: application/json" \
  -d '{
    "external_id": "test_user_12345",
    "target_language": "Spanish",
    "level": "A2"
  }'
```

**Expected Response:**
```json
{
  "detail": "User already exists"
}
```

**✅ Success Criteria:**
- Returns 400 Bad Request
- Error message indicates duplicate user

---

## 3. Conversation Module Tests

### Test 3.1: Start a Conversation Session

**Purpose:** Initialize a conversation session

**curl Command:**
```bash
curl -X POST "http://localhost:8000/api/v1/conversation/start" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_12345",
    "target_language": "Spanish",
    "level": "A2",
    "topic": "ordering food"
  }'
```

**Expected Response:**
```json
{
  "session_id": "uuid-session-id",
  "opening_message": "¡Hola! ¿Qué te gustaría pedir hoy?"
}
```

**✅ Success Criteria:**
- Returns 200 OK
- `session_id` is a valid UUID
- `opening_message` is in Spanish
- Message is related to ordering food
- Response time < 5 seconds (LLM call)

**📝 Note:** Save the `session_id` for next test!

---

### Test 3.2: Send a Message in Conversation

**Purpose:** Test conversation interaction

**curl Command:**
```bash
curl -X POST "http://localhost:8000/api/v1/conversation/{session_id}/message" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_12345",
    "message": "Yo quiero una pizza por favor"
  }'
```

**Replace `{session_id}` with the actual session ID from Test 3.1**

**Expected Response:**
```json
{
  "reply": "¡Excelente elección! ¿Qué tipo de pizza prefieres?",
  "corrected_user_message": "Yo quiero una pizza, por favor",
  "tips": "Great! Remember to use commas before 'por favor'.",
  "session_id": "uuid-session-id"
}
```

**✅ Success Criteria:**
- Returns 200 OK
- `reply` is in Spanish and contextual
- May include `corrected_user_message` if there are errors
- May include `tips` with helpful feedback
- Response time < 5 seconds

---

### Test 3.3: Multiple Message Exchange

**Purpose:** Test conversation context retention

**Send 3-4 messages in sequence:**

1. "Yo quiero una pizza"
2. "Con pepperoni y queso"
3. "¿Cuánto cuesta?"
4. "Perfecto, la quiero"

**✅ Success Criteria:**
- Each reply is contextually relevant
- AI remembers previous messages
- Responses flow naturally

---

### Test 3.4: Conversation with Different Topics

**Start new sessions with different topics:**

**Test 3.4a: Travel Topic**
```bash
curl -X POST "http://localhost:8000/api/v1/conversation/start" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_12345",
    "target_language": "French",
    "level": "B1",
    "topic": "travel"
  }'
```

**Test 3.4b: Shopping Topic**
```bash
curl -X POST "http://localhost:8000/api/v1/conversation/start" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_12345",
    "target_language": "German",
    "level": "A1",
    "topic": "shopping"
  }'
```

**✅ Success Criteria:**
- Opening messages match the topic
- Language matches the request

---

## 4. Vocabulary Module Tests

### Test 4.1: Get a Vocabulary Flashcard

**Purpose:** Generate a vocabulary flashcard

**curl Command:**
```bash
curl "http://localhost:8000/api/v1/vocabulary/next?user_id=test_user_12345&target_language=Spanish&level=A2"
```

**Expected Response:**
```json
{
  "word": "biblioteca",
  "definition": "library",
  "example_sentence": "Voy a la biblioteca para estudiar.",
  "options": [
    "library",
    "bookstore",
    "school",
    "museum"
  ],
  "correct_option_index": 0
}
```

**✅ Success Criteria:**
- Returns 200 OK
- `word` is in target language (Spanish)
- `definition` is in English
- `example_sentence` uses the word correctly
- `options` contains 4 choices
- `correct_option_index` is between 0-3
- Response time < 5 seconds

---

### Test 4.2: Get Multiple Flashcards

**Purpose:** Test variety and randomness

**Run the same command 5 times:**
```bash
for i in {1..5}; do
  echo "Flashcard $i:"
  curl "http://localhost:8000/api/v1/vocabulary/next?user_id=test_user_12345&target_language=Spanish&level=A2"
  echo ""
done
```

**✅ Success Criteria:**
- Each flashcard has different words
- Difficulty appropriate for A2 level
- All responses valid

---

### Test 4.3: Test Different Languages

**Test 4.3a: French Vocabulary**
```bash
curl "http://localhost:8000/api/v1/vocabulary/next?user_id=test_user_12345&target_language=French&level=B1"
```

**Test 4.3b: German Vocabulary**
```bash
curl "http://localhost:8000/api/v1/vocabulary/next?user_id=test_user_12345&target_language=German&level=A1"
```

**✅ Success Criteria:**
- Words are in correct language
- Difficulty matches level

---

### Test 4.4: Submit Vocabulary Answer (Correct)

**Purpose:** Test correct answer submission

**curl Command:**
```bash
curl -X POST "http://localhost:8000/api/v1/vocabulary/answer" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_12345",
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
  "explanation": "Correct!"
}
```

**✅ Success Criteria:**
- Returns 200 OK
- `is_correct` is true
- Progress is updated in database

---

### Test 4.5: Submit Vocabulary Answer (Incorrect)

**Purpose:** Test incorrect answer submission

```bash
curl -X POST "http://localhost:8000/api/v1/vocabulary/answer" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_12345",
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
  "explanation": "The correct answer was option 0."
}
```

**✅ Success Criteria:**
- Returns 200 OK
- `is_correct` is false
- Shows correct answer

---

## 5. Grammar Module Tests

### Test 5.1: Get a Grammar Question

**Purpose:** Generate a grammar question

**curl Command:**
```bash
curl "http://localhost:8000/api/v1/grammar/question?user_id=test_user_12345&target_language=Spanish&level=A2&topic=past%20tense"
```

**Expected Response:**
```json
{
  "question_id": "uuid-question-id",
  "question_text": "Complete the sentence: Ayer yo ___ al parque.",
  "options": [
    "fui",
    "voy",
    "iré",
    "iba"
  ],
  "correct_option_index": 0,
  "explanation": "Use preterite 'fui' for completed past actions."
}
```

**✅ Success Criteria:**
- Returns 200 OK
- Question is about the specified topic
- Has 4 options
- Includes explanation
- Response time < 5 seconds

---

### Test 5.2: Get Questions on Different Topics

**Test 5.2a: Articles**
```bash
curl "http://localhost:8000/api/v1/grammar/question?user_id=test_user_12345&target_language=French&level=A1&topic=articles"
```

**Test 5.2b: Verb Conjugation**
```bash
curl "http://localhost:8000/api/v1/grammar/question?user_id=test_user_12345&target_language=German&level=B1&topic=verb%20conjugation"
```

**✅ Success Criteria:**
- Questions match the topic
- Difficulty appropriate for level

---

### Test 5.3: Submit Grammar Answer (Correct)

**Purpose:** Test correct answer submission

```bash
curl -X POST "http://localhost:8000/api/v1/grammar/answer" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_12345",
    "question_id": "uuid-from-previous-test",
    "selected_option_index": 0,
    "correct_option_index": 0,
    "explanation": "Use preterite for completed past actions."
  }'
```

**Expected Response:**
```json
{
  "is_correct": true,
  "correct_option_index": 0,
  "explanation": "Use preterite for completed past actions."
}
```

**✅ Success Criteria:**
- Returns 200 OK
- `is_correct` is true
- Explanation provided

---

### Test 5.4: Submit Grammar Answer (Incorrect)

**Purpose:** Test incorrect answer feedback

```bash
curl -X POST "http://localhost:8000/api/v1/grammar/answer" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_12345",
    "question_id": "uuid-from-previous-test",
    "selected_option_index": 1,
    "correct_option_index": 0,
    "explanation": "Use preterite for completed past actions."
  }'
```

**Expected Response:**
```json
{
  "is_correct": false,
  "correct_option_index": 0,
  "explanation": "Use preterite for completed past actions."
}
```

**✅ Success Criteria:**
- Returns 200 OK
- Shows correct answer
- Provides explanation

---

## 6. Writing Module Tests

### Test 6.1: Get Writing Feedback (Good Text)

**Purpose:** Test feedback on well-written text

**curl Command:**
```bash
curl -X POST "http://localhost:8000/api/v1/writing/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_12345",
    "target_language": "Spanish",
    "level": "B1",
    "text": "Hoy fui al mercado y compré frutas frescas. Me gusta cocinar con ingredientes naturales."
  }'
```

**Expected Response:**
```json
{
  "corrected_text": "Hoy fui al mercado y compré frutas frescas. Me gusta cocinar con ingredientes naturales.",
  "overall_comment": "Excellent work! Your grammar and vocabulary are appropriate for B1 level.",
  "inline_explanation": "No major corrections needed.",
  "score": 95
}
```

**✅ Success Criteria:**
- Returns 200 OK
- Score is between 0-100
- Provides feedback
- Response time < 5 seconds

---

### Test 6.2: Get Writing Feedback (Text with Errors)

**Purpose:** Test error detection and correction

```bash
curl -X POST "http://localhost:8000/api/v1/writing/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_12345",
    "target_language": "Spanish",
    "level": "A1",
    "text": "Yo es estudiante. Yo vive en Madrid. Me gusta mucho la ciudad."
  }'
```

**Expected Response:**
```json
{
  "corrected_text": "Yo soy estudiante. Yo vivo en Madrid. Me gusta mucho la ciudad.",
  "overall_comment": "Good attempt! Watch verb conjugations - 'ser' and 'vivir' need proper forms.",
  "inline_explanation": "- 'es' should be 'soy' (yo soy)\n- 'vive' should be 'vivo' (yo vivo)",
  "score": 65
}
```

**✅ Success Criteria:**
- Returns 200 OK
- Identifies errors
- Provides corrections
- Score reflects quality
- Explanation is helpful

---

### Test 6.3: Test Different Languages

**Test 6.3a: French Writing**
```bash
curl -X POST "http://localhost:8000/api/v1/writing/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_12345",
    "target_language": "French",
    "level": "A2",
    "text": "Je suis allé au cinéma hier. Le film était très intéressant."
  }'
```

**Test 6.3b: German Writing**
```bash
curl -X POST "http://localhost:8000/api/v1/writing/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_12345",
    "target_language": "German",
    "level": "B1",
    "text": "Ich habe gestern einen Film gesehen. Es war sehr interessant."
  }'
```

**✅ Success Criteria:**
- Feedback appropriate for each language
- Grammar rules specific to language

---

## 7. Phonetics Module Tests

### Test 7.1: Evaluate Pronunciation (with Audio File)

**Purpose:** Test pronunciation evaluation

**⚠️ Note:** This requires an actual audio file. Create a test audio file first.

**Create Test Audio (macOS/Linux):**
```bash
# Record a short audio saying "Hello"
# Save as test_audio.wav
```

**curl Command:**
```bash
curl -X POST "http://localhost:8000/api/v1/phonetics/evaluate" \
  -F "user_id=test_user_12345" \
  -F "target_language=en-US" \
  -F "target_phrase=Hello, how are you?" \
  -F "audio_file=@test_audio.wav"
```

**Expected Response:**
```json
{
  "transcript": "Hello how are you",
  "stt_confidence": 0.92,
  "score": 88,
  "feedback": "Good pronunciation! Your clarity was excellent.",
  "word_level_feedback": {
    "Hello": "Clear pronunciation",
    "how": "Slight hesitation"
  }
}
```

**✅ Success Criteria:**
- Returns 200 OK
- Transcript is similar to target phrase
- Score is between 0-100
- Feedback is provided
- Response time < 10 seconds (STT + LLM)

---

### Test 7.2: Test with Different Languages

**Test 7.2a: Spanish Pronunciation**
```bash
curl -X POST "http://localhost:8000/api/v1/phonetics/evaluate" \
  -F "user_id=test_user_12345" \
  -F "target_language=es-ES" \
  -F "target_phrase=Hola, ¿cómo estás?" \
  -F "audio_file=@spanish_audio.wav"
```

**Test 7.2b: French Pronunciation**
```bash
curl -X POST "http://localhost:8000/api/v1/phonetics/evaluate" \
  -F "user_id=test_user_12345" \
  -F "target_language=fr-FR" \
  -F "target_phrase=Bonjour, comment allez-vous?" \
  -F "audio_file=@french_audio.wav"
```

**✅ Success Criteria:**
- STT recognizes correct language
- Feedback specific to language

---

### Test 7.3: Perfect Match Test

**Purpose:** Test with perfect pronunciation

**Use Text-to-Speech to generate audio, then test:**
```bash
# Generate audio file with TTS of exact phrase
# Then test with same phrase
```

**✅ Success Criteria:**
- High confidence score (>0.9)
- High pronunciation score (>95)

---

## 8. Progress Tracking Tests

### Test 8.1: Get User Progress (After Testing)

**Purpose:** Verify progress is being tracked

```bash
curl "http://localhost:8000/api/v1/users/test_user_12345/progress"
```

**Expected Response:**
```json
[
  {
    "module": "conversation",
    "score": null,
    "total_attempts": 2,
    "correct_attempts": 0
  },
  {
    "module": "vocabulary",
    "score": 50.0,
    "total_attempts": 2,
    "correct_attempts": 1
  },
  {
    "module": "grammar",
    "score": 50.0,
    "total_attempts": 2,
    "correct_attempts": 1
  },
  {
    "module": "writing",
    "score": 80.0,
    "total_attempts": 2,
    "correct_attempts": 0
  },
  {
    "module": "phonetics",
    "score": 88.0,
    "total_attempts": 1,
    "correct_attempts": 0
  }
]
```

**✅ Success Criteria:**
- Returns array of progress records
- Each module tested has a record
- Attempt counts match your tests
- Scores are calculated correctly

---

### Test 8.2: Progress Updates

**Purpose:** Verify progress updates after each activity

**Steps:**
1. Get initial progress
2. Complete 3 vocabulary exercises
3. Get progress again
4. Verify `total_attempts` increased by 3

```bash
# Initial progress
curl "http://localhost:8000/api/v1/users/test_user_12345/progress"

# Do 3 vocabulary exercises...

# Check updated progress
curl "http://localhost:8000/api/v1/users/test_user_12345/progress"
```

**✅ Success Criteria:**
- Total attempts increment correctly
- Correct attempts tracked accurately
- Scores update appropriately

---

## 9. Error Handling Tests

### Test 9.1: Invalid User ID

**Purpose:** Test error handling for non-existent user

```bash
curl "http://localhost:8000/api/v1/users/nonexistent_user_999"
```

**Expected Response:**
```json
{
  "detail": "User not found"
}
```

**✅ Success Criteria:**
- Returns 404 Not Found
- Error message is clear

---

### Test 9.2: Invalid Session ID (Conversation)

**Purpose:** Test invalid conversation session

```bash
curl -X POST "http://localhost:8000/api/v1/conversation/invalid-uuid-123/message" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_12345",
    "message": "Hello"
  }'
```

**Expected Response:**
```json
{
  "detail": "Conversation session invalid-uuid-123 not found"
}
```

**✅ Success Criteria:**
- Returns 404 Not Found or 500 with error
- Error describes the issue

---

### Test 9.3: Missing Required Fields

**Purpose:** Test validation

```bash
curl -X POST "http://localhost:8000/api/v1/conversation/start" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_12345"
  }'
```

**Expected Response:**
```json
{
  "detail": [
    {
      "loc": ["body", "target_language"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**✅ Success Criteria:**
- Returns 422 Unprocessable Entity
- Shows which fields are missing

---

### Test 9.4: Invalid API Key (LLM Failure)

**Purpose:** Test behavior when LLM API fails

**Temporarily set invalid LLM API key in .env:**
```env
LLM_API_KEY=invalid_key_test
```

**Restart server and test:**
```bash
curl "http://localhost:8000/api/v1/vocabulary/next?user_id=test_user_12345&target_language=Spanish&level=A2"
```

**Expected Response:**
```json
{
  "detail": "HTTP error during LLM API call: ..."
}
```

**✅ Success Criteria:**
- Returns 500 Internal Server Error
- Error message indicates LLM failure
- **Don't forget to restore valid API key!**

---

## 10. Integration Tests

### Test 10.1: Complete User Journey

**Purpose:** Simulate a full user experience

**Scenario:** New user learns Spanish

```bash
# Step 1: Create user
curl -X POST "http://localhost:8000/api/v1/users" \
  -H "Content-Type: application/json" \
  -d '{
    "external_id": "journey_user_1",
    "target_language": "Spanish",
    "level": "A1"
  }'

# Step 2: Start conversation
CONVERSATION_RESPONSE=$(curl -X POST "http://localhost:8000/api/v1/conversation/start" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "journey_user_1",
    "target_language": "Spanish",
    "level": "A1",
    "topic": "greetings"
  }')

SESSION_ID=$(echo $CONVERSATION_RESPONSE | jq -r '.session_id')

# Step 3: Have a conversation (3 messages)
curl -X POST "http://localhost:8000/api/v1/conversation/$SESSION_ID/message" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "journey_user_1", "message": "Hola"}'

curl -X POST "http://localhost:8000/api/v1/conversation/$SESSION_ID/message" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "journey_user_1", "message": "¿Cómo estás?"}'

curl -X POST "http://localhost:8000/api/v1/conversation/$SESSION_ID/message" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "journey_user_1", "message": "Muy bien, gracias"}'

# Step 4: Practice vocabulary (5 flashcards)
for i in {1..5}; do
  FLASHCARD=$(curl "http://localhost:8000/api/v1/vocabulary/next?user_id=journey_user_1&target_language=Spanish&level=A1")
  echo "Flashcard $i: $FLASHCARD"

  # Submit answer (alternate correct/incorrect)
  if [ $((i % 2)) -eq 0 ]; then
    SELECTED=0  # Correct
  else
    SELECTED=1  # Incorrect
  fi

  WORD=$(echo $FLASHCARD | jq -r '.word')
  CORRECT=$(echo $FLASHCARD | jq -r '.correct_option_index')

  curl -X POST "http://localhost:8000/api/v1/vocabulary/answer" \
    -H "Content-Type: application/json" \
    -d "{
      \"user_id\": \"journey_user_1\",
      \"word\": \"$WORD\",
      \"selected_option_index\": $SELECTED,
      \"correct_option_index\": $CORRECT
    }"
done

# Step 5: Practice grammar (3 questions)
for i in {1..3}; do
  QUESTION=$(curl "http://localhost:8000/api/v1/grammar/question?user_id=journey_user_1&target_language=Spanish&level=A1")
  echo "Question $i: $QUESTION"

  QUESTION_ID=$(echo $QUESTION | jq -r '.question_id')
  CORRECT=$(echo $QUESTION | jq -r '.correct_option_index')
  EXPLANATION=$(echo $QUESTION | jq -r '.explanation')

  # Submit answer (all correct)
  curl -X POST "http://localhost:8000/api/v1/grammar/answer" \
    -H "Content-Type: application/json" \
    -d "{
      \"user_id\": \"journey_user_1\",
      \"question_id\": \"$QUESTION_ID\",
      \"selected_option_index\": $CORRECT,
      \"correct_option_index\": $CORRECT,
      \"explanation\": \"$EXPLANATION\"
    }"
done

# Step 6: Get writing feedback
curl -X POST "http://localhost:8000/api/v1/writing/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "journey_user_1",
    "target_language": "Spanish",
    "level": "A1",
    "text": "Me llamo Juan. Tengo veinte años. Vivo en Madrid."
  }'

# Step 7: Check final progress
curl "http://localhost:8000/api/v1/users/journey_user_1/progress"
```

**✅ Success Criteria:**
- All requests succeed
- Progress shows activity in all modules
- Vocabulary score reflects 2/5 correct (40%)
- Grammar score reflects 3/3 correct (100%)
- Writing score is reasonable
- Conversation shows attempts

---

### Test 10.2: Multi-Language User

**Purpose:** Test user learning multiple languages

```bash
# User learns Spanish
curl "http://localhost:8000/api/v1/vocabulary/next?user_id=multi_lang_user&target_language=Spanish&level=A1"

# Same user learns French
curl "http://localhost:8000/api/v1/vocabulary/next?user_id=multi_lang_user&target_language=French&level=A1"

# Same user learns German
curl "http://localhost:8000/api/v1/vocabulary/next?user_id=multi_lang_user&target_language=German&level=A1"
```

**✅ Success Criteria:**
- All requests succeed
- Content is in correct language
- Progress tracked separately (though current implementation doesn't separate by language in progress)

---

## Troubleshooting

### Issue: "Connection refused"

**Cause:** Server not running

**Solution:**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

---

### Issue: "LLM API Error"

**Cause:** Invalid or missing API key

**Solution:**
1. Check `.env` file has valid `LLM_API_KEY`
2. Verify API key at https://makersuite.google.com/app/apikey
3. Restart server after updating `.env`

---

### Issue: "Database connection error"

**Cause:** PostgreSQL not running or wrong credentials

**Solution:**
```bash
# Check if PostgreSQL is running
pg_isready

# Start PostgreSQL (macOS)
brew services start postgresql

# Check database exists
psql -l | grep language_app

# Create if missing
createdb language_app
```

---

### Issue: "422 Unprocessable Entity"

**Cause:** Missing required fields or wrong data types

**Solution:**
- Check Swagger UI docs for exact field requirements
- Ensure all required fields are included
- Check data types (strings, integers, etc.)

---

### Issue: "Slow response times"

**Cause:** LLM API calls take time

**Solution:**
- Normal response time: 2-5 seconds for LLM calls
- STT calls: 5-10 seconds
- If > 30 seconds, check network connection

---

### Issue: "Empty or null responses"

**Cause:** LLM parsing failed

**Solution:**
- Check server logs for JSON parsing errors
- LLM sometimes returns markdown-wrapped JSON
- Code handles this, but check logs if issues persist

---

## Testing Checklist

Use this checklist to verify all features:

### Basic Features
- [ ] Health check returns OK
- [ ] User creation works
- [ ] User retrieval works
- [ ] Duplicate user prevention works

### Conversation Module
- [ ] Can start conversation session
- [ ] Opening message is in target language
- [ ] Can send messages in session
- [ ] Receives contextual replies
- [ ] Gets corrections when needed
- [ ] Gets helpful tips
- [ ] Context is maintained across messages

### Vocabulary Module
- [ ] Can get flashcards
- [ ] Flashcards have all required fields
- [ ] Options are plausible
- [ ] Can submit correct answers
- [ ] Can submit incorrect answers
- [ ] Works with multiple languages
- [ ] Different flashcards each time

### Grammar Module
- [ ] Can get grammar questions
- [ ] Questions match specified topic
- [ ] Questions match difficulty level
- [ ] Can submit correct answers
- [ ] Can submit incorrect answers
- [ ] Explanations are provided
- [ ] Works with multiple languages

### Writing Module
- [ ] Can get feedback on text
- [ ] Identifies errors correctly
- [ ] Provides corrections
- [ ] Gives helpful comments
- [ ] Score is reasonable
- [ ] Works with different languages

### Phonetics Module
- [ ] Can upload audio file
- [ ] Gets transcription
- [ ] Receives pronunciation score
- [ ] Gets helpful feedback
- [ ] Works with different languages
- [ ] Handles different audio formats

### Progress Tracking
- [ ] Progress is recorded for each module
- [ ] Attempt counts are correct
- [ ] Scores are calculated correctly
- [ ] Can retrieve user progress

### Error Handling
- [ ] Invalid user IDs return 404
- [ ] Missing fields return 422
- [ ] Invalid session IDs handled gracefully
- [ ] LLM errors return 500 with message

---

## Performance Benchmarks

### Expected Response Times

| Endpoint | Expected Time | Acceptable Max |
|----------|---------------|----------------|
| Health check | < 100ms | 500ms |
| User creation | < 200ms | 1s |
| Start conversation | 2-5s | 10s |
| Send message | 2-5s | 10s |
| Get flashcard | 2-5s | 10s |
| Get grammar question | 2-5s | 10s |
| Writing feedback | 3-6s | 15s |
| Pronunciation eval | 5-10s | 20s |

---

## Automated Testing Script

Save this as `test_all.sh`:

```bash
#!/bin/bash

BASE_URL="http://localhost:8000/api/v1"
USER_ID="auto_test_user_$(date +%s)"

echo "🧪 Starting Automated Backend Tests"
echo "===================================="
echo ""

# Test 1: Health Check
echo "✓ Testing health check..."
curl -s "$BASE_URL/health" | grep -q "ok" && echo "  PASS" || echo "  FAIL"

# Test 2: Create User
echo "✓ Creating test user..."
curl -s -X POST "$BASE_URL/users" \
  -H "Content-Type: application/json" \
  -d "{\"external_id\": \"$USER_ID\", \"target_language\": \"Spanish\", \"level\": \"A2\"}" \
  | grep -q "$USER_ID" && echo "  PASS" || echo "  FAIL"

# Test 3: Start Conversation
echo "✓ Starting conversation..."
SESSION_ID=$(curl -s -X POST "$BASE_URL/conversation/start" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\": \"$USER_ID\", \"target_language\": \"Spanish\", \"level\": \"A2\"}" \
  | jq -r '.session_id')
[ ! -z "$SESSION_ID" ] && echo "  PASS (Session: $SESSION_ID)" || echo "  FAIL"

# Test 4: Get Flashcard
echo "✓ Getting vocabulary flashcard..."
curl -s "$BASE_URL/vocabulary/next?user_id=$USER_ID&target_language=Spanish&level=A2" \
  | grep -q "word" && echo "  PASS" || echo "  FAIL"

# Test 5: Get Grammar Question
echo "✓ Getting grammar question..."
curl -s "$BASE_URL/grammar/question?user_id=$USER_ID&target_language=Spanish&level=A2" \
  | grep -q "question_text" && echo "  PASS" || echo "  FAIL"

# Test 6: Get Writing Feedback
echo "✓ Getting writing feedback..."
curl -s -X POST "$BASE_URL/writing/feedback" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\": \"$USER_ID\", \"target_language\": \"Spanish\", \"level\": \"A2\", \"text\": \"Hola mundo\"}" \
  | grep -q "score" && echo "  PASS" || echo "  FAIL"

# Test 7: Check Progress
echo "✓ Checking user progress..."
curl -s "$BASE_URL/users/$USER_ID/progress" \
  | grep -q "module" && echo "  PASS" || echo "  FAIL"

echo ""
echo "===================================="
echo "🎉 Automated tests complete!"
```

**Run automated tests:**
```bash
chmod +x test_all.sh
./test_all.sh
```

---

## Summary

This testing guide covers:
- ✅ All 5 learning modules
- ✅ User management
- ✅ Progress tracking
- ✅ Error handling
- ✅ Multiple languages
- ✅ Integration scenarios
- ✅ Performance benchmarks
- ✅ Automated testing

**Next Steps:**
1. Run through each test section
2. Document any failures
3. Verify all features work as expected
4. Use automated script for regression testing
5. Add tests to CI/CD pipeline (future)

---

**Happy Testing! 🚀**
