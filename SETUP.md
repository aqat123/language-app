# Setup and Installation Guide

Complete step-by-step guide for setting up the Language Learning Application backend. This guide covers both initial setup for new developers and specific considerations for different operating systems.

**Time Required:** 30-45 minutes  
**Difficulty Level:** Intermediate (basic command-line knowledge required)

## Prerequisites Checklist

Before starting, verify you have:

- [ ] Python 3.11 or higher installed
- [ ] PostgreSQL 12 or higher installed (or plan to install during this guide)
- [ ] Git (optional, for cloning the project)
- [ ] Text editor or IDE (VS Code, PyCharm, etc.)
- [ ] Internet connection (for downloading packages and API keys)
- [ ] Administrator/sudo access on your machine

**Check Python Version:**

```bash
python3 --version
```

Expected output: `Python 3.11.x` or higher

If you need to install or update Python:
- **macOS:** `brew install python@3.11`
- **Ubuntu/Debian:** `sudo apt install python3.11`
- **Windows:** Download from https://www.python.org/downloads/

## Section 1: Get API Keys

You need two API keys to enable all AI features.

### Step 1.1: Google Gemini API Key

The Gemini API powers all content generation (conversations, flashcards, grammar questions, writing feedback).

1. Go to https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and save it for Section 4

**Note:** Keep this key confidential and never commit it to version control.

### Step 1.2: Google Cloud Speech-to-Text API Key

This API enables the Phonetics module to evaluate pronunciation.

1. Go to https://console.cloud.google.com/
2. Create a new project and enable the Speech-to-Text API
3. Create an API key in the credentials section
4. Copy the key and save it for Section 4

### Step 1.3: API Keys Summary

Before proceeding, you should have:

- [ ] Gemini API Key: `AIzaSy...`
- [ ] Speech-to-Text API Key: `AIzaSy...`

## Section 2: Install PostgreSQL

PostgreSQL is the database that stores user progress, conversation history, and generated content.

### Step 2.1: macOS (Using Homebrew)

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

Expected output: `accepting connections`

### Step 2.2: Ubuntu/Debian Linux

```bash
# Update package list
sudo apt update

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Start and enable PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Verify it's running
sudo systemctl status postgresql
```

Expected output: `active (running)`

### Step 2.3: Windows

