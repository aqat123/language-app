# Simple Web Interface

A lightweight, vanilla JavaScript web interface for testing and demonstrating the Language Learning Backend. This is a **demo interface** designed for development and testing—not production use.

---

## Quick Start

### Prerequisites
- Backend running on `http://localhost:8000` (see [../../SETUP.md](../../SETUP.md))
- Modern web browser (Chrome, Firefox, Safari, Edge)
- No dependencies or build tools required

### Running the Frontend

**Option 1: Direct File Access**
```bash
# Just double-click index.html in Finder, or:
open simple-web-interface/index.html
```

**Option 2: HTTP Server (Recommended)**
```bash
cd simple-web-interface
python3 -m http.server 8080
# Then open: http://localhost:8080
```

**Option 3: Node.js HTTP Server**
```bash
cd simple-web-interface
npx http-server -p 8080
# Then open: http://localhost:8080
```

### Using the App
1. Enter a username (or choose existing user ID)
2. Select target language (Spanish, French, German, etc.)
3. Choose proficiency level (A1-B2)
4. Click "Start Learning"
5. Choose a learning module and begin practicing

---

## Project Structure

### `index.html`
- Single-page application HTML skeleton
- Sections for user registration and five learning modules
- All interactive elements have `id` attributes for JavaScript targeting
- Uses semantic HTML with accessibility in mind

### `app.js` (822 lines)
- **Core Logic**: User registration, session management, state tracking
- **Module Handlers**: One function set per learning module (vocabulary, conversation, grammar, writing, phonetics)
- **API Communication**: All requests use async/await pattern to `http://localhost:8000/api/v1`
- **UI Utilities**: Section switching, error display, loading states
- **Global State**: User info, current lesson data, audio recording state

**Global Variables:**
- `currentUser` – logged-in user (id, language, level)
- `currentFlashcard` – active vocabulary word
- `currentConversationId` – chat session identifier
- `currentGrammarQuestion` – active grammar exercise
- `mediaRecorder`, `audioChunks`, `audioBlob` – audio recording state

### `styles.css`
- Responsive grid layout (desktop/mobile)
- Gradient UI with modern color scheme
- Module-specific styling (cards, options, chat bubbles)
- Loading spinners, error states, feedback highlights

---

## Modules Implementation

### Vocabulary Module
Displays AI-generated flashcards with multiple-choice answers. User sees the word, example sentence, and four options. Upon selection, the frontend sends the answer to the backend for evaluation, receives correctness feedback, and pre-loads the next flashcard in the background for smooth experience. Includes optional AI-generated image display for visual memory aid.

**Flow:**
1. `loadNextWord()` → fetches next flashcard
2. `displayFlashcard()` → renders word, sentence, and options
3. `selectOption()` → sends answer, displays visual feedback (green/red highlight)
4. `preloadNextFlashcard()` → background fetch for speed
5. Loop back to step 1

### Conversation Module
Chat interface for real-time conversation with an AI language tutor. User enters messages, backend processes them through the tutor system prompt, and returns responses with optional grammar corrections and teaching tips. Messages display as chat bubbles (user left, AI right). Supports multi-turn conversations within a session.

**Flow:**
1. `startConversation()` → initializes session, displays opening message
2. `sendMessage()` → user types message, presses Enter
3. Message sent to `/conversation/chat` endpoint with session ID
4. Backend returns tutor response + optional corrections
5. Messages appended to chat container
6. User can continue typing

### Grammar Module
Interactive grammar exercise with multiple-choice format. Backend generates a grammar question with context, options, and correct answer. User selects an option, frontend highlights correctness, and displays detailed explanation. Questions adapt to user's language level.

**Flow:**
1. `loadGrammarQuestion()` → fetches question with options and explanation
2. `displayGrammarQuestion()` → renders formatted question
3. `selectGrammarOption()` → shows correctness, displays explanation
4. Explanation fetched from backend and displayed with styling
5. "Next Question" button available for continuation

### Writing Module
User submits a written passage in their target language. Backend analyzes it, returns corrections, and provides structured feedback (grammar issues, vocabulary suggestions, style notes). Each feedback item includes severity level and explanation.

**Flow:**
1. `submitWriting()` → sends text to `/writing/analyze` endpoint
2. User sees corrected version displayed clearly
3. Feedback items listed with icons/colors by type
4. User can submit another piece of writing

### Phonetics Module
Audio-based pronunciation practice. User records themselves speaking a target phrase, backend performs speech-to-text transcription, compares with target, and provides pronunciation score (0-100) plus feedback tips (rhythm, intonation, clarity).

**Flow:**
1. `loadPhoneticsPractice()` → fetches target phrase
2. `startRecording()` → activates microphone, captures audio chunks
3. `stopRecording()` → stops recording, sends audio blob to backend
4. `submitPhoneticsPractice()` → backend transcribes + scores pronunciation
5. Results display: transcript, score, and feedback tips

---

## API Integration

