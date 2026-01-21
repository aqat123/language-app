# How the Language Learning App Works

Complete technical breakdown of how a module executes from start to finish.

---

## 📚 Example: Vocabulary Module Execution

Let's trace exactly what happens when a user clicks "Vocabulary".

---

## Step-by-Step Execution Flow

### **1. User Clicks "Vocabulary" Button**

**In the browser (simple-web-interface/index.html):**
```html
<div class="module-card" onclick="startVocabulary()">
    <div class="module-icon">📚</div>
    <h3>Vocabulary</h3>
    <p>Learn new words with flashcards</p>
</div>
```

---

### **2. JavaScript Function Runs**

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

---

### **3. HTTP Request Goes to Backend**

**Request Details:**
```http
GET http://localhost:8000/api/v1/vocabulary/next?user_id=maria&target_language=Spanish&level=A1
```

**Query Parameters:**
- `user_id`: "maria"
- `target_language`: "Spanish"
- `level`: "A1"

---

### **4. Backend Receives Request**

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

---

### **5. Service Layer Generates Content**

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

---

### **6. Gemini AI Processes Request**

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

---

### **7. Response Travels Back to Web App**

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

---

### **8. JavaScript Displays the Flashcard**

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

---

### **9. User Sees This on Screen**

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

---

### **10. User Clicks "Cat" (Correct Answer)**

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

---

### **11. Backend Updates Progress**

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

---

### **12. Web Shows Feedback**

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

---

## 🔄 Complete Data Flow Diagram

```
┌──────────────┐
│   Browser    │  User clicks "Vocabulary"
│  (Web App)   │
└──────┬───────┘
       │ 1. JavaScript: startVocabulary()
       │
       ▼
┌──────────────┐
│ JavaScript   │  2. HTTP GET Request
│   app.js     │  → /api/v1/vocabulary/next
└──────┬───────┘
       │
       │ 3. Network Request
       ▼
┌──────────────┐
│   FastAPI    │  4. Route to endpoint
│   Backend    │  → vocabulary.py endpoint
└──────┬───────┘
       │
       │ 5. Call service function
       ▼
┌──────────────┐
│   Service    │  6. Create AI prompt
│ vocabulary.py│  7. Check/create user in DB
└──────┬───────┘
       │
       │ 8. HTTP POST to Gemini
       ▼
┌──────────────┐
│  Gemini AI   │  9. Process prompt
│ (Google)     │  10. Generate flashcard
└──────┬───────┘
       │
       │ 11. JSON response
       ▼
┌──────────────┐
│   Service    │  12. Validate content (checker AI)
│ vocabulary.py│  13. Save to content_logs table
│              │  14. Return FlashcardResponse
└──────┬───────┘
       │
       │ 15. HTTP Response (JSON)
       ▼
┌──────────────┐
│ JavaScript   │  16. Parse JSON
│   app.js     │  17. Update HTML/DOM
└──────┬───────┘
       │
       │ 18. Render UI
       ▼
┌──────────────┐
│   Browser    │  User sees flashcard
│   Display    │
└──────────────┘
       │
       │ 19. User clicks answer
       ▼
┌──────────────┐
│ JavaScript   │  20. HTTP POST to /vocabulary/answer
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Backend    │  21. Update user_progress table
│   Service    │  22. Calculate score
└──────┬───────┘
       │
       │ 23. Response: {is_correct: true}
       ▼
┌──────────────┐
│   Browser    │  24. Show feedback
│              │  ✅ Correct!
└──────────────┘
```

---

## ⏱️ Timeline (What Happens When)

