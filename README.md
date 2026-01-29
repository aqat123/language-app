# Language Learning Application

An AI-powered language learning platform that provides interactive exercises across five learning modules: Conversation, Vocabulary, Grammar, Writing, and Phonetics.

## Overview

This application combines artificial intelligence with pedagogically sound teaching methods to help learners practice language skills through real-world scenarios and adaptive exercises.

## Learning Modules

### 💬 Conversation Module

Interactive dialogue-based learning with an AI tutor. Students practice real-world conversations on topics such as ordering food, booking travel, or shopping. The system provides context-aware responses, corrects grammar in real-time, and offers pronunciation guidance through transcription feedback.

### 📚 Vocabulary Module

AI-generated flashcard system with adaptive difficulty levels. Each flashcard presents a word in the target language, provides an English definition, includes an example sentence in context, and offers multiple-choice options. The system tracks mastery and adjusts difficulty based on student performance.

### 📖 Grammar Module

Dynamic grammar exercises with topic-based question generation. Students answer multiple-choice questions covering grammar concepts appropriate to their proficiency level. The system explains errors and provides detailed feedback on rule violations.

### ✏️ Writing Module

Composition feedback system with detailed corrections and explanations. Students submit written text and receive grammatical corrections, stylistic suggestions, and inline explanations of errors. The feedback helps students identify patterns in their writing mistakes.

### 🎤 Phonetics Module

Pronunciation evaluation through speech-to-text analysis. Students practice target phrases by recording audio. The system transcribes speech, compares it to the target, and provides detailed pronunciation feedback on vowel sounds, stress patterns, and overall clarity.

## Core Features

- AI-powered content generation using Google Gemini API
- Generate-then-Verify pattern ensuring educational content accuracy
- Comprehensive progress tracking across all modules
- Multi-language support with adaptive difficulty levels
- User progress persistence in PostgreSQL database
- Speech-to-text integration for pronunciation evaluation
- Content logging for continuous improvement
- RESTful API for seamless frontend-backend communication

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Backend Framework | FastAPI | 0.124.0 |
| Python Version | Python | 3.11+ |
| ORM | SQLAlchemy | 2.0.35 |
| Database | PostgreSQL | 12+ |
| Validation | Pydantic | 2.12.5 |
| HTTP Client | httpx | 0.27.0 |
| Server | Uvicorn | 0.38.0 |
| LLM Service | Google Gemini API | Latest |
| Speech Service | Google Cloud Speech-to-Text | Latest |

## Project Structure

```
language-app/
├── README.md                 (this file)
├── SETUP.md                  (installation guide)
├── ARCHITECTURE.md           (system design)
├── API.md                    (API reference)
├── TESTING.md                (testing guide)
├── HOW_IT_WORKS.md           (detailed walkthrough)
├── backend/                  (FastAPI backend)
│   ├── app/
│   │   ├── api/v1/          (REST endpoints)
│   │   ├── services/        (business logic)
│   │   ├── db/              (database layer)
│   │   ├── schemas/         (data models)
│   │   └── core/            (configuration)
│   └── requirements.txt
└── simple-web-interface/     (web interface)
    ├── index.html
    ├── app.js
    └── styles.css
```

## Getting Started

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 12 or higher
- Google Gemini API key
- Google Cloud Speech-to-Text API key
- Basic command-line knowledge

### Quick Start

1. **Follow the setup guide**

   See [SETUP.md](SETUP.md) for detailed installation and configuration instructions (30-45 minutes).

2. **Start the backend**

   ```bash
   cd backend
   source venv/bin/activate
   uvicorn main:app --reload
   ```

3. **Access the application**

   - Backend API: http://localhost:8000/api/v1/docs
   - Web Interface: http://localhost:8080

4. **Run tests**

   See [TESTING.md](TESTING.md) for comprehensive testing instructions.

## Documentation

- **[SETUP.md](SETUP.md)** - Complete installation and configuration guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design, data flow, and integration patterns
- **[API.md](API.md)** - Complete REST API reference documentation
- **[TESTING.md](TESTING.md)** - Testing strategies and comprehensive test examples
- **[HOW_IT_WORKS.md](HOW_IT_WORKS.md)** - Detailed technical walkthrough with concrete examples

## Use Case

The application serves as a learning platform for language students who want to practice speaking, reading, and writing in a foreign language. It provides immediate feedback on pronunciation, grammar, and vocabulary comprehension through AI-powered analysis.

## Target Audience

- Language learners of all proficiency levels (A1-C2)
- Self-paced learners seeking supplementary practice
- Classroom settings as a supplementary tool
- Developers learning full-stack AI application development

## Architecture at a Glance

```
┌─────────────────┐
│   Client Layer  │
│  (Web Browser)  │
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────────────────────┐
│    FastAPI Backend              │
│  ├─ API Endpoints               │
│  ├─ Service Layer               │
│  └─ AI Integration              │
└────┬─────────────────────┬──────┘
     │                     │
     ▼                     ▼
┌──────────────┐    ┌──────────────────┐
│ PostgreSQL   │    │ Google APIs      │
│ Database     │    │ ├─ Gemini LLM    │
└──────────────┘    │ └─ Speech-to-Text│
                    └──────────────────┘
```

## Key Features Implementation

### Generate-then-Verify Pattern

Educational quality is paramount. Every piece of AI-generated content undergoes rigorous validation:

1. **LLM Generation** - Google Gemini creates contextually appropriate content based on module requirements and learner proficiency
2. **Automated Validation** - A second AI validator checks for accuracy, pedagogical soundness, and cultural appropriateness
3. **Quality Assurance** - Only validated content is delivered to learners

This dual-verification approach ensures that every exercise, explanation, and feedback is educationally sound and factually correct.

### Adaptive Learning with Progress Tracking

The system learns alongside the learner:

- Real-time performance metrics across all modules
- Difficulty automatically adjusts based on success rate
- Detailed progress visualization showing growth over time
- Data-driven insights into learning patterns and weak areas

### Comprehensive Content Logging

Every interaction creates valuable learning data:

- All AI-generated content is permanently logged
- Student responses are recorded with outcomes
- Validation results tracked for continuous model improvement
- Historical data enables personalized learning recommendations

## Technical Highlights

- Type-safe codebase using Pydantic for validation
- Async/await patterns for non-blocking operations
- Clean separation of concerns (endpoints, services, database)
- Comprehensive error handling and validation
- Extensible module architecture
- Cross-platform compatibility (macOS, Linux, Windows)

## Related Documentation

For more detailed information:

- System architecture and data flows: See [ARCHITECTURE.md](ARCHITECTURE.md)
- API endpoint specifications: See [API.md](API.md)
- Testing procedures: See [TESTING.md](TESTING.md)
- Setup and installation: See [SETUP.md](SETUP.md)
- Technical walkthrough: See [HOW_IT_WORKS.md](HOW_IT_WORKS.md)

## Troubleshooting

Common issues and solutions are documented in:

- [SETUP.md](SETUP.md) - Setup-related issues
- [TESTING.md](TESTING.md) - Testing-related issues
- [ARCHITECTURE.md](ARCHITECTURE.md) - Design and integration questions

## Next Steps

1. Review the [SETUP.md](SETUP.md) guide for installation
2. Configure API keys as specified in setup guide
3. Initialize the database
4. Start the backend server
5. Explore the API using Swagger UI at http://localhost:8000/api/v1/docs
6. Run tests using [TESTING.md](TESTING.md) procedures