### Base URL Configuration
```javascript
const API_BASE_URL = 'http://localhost:8000/api/v1';
```
All requests target this endpoint. For local testing, no changes needed. For deployment, update this constant.

### Authentication
Currently **no authentication required**—requests include `user_id` as a query parameter or in request body. For production, update to use JWT tokens in Authorization header.

### Request Pattern
```javascript
const response = await fetch(`${API_BASE_URL}/endpoint`, {
    method: 'POST',  // or GET
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id, language, level, ... })
});

if (!response.ok) throw new Error('Request failed');
const data = await response.json();
```

### Error Handling
- Network errors caught in try/catch blocks
- HTTP errors checked via `response.ok`
- User-facing errors displayed via `showError()` or in UI sections
- Backend error messages passed directly to user where helpful

### Common Endpoints Used
| Module | Endpoint | Method |
|--------|----------|--------|
| Vocabulary | `/vocabulary/next` | GET |
| Vocabulary | `/vocabulary/evaluate` | POST |
| Conversation | `/conversation/start` | POST |
| Conversation | `/conversation/chat` | POST |
| Grammar | `/grammar/next-question` | GET |
| Writing | `/writing/analyze` | POST |
| Phonetics | `/phonetics/practice` | GET |
| Phonetics | `/phonetics/submit` | POST |

See [../../API.md](../../API.md) for complete endpoint reference.

---

## Frontend Features

### Section Navigation
JavaScript uses `showSection()` to switch between modules. HTML sections marked with class `section` and `id` attributes. Only one section visible at a time (others have `hidden` class).

### Loading States
All async operations display "Loading..." message in target container. Prevents user interaction while waiting for backend response.

### Error Messages
Errors displayed via:
- `alert()` popup for critical issues (via `showError()`)
- Inline error text within sections for recoverable errors
- Console logs for debugging (developer tools)

### State Management
Global variables track:
- Current user profile (language, level, ID)
- Active lesson data (flashcard, grammar question, conversation ID)
- Recording state (MediaRecorder, audio chunks, blob)
- Pre-loaded data for performance (next flashcard promise)

### Asynchronous Operations
All API calls use modern async/await syntax:
```javascript
async function loadData() {
    try {
        const response = await fetch(url);
        const data = await response.json();
        // update UI
    } catch (error) {
        showError(error.message);
    }
}
```

### Responsive Design
CSS uses flexbox and grid layouts. Adapts to mobile, tablet, and desktop viewports. Gradient backgrounds, rounded corners, and shadows for modern appearance.

---

## Development Notes

### Dependencies
**None.** This is vanilla JavaScript, HTML, and CSS. No frameworks, libraries, or build tools required.

### Browser Compatibility
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

Requires:
- `fetch()` API for HTTP requests
- `async/await` syntax support
- MediaRecorder API for audio (Phonetics module only)
- `XMLHttpRequest` polyfill not needed

### CORS Requirements
Backend must enable CORS headers for cross-origin requests from `http://localhost:8080` (or deployment domain):
```
Access-Control-Allow-Origin: http://localhost:8080
Access-Control-Allow-Methods: GET, POST
Access-Control-Allow-Headers: Content-Type
```
Backend starter code includes `FastAPI CORS middleware` with `allow_origins=["*"]`.

### Testing with Backend

**Checklist:**
- ✅ Backend running on `http://localhost:8000`
- ✅ Frontend accessible on `http://localhost:8080`
- ✅ Registration succeeds (user ID stored in `currentUser`)
- ✅ Vocabulary: word loads, options clickable, feedback displays
- ✅ Conversation: opening message appears, chat input works
- ✅ Grammar: question loads, options clickable
- ✅ Writing: text submission works, feedback displays
- ✅ Phonetics: audio recording activates, submission works
- ✅ Browser console shows no errors (F12 → Console tab)

**Manual Test Flow:**
```javascript
// In browser console:
console.log(currentUser);  // See current user
console.log(currentFlashcard);  // See current word
console.log(currentConversationId);  // See chat session
```

---

## Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| "Error: Failed to fetch" | Backend not running or wrong URL | Start backend on port 8000; check `API_BASE_URL` |
| CORS error | Missing backend CORS config | Add `CORSMiddleware` to `main.py` |
| Blank page | Missing `index.html` or browser not served | Use HTTP server, not `file://` protocol |
| Audio not working | Browser permission denied | Allow microphone access; try Chrome |
| Slow flashcard loading | Pre-load not triggering | Check browser console for fetch errors |
| Input fields not responding | CSS `pointer-events: none` set | Check that options are re-enabled after selection |

---

## Architecture Overview

For system-wide architecture, execution flow, and technology stack details, see [../../ARCHITECTURE.md](../../ARCHITECTURE.md).

This frontend is the **HTTP Client Layer** in the full stack:
```
[HTML/CSS/JS Frontend] ←→ (HTTP) ←→ [FastAPI Backend] ←→ [Gemini API + Database]
```

The backend handles all business logic, AI calls, and data persistence. This frontend is stateless except for the current user session.

---