1. Download PostgreSQL installer from https://www.postgresql.org/download/windows/
2. Download version 15.x (or latest stable)
3. Run the installer (.exe file)
4. Accept license agreement
5. Choose installation directory (default is fine)
6. Keep all components checked
7. When prompted for password, enter a strong password (you'll need it later)
8. Use default port 5432
9. Choose your locale
10. Complete the installation

**Verify Installation:**

```cmd
psql --version
```

Expected output: `psql (PostgreSQL) 15.x`

### Step 2.4: Create the Database

Once PostgreSQL is installed and running:

**macOS/Linux:**

```bash
# Create the language_app database
createdb language_app

# Verify creation
psql -l
```

You should see `language_app` in the list.

**Windows (using SQL Shell):**

```cmd
# Open "SQL Shell (psql)" from Start Menu
# When prompted:
# Server: localhost
# Database: postgres
# Port: 5432
# Username: postgres
# Password: [the password you set during installation]

# Then in the psql prompt:
CREATE DATABASE language_app;

# Exit
\q
```

### Step 2.5: Get Your Database URL

Your database connection URL will be in one of these formats:

**Default (password-less, local development):**

```
postgresql://postgres:@localhost:5432/language_app
```

**With custom password:**

```
postgresql://postgres:your_password@localhost:5432/language_app
```

**Test Your Connection:**

```bash
psql "postgresql://postgres:@localhost:5432/language_app"
```

If you connect successfully, the database is ready. Type `\q` to exit.

## Section 3: Python Environment Setup

### Step 3.1: Navigate to Backend Directory

```bash
cd language-app/backend
```

### Step 3.2: Create Virtual Environment

A virtual environment isolates project dependencies from your system Python.

```bash
# Create virtual environment named 'venv'
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# You should see (venv) in your terminal prompt
```

### Step 3.3: Install Dependencies

```bash
# Upgrade pip (package manager)
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

Expected: Installation of 20+ packages (FastAPI, SQLAlchemy, Pydantic, etc.)

**Verify Installation:**

```bash
pip list | grep -E "fastapi|sqlalchemy|pydantic|uvicorn"
```

Expected: See versions of FastAPI, SQLAlchemy, Pydantic, and Uvicorn

## Section 4: Environment Configuration

### Step 4.1: Create .env File

The `.env` file stores sensitive configuration (API keys, database credentials).

```bash
# Copy the example file
cp .env.example .env

# Open for editing
nano .env  # or use your preferred editor
```

### Step 4.2: Fill in Configuration Values

Edit the `.env` file with your actual values:

```env
# DATABASE
DATABASE_URL=postgresql://postgres:@localhost:5432/language_app

# GOOGLE GEMINI API
LLM_API_KEY=AIzaSy...your_gemini_key...
LLM_API_BASE_URL=https://generativelanguage.googleapis.com/v1beta
LLM_MODEL=gemini-2.5-flash

# GOOGLE SPEECH-TO-TEXT API
STT_API_KEY=AIzaSy...your_speech_to_text_key...
STT_API_BASE_URL=https://speech.googleapis.com/v1

# APPLICATION SETTINGS
ENV=dev
DEBUG=True
API_V1_PREFIX=/api/v1
PROJECT_NAME=Language Learning Backend
BACKEND_CORS_ORIGINS=*
```

**Important:**

- Replace `your_gemini_key` with the actual key from Section 1.1
- Replace `your_speech_to_text_key` with the actual key from Section 1.2
- Adjust `DATABASE_URL` if you set a custom password for PostgreSQL
- Never commit `.env` to version control

### Step 4.3: Verify Environment File

```bash
# Check that .env was created
cat .env

# Verify it has all required variables
grep -E "DATABASE_URL|LLM_API_KEY|STT_API_KEY" .env
```

## Section 5: Database Initialization

### Step 5.1: Initialize Database Schema

The backend automatically creates database tables on startup. When you run the server for the first time, it will:

1. Create the `users` table
2. Create the `user_progress` table
3. Create the `conversation_sessions` table
4. Create the `content_logs` table

No manual SQL commands are needed.

## Section 6: Run the Backend

### Step 6.1: Start the Server

Make sure you're in the backend directory with the virtual environment activated:

```bash
# Verify you're in the right place
pwd  # Should end with: .../language-app/backend

# Verify venv is activated
which python  # Should show path with /venv/

# Start the server
uvicorn main:app --reload
```

**Expected Output:**

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started server process [12345]
INFO:     Application startup complete.
```

### Step 6.2: Verify the Server is Running

Open in your browser:

```
http://localhost:8000/api/v1/docs
```

You should see the **Swagger UI** with all API endpoints listed.

**Alternative (using curl):**

```bash
curl http://localhost:8000/api/v1/health
```

Expected response:

```json
{
  "status": "ok"
}
```

### Step 6.3: Stop the Server

When done, stop the server with:

```bash
# Press Ctrl+C in the terminal
```

### Step 6.4: Test from Web Interface

Now test the application through the web interface:

1. **Open a new terminal window** (keep the backend running in your current terminal)

2. **Navigate to the web interface directory:**

   ```bash
   cd language-app/simple-web-interface
   ```

3. **Start the web server:**

   ```bash
   python -m http.server 3000
   ```

   Expected output:

   ```
   Serving HTTP on 0.0.0.0 port 3000 (http://0.0.0.0:3000/) ...
   ```

4. **Open your browser** and go to:

   ```
   http://localhost:3000
   ```

   You should see the language learning application interface.

5. **Test the modules** by interacting with the available learning features

6. **Verify backend communication** by checking that:
   - API calls are being made (check backend terminal for logs)
   - Responses are received without errors
   - The web interface displays content correctly

7. **Stop the web server** when done:

   ```bash
   # Press Ctrl+C in the terminal running the http.server
   ```

## Section 7: Platform-Specific Notes

### Important: Database Models and UUID Handling

When switching between SQLite and PostgreSQL, ensure database models use **string IDs**, not native UUID types:

**Correct (use this):**

```python
from sqlalchemy import Column, String
from uuid import uuid4

def get_uuid_str():
    return str(uuid4())

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=get_uuid_str)
```

**Incorrect (do not use):**

```python
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID

class User(Base):
    id = Column(UUID(as_uuid=True), primary_key=True)  # Will fail on Windows/SQLite
```

### Pydantic v2 Compatibility

The project uses Pydantic v2 (2.12.5+). Use these methods:

**Correct:**

```python
# Convert model to dictionary
user_dict = user_model.model_dump()

# Create model from dictionary
user = UserSchema.model_validate(data)
```

**Incorrect (Pydantic v1 syntax):**

```python
user_dict = user_model.dict()  # Will not work
user = UserSchema.from_orm(data)  # Will not work
```

### macOS-Specific Notes

**If PostgreSQL was installed with Homebrew:**

Restart PostgreSQL if needed:

```bash
brew services restart postgresql@15
```

**If you encounter permission issues:**

```bash
# Ensure your user owns the PostgreSQL data directory
brew services stop postgresql@15
rm -rf /usr/local/var/postgres
initdb /usr/local/var/postgres
brew services start postgresql@15
```

### Windows-Specific Notes

**If you encounter "port already in use" error:**

```cmd
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with the number)
taskkill /PID <PID> /F
```

**If PostgreSQL service won't start:**

```cmd
# Start PostgreSQL service
net start postgresql-x64-15

# Or restart:
net stop postgresql-x64-15
net start postgresql-x64-15
```

**If psql command not found:**

Add PostgreSQL to your PATH:

```cmd
# Control Panel → System → Advanced → Environment Variables
# Add: C:\Program Files\PostgreSQL\15\bin
```

### Cross-Platform Compatibility Reminders

1. **Always use forward slashes in paths** when possible (they work on all platforms)
2. **Database URLs:** Use `postgresql://` not `postgres://` (newer standard)
3. **Virtual environment activation** varies by OS - use the correct command for your platform
4. **Environment variables:** .env files are read correctly on all platforms when using python-dotenv

## Section 8: Troubleshooting

### Error: "ModuleNotFoundError: No module named 'fastapi'"

**Cause:** Virtual environment not activated or dependencies not installed

**Solution:**

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Error: "FATAL: role 'postgres' does not exist"

**Cause:** PostgreSQL user not found

**Solution:**

```bash
# macOS - reinstall PostgreSQL
brew uninstall postgresql@15
brew install postgresql@15

# Linux - create the postgres user
sudo -u postgres createuser -s postgres
```

### Error: "Address already in use" (port 8000)

**Cause:** Another application is using port 8000

**Solution:**

```bash
# macOS/Linux - kill the process
lsof -ti:8000 | xargs kill -9

# Windows - see Windows-Specific section above
```

### Error: "could not translate host name 'localhost' to address"

**Cause:** Network configuration issue

**Solution:**

Try using IP address instead:

```env
DATABASE_URL=postgresql://postgres:@127.0.0.1:5432/language_app
```

### Error: "FATAL: password authentication failed for user 'postgres'"

**Cause:** Incorrect password in DATABASE_URL

**Solution:**

1. Reset PostgreSQL password:

   ```bash
   # macOS/Linux
   sudo -u postgres psql
   \password postgres
   # Enter new password twice
   ```

2. Update DATABASE_URL in .env with new password

### Error: "relation 'users' does not exist"

**Cause:** Database tables not created yet

**Solution:**

Tables are created automatically when you run the server for the first time. If this error persists:

```bash
# Delete the database and recreate
dropdb language_app
createdb language_app

# Restart the server
uvicorn main:app --reload
```

### Verifying Complete Setup

Once everything is installed, verify with this checklist:

- [ ] Python 3.11+ installed: `python3 --version`
- [ ] PostgreSQL running: `pg_isready`
- [ ] Database created: `psql language_app`
- [ ] Virtual environment activated: See `(venv)` in prompt
- [ ] Dependencies installed: `pip list | grep fastapi`
- [ ] .env file configured with API keys
- [ ] Backend starts: `uvicorn main:app --reload`
- [ ] Swagger UI accessible: http://localhost:8000/api/v1/docs
- [ ] Health check works: `curl http://localhost:8000/api/v1/health`

## Next Steps

After completing setup:

1. Review [API.md](API.md) to understand available endpoints
2. Follow [TESTING.md](TESTING.md) to test the API
3. Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand system design
4. Start developing or testing the application

For issues not covered here, check the Troubleshooting section or refer to [API.md](API.md) for endpoint-specific issues.
