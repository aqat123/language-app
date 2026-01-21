# Simple Web Interface

A clean, simple web interface to test your Language Learning Backend.

## 🚀 How to Use

1. **Make sure your backend is running:**
   ```bash
   cd ../backend
   source venv/bin/activate
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Open the web interface:**
   ```bash
   # Option 1: Just double-click index.html in Finder
   
   # Option 2: Use a simple HTTP server
   python3 -m http.server 8080
   # Then open: http://localhost:8080
   ```

3. **Start Learning:**
   - Enter your name
   - Choose a language (Spanish, French, etc.)
   - Select your level (A1-B2)
   - Click "Start Learning"
   - Choose a module and start practicing!

## ✨ Features

- 📚 **Vocabulary**: Flashcards with multiple choice
- 💬 **Conversation**: Real-time AI chat tutor
- 📖 **Grammar**: Interactive grammar exercises
- ✍️ **Writing**: Get AI feedback on your writing
- 📊 **Progress**: Track your learning progress

## 🎨 Modules

### Vocabulary
- AI-generated flashcards
- Multiple choice questions
- Instant feedback
- Progress tracking

### Conversation
- Start a conversation with AI tutor
- Real-time responses
- Grammar corrections
- Natural language practice

### Grammar
- Dynamic grammar questions
- Multiple choice format
- Detailed explanations
- Adaptive difficulty

### Writing
- Submit your writing
- Get corrections
- Detailed feedback
- Scoring system

## 🛠️ Technical Details

- Pure HTML/CSS/JavaScript (no frameworks)
- Connects to backend at `http://localhost:8000/api/v1`
- Responsive design
- Modern gradient UI

## 📝 Notes

- Backend must be running on port 8000
- CORS is already enabled in your backend
- All AI features work (vocabulary, conversation, grammar, writing)
- Progress is saved to database

## 🎯 Next Steps

This is a simple demo interface. For production:
- Add authentication
- Better error handling
- Loading states
- Offline mode
- Mobile optimization