```
Time   |  Component       |  Action
-------|------------------|------------------------------------------
0.0s   |  Browser         |  User clicks "Vocabulary" button
0.1s   |  JavaScript      |  Shows "Loading..." message
0.2s   |  JavaScript      |  Sends HTTP GET request to backend
       |                  |
0.3s   |  Backend API     |  Receives request
0.4s   |  Backend Service |  Creates AI prompt
0.5s   |  Backend Service |  Sends request to Gemini AI
       |                  |
0.5s   |  Gemini API      |  Receives request
1.5s   |  Gemini API      |  Processes prompt (AI inference)
2.0s   |  Gemini API      |  Returns JSON flashcard
       |                  |
2.1s   |  Backend Service |  Receives AI response
2.2s   |  Backend Service |  Validates content (checker)
2.3s   |  Backend Service |  Saves to content_logs table
2.4s   |  Backend API     |  Returns HTTP response
       |                  |
2.5s   |  JavaScript      |  Receives flashcard data
2.6s   |  JavaScript      |  Updates DOM (document.getElementById)
2.7s   |  Browser         |  Renders flashcard UI
2.8s   |  User            |  Sees flashcard with 4 options
       |                  |
-------|------------------|------------------------------------------
+5.0s  |  User            |  Clicks "Cat" option
+5.1s  |  JavaScript      |  Marks option as selected (green)
+5.2s  |  JavaScript      |  Sends POST to /vocabulary/answer
       |                  |
+5.3s  |  Backend Service |  Checks answer (correct!)
+5.4s  |  Backend Service |  Updates user_progress table
+5.5s  |  Backend Service |  Calculates new score (100%)
+5.6s  |  Backend API     |  Returns {is_correct: true}
       |                  |
+5.7s  |  JavaScript      |  Receives response
+5.8s  |  JavaScript      |  Shows "✅ Correct!" feedback
+5.9s  |  Browser         |  Displays success message
+6.0s  |  User            |  Sees feedback and "Next Word" button
```

---

## 📦 Database Storage

After this interaction, the following data is stored:

### **users Table**
```sql
id                              | external_id | target_language | level | created_at
--------------------------------|-------------|-----------------|-------|------------
abc-123-def-456...              | maria       | Spanish         | A1    | 2026-01-21...
```

### **user_progress Table**
```sql
id          | user_id     | module      | score | total_attempts | correct_attempts
------------|-------------|-------------|-------|----------------|------------------
xyz-789...  | abc-123...  | vocabulary  | 100.0 | 1              | 1
```

### **content_logs Table**
```sql
id          | user_id    | module     | generated_content                           | is_validated
------------|------------|------------|---------------------------------------------|-------------
qwe-456...  | abc-123... | vocabulary | {"word":"Gato","definition":"Cat",...}     | true
```

### **conversation_sessions Table**
```sql
(No entries yet - only used for Conversation module)
```

---

## 🔁 Same Pattern for All Modules

All modules follow the same pattern:

### **Conversation Module**
```
User types message → Backend → Gemini generates reply → Display chat
```

### **Grammar Module**
```
User requests question → Backend → Gemini generates MCQ → User answers → Score updated
```

### **Writing Module**
```
User submits text → Backend → Gemini checks grammar → Returns corrections → Display feedback
```

### **Phonetics Module** (Not tested - needs STT API)
```
User records audio → Backend → Google STT → Compare to target → Score pronunciation
```

---

## 🧩 Key Components

### **Frontend (simple-web-interface/)**
- `index.html` - UI structure
- `styles.css` - Visual design
- `app.js` - Business logic, API calls

### **Backend (backend/)**
- `app/api/v1/endpoints/` - HTTP routes
- `app/services/` - Business logic, AI integration
- `app/db/models.py` - Database schema
- `app/core/config.py` - Configuration

### **Database**
- `test_language_app.db` - SQLite file (52KB)
- Stores: users, progress, AI content, conversations

### **External Services**
- **Gemini AI** - Content generation
- **Google Cloud STT** - Speech recognition (not configured)

---

## 📊 Request/Response Examples

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

## 🎯 Summary

**One complete vocabulary interaction involves:**

1. ✅ User clicks button
2. ✅ JavaScript makes API call
3. ✅ Backend creates prompt
4. ✅ Gemini AI generates content (~2 seconds)
5. ✅ Content is validated
6. ✅ Data saved to database
7. ✅ Response sent to frontend
8. ✅ UI updated with flashcard
9. ✅ User selects answer
10. ✅ Answer sent to backend
11. ✅ Progress updated in database
12. ✅ Feedback displayed

**Total time:** ~3 seconds  
**Database writes:** 2 (content_log, user_progress)  
**AI API calls:** 1 (or 2 if checker is called)  
**HTTP requests:** 2 (GET flashcard, POST answer)

---

**This same flow applies to all 7 learning modules!** 🚀
