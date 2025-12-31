# Further Steps - Complete Setup Guide

This guide walks you through **everything you need to do** to get the Language Learning Backend up and running, from getting API keys to running your first test.

## 📋 Table of Contents

- [Overview](#overview)
- [Step 1: Get API Keys](#step-1-get-api-keys)
- [Step 2: Install PostgreSQL](#step-2-install-postgresql)
- [Step 3: Set Up Python Environment](#step-3-set-up-python-environment)
- [Step 4: Configure Environment Variables](#step-4-configure-environment-variables)
- [Step 5: Initialize Database](#step-5-initialize-database)
- [Step 6: Run the Backend](#step-6-run-the-backend)
- [Step 7: Test Your Setup](#step-7-test-your-setup)
- [Step 8: Next Steps](#step-8-next-steps)
- [Troubleshooting](#troubleshooting)

---

## Overview

### What You'll Need:

- ⏱️ **Time Required:** 30-45 minutes
- 💻 **Skills:** Basic command line knowledge
- 💰 **Cost:** Free (using free tiers of Google APIs)

### What You'll Accomplish:

By the end of this guide, you'll have:
- ✅ A fully functional FastAPI backend
- ✅ PostgreSQL database configured
- ✅ AI services (Gemini LLM + Speech-to-Text) connected
- ✅ Interactive API documentation at your fingertips
- ✅ A working language learning platform backend

---

## Step 1: Get API Keys

You need **two API keys** to run this backend:

### 1.1 Google Gemini API Key (for AI Language Generation)

**What it does:** Powers all AI features - conversations, flashcards, grammar questions, writing feedback

**How to get it (FREE):**

1. **Go to Google AI Studio:**
   - Open: https://makersuite.google.com/app/apikey
   - Sign in with your Google account

2. **Create API Key:**
   - Click "**Create API Key**" button
   - You'll see a dialog with options
   - Click "**Create API key in new project**" (easiest option)

3. **Copy Your Key:**
   - Copy the API key that appears (looks like: `AIzaSy...`)
   - ⚠️ **IMPORTANT:** Save this somewhere safe! You'll need it in Step 4

4. **Verify it works (Optional):**
   ```bash
   curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=YOUR_API_KEY" \
     -H 'Content-Type: application/json' \
     -d '{"contents":[{"parts":[{"text":"Hello"}]}]}'
   ```
   - Replace `YOUR_API_KEY` with your actual key
   - If you get a JSON response, it works! ✅

**📝 Save for later:**
```
LLM_API_KEY=AIzaSy...your-key-here...
```

---

### 1.2 Google Cloud Speech-to-Text API Key (for Pronunciation)

**What it does:** Converts user speech to text for pronunciation evaluation

**How to get it (FREE tier available):**

1. **Go to Google Cloud Console:**
   - Open: https://console.cloud.google.com/
   - Sign in with your Google account

2. **Create a Project (if you don't have one):**
   - Click the project dropdown at the top
   - Click "**New Project**"
   - Name it: "Language Learning App"
   - Click "**Create**"

3. **Enable Speech-to-Text API:**
   - Go to: https://console.cloud.google.com/apis/library/speech.googleapis.com
   - Make sure your project is selected
   - Click "**Enable**" button
   - Wait for it to enable (~30 seconds)

4. **Create API Credentials:**
   - Go to: https://console.cloud.google.com/apis/credentials
   - Click "**+ Create Credentials**" at the top
   - Select "**API key**"
   - Copy the API key that appears
   - Click "**Restrict Key**" (recommended for security)

5. **Restrict Your Key (Optional but Recommended):**
   - Under "API restrictions", select "Restrict key"
   - Find and check "Cloud Speech-to-Text API"
   - Click "Save"

6. **Verify it works (Optional):**
   ```bash
   # Test with a simple request
   curl -X POST "https://speech.googleapis.com/v1/speech:recognize?key=YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "config": {
         "encoding": "LINEAR16",
         "sampleRateHertz": 16000,
         "languageCode": "en-US"
       },
       "audio": {
         "content": "//base64_audio_content//"
       }
     }'
   ```

**📝 Save for later:**
```
STT_API_KEY=AIzaSy...your-key-here...
```

---

### 1.3 API Keys Checklist

Before proceeding, make sure you have:
- [ ] Gemini API key saved
- [ ] Speech-to-Text API key saved
- [ ] Both keys tested and working

---

## Step 2: Install PostgreSQL

### 2.1 Why PostgreSQL?

PostgreSQL is the database that stores:
- User information and progress
- Conversation history
- All generated content logs

### 2.2 Installation by Operating System

#### **macOS (Using Homebrew)**

```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install PostgreSQL
brew install postgresql@15

# Start PostgreSQL service
brew services start postgresql@15

# Verify it's running
pg_isready
```

**Expected output:** `accepting connections`

---

#### **Ubuntu/Debian Linux**

```bash
# Update package list
sudo apt update

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Verify it's running
sudo systemctl status postgresql
```

---

#### **Windows**

1. **Download PostgreSQL:**
   - Go to: https://www.postgresql.org/download/windows/
   - Click "Download the installer"
   - Download version 15.x

2. **Run the installer:**
   - Run the downloaded .exe file
   - Click "Next" through the setup
   - **Remember the password** you set for the `postgres` user!
   - Keep default port: 5432
   - Click "Next" and "Finish"

3. **Verify installation:**
   - Open Command Prompt
   - Run: `psql --version`
   - Should show: `psql (PostgreSQL) 15.x`

---

### 2.3 Create Database

Once PostgreSQL is installed and running:

#### **macOS/Linux:**

```bash
# Connect to PostgreSQL
psql postgres

# Inside psql prompt, create database:
CREATE DATABASE language_app;

# Create a user (optional, for production)
CREATE USER lang_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE language_app TO lang_user;

# Exit psql
\q
```

**Or use command line directly:**
```bash
createdb language_app
```

---

#### **Windows:**

```cmd
# Open SQL Shell (psql) from Start Menu
# When prompted:
# Server: localhost
# Database: postgres
# Port: 5432
# Username: postgres
# Password: [enter password you set during installation]

# Then create database:
CREATE DATABASE language_app;

# Exit
\q
```

---

### 2.4 Verify Database Creation

```bash
# List all databases
psql -l

# Or connect to it
psql language_app
```

You should see `language_app` in the list! ✅

---

### 2.5 Get Your Database URL

Your database URL will be one of these formats:

**Local development (default):**
```
postgresql://postgres:@localhost:5432/language_app
```

**With custom user/password:**
```
postgresql://lang_user:your_secure_password@localhost:5432/language_app
```

**Test connection:**
```bash
psql "postgresql://postgres:@localhost:5432/language_app"
```

If it connects, you're good! ✅

**📝 Save for later:**
```
DATABASE_URL=postgresql://postgres:@localhost:5432/language_app
```

---

## Step 3: Set Up Python Environment

### 3.1 Check Python Version

```bash
python3 --version
```

**Required:** Python 3.11 or higher

**If you need to install/update Python:**
- macOS: `brew install python@3.11`
- Ubuntu: `sudo apt install python3.11`
- Windows: Download from https://www.python.org/downloads/

---

### 3.2 Navigate to Backend Directory

```bash
cd /Users/aqilahmedabdulkhaliq/Downloads/language-app/backend
```

---

### 3.3 Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows
```

**You should see `(venv)` in your terminal prompt** ✅

---

### 3.4 Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt
```

**Expected output:** Installation of 20+ packages

**Verify installation:**
```bash
pip list
```

You should see:
- fastapi
- uvicorn
- sqlalchemy
- psycopg2-binary
- httpx
- pydantic
- And many more...

---

## Step 4: Configure Environment Variables

### 4.1 Create .env File

```bash
# Copy the example file
cp .env.example .env

# Open for editing
nano .env  # or use your preferred editor
```

---

### 4.2 Fill in Your Configuration

Edit `.env` file with your actual values:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:@localhost:5432/language_app

# LLM API Configuration (Google Gemini)
LLM_API_KEY=AIzaSy...your-gemini-key-here...
LLM_API_BASE_URL=https://generativelanguage.googleapis.com/v1beta
LLM_MODEL=gemini-1.5-flash

# Speech-to-Text API Configuration (Google Cloud)
STT_API_KEY=AIzaSy...your-stt-key-here...
STT_API_BASE_URL=https://speech.googleapis.com/v1

# Application Configuration
ENV=dev
DEBUG=True
API_V1_PREFIX=/api/v1
PROJECT_NAME=Language Learning Backend

# CORS Configuration
BACKEND_CORS_ORIGINS=*
```

---

### 4.3 What Each Variable Means

| Variable | What It Is | Where You Got It |
|----------|------------|------------------|
| `DATABASE_URL` | PostgreSQL connection string | Step 2.5 |
| `LLM_API_KEY` | Google Gemini API key | Step 1.1 |
| `STT_API_KEY` | Google Speech-to-Text key | Step 1.2 |
| `LLM_API_BASE_URL` | Gemini API endpoint | Keep as-is |
| `STT_API_BASE_URL` | Speech API endpoint | Keep as-is |
| `LLM_MODEL` | Which Gemini model to use | Keep as-is |
| `ENV` | Environment (dev/prod) | Keep as dev |
| `DEBUG` | Enable debug mode | Keep as True |
| `API_V1_PREFIX` | API URL prefix | Keep as-is |
| `BACKEND_CORS_ORIGINS` | Allowed origins | * = allow all (dev only) |

---

### 4.4 Verify Your .env File

```bash
# Check file exists and has content
cat .env

# Make sure no trailing spaces or quotes around values
```

**✅ Checklist:**
- [ ] `.env` file exists in `backend/` directory
- [ ] `DATABASE_URL` points to your local database
- [ ] `LLM_API_KEY` is your actual Gemini key (starts with AIza...)
- [ ] `STT_API_KEY` is your actual Speech key (starts with AIza...)
- [ ] No extra quotes around values
- [ ] No trailing whitespace

---

## Step 5: Initialize Database

### 5.1 Understanding Database Initialization

When you first run the backend, it will automatically:
- Connect to PostgreSQL
- Create all necessary tables (users, user_progress, conversation_sessions, content_logs)
- Set up relationships between tables

**You don't need to manually create tables!** SQLAlchemy does this automatically.

---

### 5.2 Test Database Connection

Before running the server, let's verify the database connection:

```bash
# Make sure you're in the backend directory with venv activated
cd /Users/aqilahmedabdulkhaliq/Downloads/language-app/backend
source venv/bin/activate

# Test connection with Python
python3 -c "
from app.db.database import engine
from app.db.models import Base
try:
    Base.metadata.create_all(bind=engine)
    print('✅ Database connection successful!')
    print('✅ Tables created!')
except Exception as e:
    print(f'❌ Database error: {e}')
"
```

**Expected output:**
```
✅ Database connection successful!
✅ Tables created!
```

---

### 5.3 Verify Tables Were Created

```bash
# Connect to database
psql language_app

# List tables
\dt

# You should see:
# - users
# - user_progress
# - conversation_sessions
# - content_logs

# Exit
\q
```

---

## Step 6: Run the Backend

### 6.1 Start the Server

```bash
# Make sure you're in backend directory with venv activated
cd /Users/aqilahmedabdulkhaliq/Downloads/language-app/backend
source venv/bin/activate

# Run the server
uvicorn main:app --reload
```

**Expected output:**
```
INFO:     Will watch for changes in these directories: ['/Users/.../backend']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**✅ Success indicators:**
- No errors in the output
- Says "Application startup complete"
- Server is running on http://127.0.0.1:8000

---

### 6.2 Understand What Just Happened

When you started the server:

1. **FastAPI loaded** - Your web framework initialized
2. **Configuration loaded** - `.env` file was read
3. **Database connected** - Connection to PostgreSQL established
4. **Tables created** - All models were synced to database
5. **Routes registered** - All API endpoints are now active
6. **Server listening** - Ready to receive requests

---

### 6.3 Access the API

**Your server is now running at these URLs:**

| URL | What It Is |
|-----|------------|
| http://localhost:8000 | Root endpoint |
| http://localhost:8000/api/v1/health | Health check |
| http://localhost:8000/api/v1/docs | **Interactive API documentation** |
| http://localhost:8000/api/v1/redoc | Alternative documentation |

---

## Step 7: Test Your Setup

### 7.1 Quick Browser Test

**Open your browser and go to:**
```
http://localhost:8000/api/v1/docs
```

**You should see:**
- Swagger UI interface
- List of all API endpoints
- Green "Authorize" button
- Multiple sections: health, auth, conversation, vocabulary, grammar, writing, phonetics

**✅ If you see this, your backend is working!**

---

### 7.2 Test Health Endpoint

**In your browser:**
```
http://localhost:8000/api/v1/health
```

**Expected response:**
```json
{
  "status": "ok"
}
```

---

### 7.3 Test with curl

```bash
# Open a NEW terminal window (keep server running in the first one)

# Test health check
curl http://localhost:8000/api/v1/health

# Expected: {"status":"ok"}
```

---

### 7.4 Create Your First User

**Using curl:**
```bash
curl -X POST "http://localhost:8000/api/v1/users" \
  -H "Content-Type: application/json" \
  -d '{
    "external_id": "my_first_user",
    "target_language": "Spanish",
    "level": "A2"
  }'
```

**Expected response:**
```json
{
  "id": "some-uuid-here",
  "external_id": "my_first_user",
  "target_language": "Spanish",
  "level": "A2"
}
```

**✅ If this works, your database is connected and working!**

---

### 7.5 Test AI Integration (The Big Test!)

**Get a vocabulary flashcard (this tests Gemini API):**

```bash
curl "http://localhost:8000/api/v1/vocabulary/next?user_id=my_first_user&target_language=Spanish&level=A2"
```

**This will take 3-5 seconds** (calling Gemini API)

**Expected response:**
```json
{
  "word": "biblioteca",
  "definition": "library",
  "example_sentence": "Voy a la biblioteca para estudiar.",
  "options": ["library", "bookstore", "school", "museum"],
  "correct_option_index": 0
}
```

**✅ If you get a flashcard, your AI integration is working!**

**❌ If you get an error:**
- Check your `LLM_API_KEY` in `.env`
- Verify the key works (test from Step 1.1)
- Check server logs for error details

---

### 7.6 Start a Conversation (Full Test)

**Start a conversation session:**
```bash
curl -X POST "http://localhost:8000/api/v1/conversation/start" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "my_first_user",
    "target_language": "Spanish",
    "level": "A2",
    "topic": "ordering food"
  }'
```

**Expected response:**
```json
{
  "session_id": "uuid-here",
  "opening_message": "¡Hola! ¿Qué te gustaría pedir hoy?"
}
```

**✅ If you get an opening message in Spanish, everything is working perfectly!**

---

### 7.7 Verification Checklist

Before moving on, verify:

- [ ] Server starts without errors
- [ ] Can access http://localhost:8000/api/v1/docs
- [ ] Health check returns OK
- [ ] Can create a user
- [ ] Can get vocabulary flashcard (AI working)
- [ ] Can start conversation (AI + DB working)
- [ ] No errors in server logs

---

## Step 8: Next Steps

### 8.1 Explore the API

**Interactive documentation:**
```
http://localhost:8000/api/v1/docs
```

**Try these features:**
1. Create multiple users
2. Start conversations in different languages
3. Get grammar questions
4. Get writing feedback
5. Check user progress

---

### 8.2 Run Comprehensive Tests

```bash
# See check.md for full testing guide
cat check.md
```

**Follow the testing guide to:**
- Test all 5 learning modules
- Test error handling
- Test progress tracking
- Run integration tests

---

### 8.3 Development Workflow

**When working on the backend:**

```bash
# 1. Activate virtual environment
cd backend
source venv/bin/activate

# 2. Start server in development mode
uvicorn main:app --reload

# 3. Make changes to code
# Server auto-reloads when you save files

# 4. Test your changes at http://localhost:8000/api/v1/docs
```

---

### 8.4 Common Development Tasks

**Add a new dependency:**
```bash
source venv/bin/activate
pip install package-name
pip freeze > requirements.txt
```

**Reset database:**
```bash
dropdb language_app
createdb language_app
# Restart server (tables will be recreated)
```

**View server logs:**
```bash
# Logs appear in terminal where uvicorn is running
# Look for errors, warnings, and request logs
```

**Check database contents:**
```bash
psql language_app

# View users
SELECT * FROM users;

# View progress
SELECT * FROM user_progress;

# View conversation sessions
SELECT * FROM conversation_sessions;

# Exit
\q
```

---

### 8.5 Next Development Steps

**Recommended enhancements:**

1. **Add Authentication**
   - Implement JWT tokens
   - Secure endpoints with authentication

2. **Add Caching**
   - Use Redis for caching flashcards
   - Reduce LLM API calls

3. **Add Rate Limiting**
   - Prevent API abuse
   - Limit requests per user

4. **Improve Error Handling**
   - Add retry logic for LLM calls
   - Better error messages

5. **Add Logging**
   - Use proper logging framework
   - Log to files, not just console

6. **Write Tests**
   - Unit tests for services
   - Integration tests for endpoints
   - Use pytest

7. **Add Monitoring**
   - Track API response times
   - Monitor LLM API usage
   - Set up alerts

---

### 8.6 Deployment Preparation

**When ready to deploy:**

1. **Update .env for production:**
   ```env
   ENV=production
   DEBUG=False
   BACKEND_CORS_ORIGINS=https://yourdomain.com
   ```

2. **Use production database:**
   - Set up PostgreSQL on cloud (AWS RDS, Google Cloud SQL, etc.)
   - Update `DATABASE_URL`

3. **Secure API keys:**
   - Use environment variables (don't commit .env)
   - Use secrets manager (AWS Secrets Manager, etc.)

4. **Choose deployment platform:**
   - **Google Cloud Run** (recommended, easy)
   - **AWS Elastic Beanstalk**
   - **Heroku**
   - **DigitalOcean App Platform**
   - **Railway**

5. **Deploy:**
   ```bash
   # Example: Google Cloud Run
   gcloud run deploy language-backend \
     --source . \
     --set-env-vars DATABASE_URL=... \
     --allow-unauthenticated
   ```

---

### 8.7 Connect to Android App

**Once backend is deployed:**

1. **Update Android app's API base URL:**
   ```kotlin
   const val BASE_URL = "https://your-backend-url.com/api/v1"
   ```

2. **Test from Android:**
   - Health check
   - User creation
   - All module features

3. **Handle errors gracefully:**
   - Network errors
   - API errors
   - Timeout errors

---

## Troubleshooting

### Problem: Server won't start

**Error:** `Address already in use`

**Solution:**
```bash
# Find what's using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
uvicorn main:app --reload --port 8080
```

---

### Problem: Database connection error

**Error:** `could not connect to server: Connection refused`

**Solution:**
```bash
# Check if PostgreSQL is running
pg_isready

# Start PostgreSQL
brew services start postgresql@15  # macOS
sudo systemctl start postgresql     # Linux

# Check DATABASE_URL in .env is correct
cat .env | grep DATABASE_URL
```

---

### Problem: LLM API error

**Error:** `HTTP error during LLM API call`

**Solution:**
1. Check your `LLM_API_KEY` in `.env`
2. Verify key at https://makersuite.google.com/app/apikey
3. Make sure you have no quotes around the key
4. Test the key with curl (see Step 1.1)

---

### Problem: Import errors

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
# Make sure venv is activated
source venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt

# Verify installation
pip list | grep fastapi
```

---

### Problem: Database tables not created

**Error:** `relation "users" does not exist`

**Solution:**
```bash
# Manually create tables
python3 -c "
from app.db.database import engine
from app.db.models import Base
Base.metadata.create_all(bind=engine)
"

# Restart server
```

---

### Problem: Slow API responses

**Issue:** Requests take > 10 seconds

**Reasons:**
- LLM API calls take 2-5 seconds (normal)
- STT calls take 5-10 seconds (normal)
- Network latency
- Cold start (first request)

**Not a problem if < 10 seconds per request**

---

### Problem: .env file not being read

**Error:** `field required` for API keys

**Solution:**
```bash
# Check .env is in correct location
ls -la .env

# Check there's no .env.example being read instead
cat .env

# Restart server after changing .env
```

---

## Quick Reference

### Essential Commands

```bash
# Activate virtual environment
source venv/bin/activate

# Start server
uvicorn main:app --reload

# Access documentation
open http://localhost:8000/api/v1/docs

# Check logs (in terminal where uvicorn runs)

# Stop server
Ctrl + C

# Deactivate virtual environment
deactivate
```

---

### Essential URLs

| Purpose | URL |
|---------|-----|
| API Docs | http://localhost:8000/api/v1/docs |
| Health Check | http://localhost:8000/api/v1/health |
| Root | http://localhost:8000 |
| ReDoc | http://localhost:8000/api/v1/redoc |

---

### Files to Know

| File | Purpose |
|------|---------|
| `.env` | Your configuration and API keys |
| `main.py` | Entry point of application |
| `app/main.py` | FastAPI app initialization |
| `check.md` | Comprehensive testing guide |
| `README.md` | Full documentation |
| `requirements.txt` | Python dependencies |

---

## Success Checklist

You're ready to go when you have:

- [ ] ✅ Python 3.11+ installed
- [ ] ✅ PostgreSQL installed and running
- [ ] ✅ Google Gemini API key obtained
- [ ] ✅ Google Speech-to-Text API key obtained
- [ ] ✅ Virtual environment created and activated
- [ ] ✅ Dependencies installed
- [ ] ✅ `.env` file configured with all keys
- [ ] ✅ Database created (`language_app`)
- [ ] ✅ Server starts without errors
- [ ] ✅ Can access API documentation
- [ ] ✅ Health check returns OK
- [ ] ✅ Can create users
- [ ] ✅ Can get AI-generated content
- [ ] ✅ All tests pass (from check.md)

---

## What You've Accomplished 🎉

Congratulations! You now have:

✅ A fully functional AI-powered language learning backend
✅ 5 complete learning modules (Conversation, Vocabulary, Grammar, Writing, Phonetics)
✅ Integration with Google's Gemini AI for content generation
✅ Speech-to-text for pronunciation evaluation
✅ PostgreSQL database for user data and progress
✅ Interactive API documentation
✅ A solid foundation for your Android app

---

## Getting Help

**If you get stuck:**

1. **Check this guide** - Read the troubleshooting section
2. **Check server logs** - Look for error messages in terminal
3. **Check API docs** - Visit http://localhost:8000/api/v1/docs
4. **Test systematically** - Use check.md testing guide
5. **Verify each component:**
   - PostgreSQL running? (`pg_isready`)
   - Virtual environment activated? (`which python`)
   - .env file correct? (`cat .env`)
   - API keys valid? (Test from Step 1)

**Common issues are usually:**
- Forgot to activate virtual environment
- Wrong DATABASE_URL in .env
- Invalid or missing API keys
- PostgreSQL not running
- Port 8000 already in use

---

**Happy Coding! 🚀**

Now proceed to `check.md` to test all features comprehensively!
