# Language Learning App - Backend

A FastAPI-based backend server for an AI-powered language learning application. This backend provides RESTful API endpoints for various language learning modules including conversation practice, vocabulary building, grammar exercises, writing feedback, and pronunciation assessment.

## Table of Contents

- [Technologies Used](#technologies-used)
- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
  - [Option 1: Using the Setup Script](#option-1-using-the-setup-script-recommended)
  - [Option 2: Manual Setup](#option-2-manual-setup)
- [Virtual Environment Management](#virtual-environment-management)
  - [Activating the Virtual Environment](#activating-the-virtual-environment)
  - [Deactivating the Virtual Environment](#deactivating-the-virtual-environment)
  - [Switching Python Versions](#switching-python-versions)
- [Running the Application](#running-the-application)
  - [Development Mode](#development-mode)
  - [Production Mode](#production-mode)
- [Docker Support](#docker-support)
- [API Documentation](#api-documentation)
- [Dependencies](#dependencies)
- [Development Workflow](#development-workflow)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## Technologies Used

### Core Framework
- **FastAPI** (v0.124.0) - Modern, fast web framework for building APIs with Python
- **Uvicorn** (v0.38.0) - Lightning-fast ASGI server implementation
- **Starlette** (v0.50.0) - Lightweight ASGI framework/toolkit (FastAPI dependency)

### Data Validation & Type Checking
- **Pydantic** (v2.12.5) - Data validation using Python type annotations
- **pydantic_core** (v2.41.5) - Core validation logic for Pydantic
- **annotated-types** (v0.7.0) - Reusable constraint types for use with typing.Annotated
- **typing_extensions** (v4.15.0) - Backported and experimental type hints

### Utilities
- **python-dotenv** (v1.2.1) - Environment variable management from .env files
- **PyYAML** (v6.0.3) - YAML parser and emitter
- **click** (v8.3.1) - Command-line interface creation toolkit

### Server & Performance
- **uvloop** (v0.22.1) - Ultra-fast asyncio event loop (Unix-based systems)
- **httptools** (v0.7.1) - Fast HTTP parsing
- **watchfiles** (v1.1.1) - Hot-reload file watching
- **websockets** (v15.0.1) - WebSocket protocol implementation

### HTTP & Networking
- **h11** (v0.16.0) - Pure-Python HTTP/1.1 protocol implementation
- **anyio** (v4.12.0) - Asynchronous networking and concurrency library
- **idna** (v3.11) - Internationalized Domain Names in Applications

### Documentation & Development
- **annotated-doc** (v0.0.4) - Documentation utilities
- **typing-inspection** (v0.4.2) - Runtime inspection of types

### AI Integration (Planned)
Based on the project plan, the following AI services will be integrated:
- **Google Gemini API** - Large language model for content generation
- **Google Cloud Speech-to-Text** - Speech recognition for pronunciation assessment
- **spaCy/Grammarly API** - Grammar checking (optional)

### Database (Planned)
- **PostgreSQL** - Primary database for user data and progress tracking

### Deployment & Infrastructure
- **Docker** - Containerization for consistent deployment
- **AWS/GCP** - Cloud deployment platform (planned)

---

## Prerequisites

Before setting up the backend, ensure you have the following installed:

- **Python 3.9 or higher** (Python 3.11+ recommended)
  - Check version: `python3 --version`
  - Download from: [python.org](https://www.python.org/downloads/)

- **pip** (Python package installer)
  - Usually comes with Python
  - Check version: `pip --version`

- **Git** (for cloning the repository)
  - Check version: `git --version`

- **Docker** (optional, for containerized deployment)
  - Download from: [docker.com](https://www.docker.com/get-started)

---

## Project Structure

```
backend/
├── main.py                 # Main FastAPI application entry point
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker configuration
├── setup.sh               # Automated setup script
├── .gitignore             # Git ignore rules
├── README.md              # This file
├── technologies.md        # Detailed project plan and architecture
├── setup_log.md           # Setup documentation
├── diagram.png            # Architecture diagram
└── venv/                  # Virtual environment (created after setup)
```

---

## Installation & Setup

### Option 1: Using the Setup Script (Recommended)

The easiest way to set up the backend is using the provided setup script:

```bash
# Navigate to the backend directory
cd "language app/backend"

# Make the setup script executable (if not already)
chmod +x setup.sh

# Run the setup script
./setup.sh
```

The script will:
1. Check if Python 3 is installed
2. Create a virtual environment in `./venv`
3. Activate the virtual environment
4. Install all dependencies from `requirements.txt`

### Option 2: Manual Setup

If you prefer manual setup or encounter issues with the script:

```bash
# Navigate to the backend directory
cd "language app/backend"

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment (see next section for OS-specific commands)
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Upgrade pip (recommended)
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

---

## Virtual Environment Management

### Why Use a Virtual Environment?

A virtual environment isolates your project's dependencies from other Python projects and system-wide packages. This prevents version conflicts and ensures reproducibility.

### Activating the Virtual Environment

You must activate the virtual environment before running the application or installing new packages.

**On macOS/Linux:**
```bash
source venv/bin/activate
```

**On Windows (Command Prompt):**
```cmd
venv\Scripts\activate
```

**On Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

**On Windows (Git Bash):**
```bash
source venv/Scripts/activate
```

After activation, your terminal prompt will show `(venv)` prefix:
```
(venv) user@machine:~/language app/backend$
```

### Deactivating the Virtual Environment

When you're done working on the project:

```bash
deactivate
```

The `(venv)` prefix will disappear from your prompt.

### Switching Python Versions

If you need to use a different Python version:

1. **Delete the existing virtual environment:**
   ```bash
   rm -rf venv
   ```

2. **Create a new virtual environment with the desired Python version:**
   ```bash
   # Use a specific Python version (if installed)
   python3.11 -m venv venv
   # or
   python3.12 -m venv venv
   ```

3. **Activate the new environment and reinstall dependencies:**
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```

### Verifying Your Virtual Environment

Check which Python and pip are being used:

```bash
which python    # Should point to venv/bin/python
which pip       # Should point to venv/bin/pip
python --version
```

### Managing Dependencies

**Installing a new package:**
```bash
# Make sure venv is activated
pip install package-name
```

**Updating requirements.txt after adding packages:**
```bash
pip freeze > requirements.txt
```

**Installing from requirements.txt:**
```bash
pip install -r requirements.txt
```

**Upgrading all packages:**
```bash
pip install --upgrade -r requirements.txt
```

---

## Running the Application

### Development Mode

Development mode includes hot-reload, which automatically restarts the server when code changes are detected.

**Method 1: Using Uvicorn directly**
```bash
# Make sure the virtual environment is activated
source venv/bin/activate

# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Method 2: Custom host/port**
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 5000
```

**Method 3: With additional logging**
```bash
uvicorn main:app --reload --log-level debug
```

The server will start at:
- Default: http://127.0.0.1:8000
- API endpoint example: http://127.0.0.1:8000/api/greeting

### Production Mode

For production, disable auto-reload and configure workers:

```bash
# Single worker (basic)
uvicorn main:app --host 0.0.0.0 --port 80

# Multiple workers for better performance
uvicorn main:app --host 0.0.0.0 --port 80 --workers 4

# With uvloop for improved performance (Unix-based systems)
uvicorn main:app --host 0.0.0.0 --port 80 --loop uvloop --workers 4
```

### Environment Variables

Create a `.env` file in the backend directory for configuration:

```env
# .env file example
ENVIRONMENT=development
DEBUG=True
HOST=0.0.0.0
PORT=8000

# API Keys (add as needed)
GEMINI_API_KEY=your-api-key-here
GOOGLE_CLOUD_API_KEY=your-api-key-here

# Database Configuration (when implemented)
DATABASE_URL=postgresql://user:password@localhost/dbname
```

Load environment variables in your code:
```python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
```

---

## Docker Support

### Building the Docker Image

```bash
# Build the image
docker build -t language-learning-backend .

# Build with a specific tag
docker build -t language-learning-backend:v1.0 .
```

### Running the Docker Container

```bash
# Run the container
docker run -d -p 80:80 --name backend language-learning-backend

# Run with environment variables
docker run -d -p 80:80 --env-file .env --name backend language-learning-backend

# Run in interactive mode (for debugging)
docker run -it -p 80:80 language-learning-backend
```

### Accessing the Containerized Application

Once the container is running, access the API at:
- http://localhost:80/api/greeting
- http://localhost:80/docs (Swagger UI)

### Docker Compose (Recommended for multi-service setup)

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:80"
    environment:
      - ENVIRONMENT=production
    env_file:
      - .env
    volumes:
      - ./:/app
    restart: unless-stopped

  # Add database service when needed
  # postgres:
  #   image: postgres:15
  #   environment:
  #     POSTGRES_DB: language_app
  #     POSTGRES_USER: user
  #     POSTGRES_PASSWORD: password
  #   ports:
  #     - "5432:5432"
```

Run with Docker Compose:
```bash
docker-compose up -d
docker-compose down
```

---

## API Documentation

FastAPI automatically generates interactive API documentation.

### Accessing Documentation

Once the server is running:

1. **Swagger UI (Interactive):**
   - URL: http://127.0.0.1:8000/docs
   - Full interactive interface to test API endpoints

2. **ReDoc (Alternative):**
   - URL: http://127.0.0.1:8000/redoc
   - Clean, readable API reference

### Current Endpoints

#### GET /api/greeting
Returns a simple greeting message from the backend.

**Request:**
```bash
curl http://127.0.0.1:8000/api/greeting
```

**Response:**
```json
{
  "message": "Hello from the backend!"
}
```

### Planned Endpoints (Based on Project Architecture)

The following endpoints will be implemented:

- `POST /api/phonetics` - Pronunciation assessment
- `GET/POST /api/vocabulary` - Vocabulary flashcards and exercises
- `POST /api/conversation` - AI-powered conversation practice
- `POST /api/writing` - Writing feedback and corrections
- `GET/POST /api/grammar` - Grammar exercises and explanations
- `GET /api/user/progress` - User progress tracking
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User authentication

---

## Dependencies

### Core Dependencies Breakdown

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | 0.124.0 | Web framework for building APIs |
| uvicorn | 0.38.0 | ASGI server for running FastAPI |
| pydantic | 2.12.5 | Data validation and settings management |
| python-dotenv | 1.2.1 | Load environment variables from .env |
| starlette | 0.50.0 | ASGI framework/toolkit |
| PyYAML | 6.0.3 | YAML file parsing |

### Performance Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| uvloop | 0.22.1 | Fast event loop for asyncio |
| httptools | 0.7.1 | Fast HTTP request parsing |
| websockets | 15.0.1 | WebSocket support |
| watchfiles | 1.1.1 | File change detection for hot-reload |

For a complete list, see `requirements.txt`.

---

## Development Workflow

### 1. Starting Development

```bash
# Activate virtual environment
source venv/bin/activate

# Start development server
uvicorn main:app --reload
```

### 2. Making Changes

- Edit `main.py` or add new Python modules
- Server auto-reloads on file changes (in development mode)
- Test changes at http://127.0.0.1:8000

### 3. Testing API Endpoints

**Using curl:**
```bash
curl -X GET http://127.0.0.1:8000/api/greeting
```

**Using HTTPie (if installed):**
```bash
http GET http://127.0.0.1:8000/api/greeting
```

**Using Swagger UI:**
- Navigate to http://127.0.0.1:8000/docs
- Click "Try it out" on any endpoint

### 4. Adding New Dependencies

```bash
# Install new package
pip install package-name

# Update requirements.txt
pip freeze > requirements.txt
```

### 5. Code Quality (Recommended)

Install development tools:
```bash
pip install black flake8 mypy pytest
```

Format code:
```bash
black main.py
```

Lint code:
```bash
flake8 main.py
```

Type checking:
```bash
mypy main.py
```

### 6. Version Control

```bash
# Check status
git status

# Add changes
git add .

# Commit changes
git commit -m "Description of changes"

# Push to remote
git push origin main
```

---

## Troubleshooting

### Common Issues

#### 1. "python3: command not found"

**Solution:** Install Python 3:
- macOS: `brew install python3`
- Ubuntu/Debian: `sudo apt-get install python3`
- Windows: Download from [python.org](https://www.python.org)

#### 2. "Permission denied" when running setup.sh

**Solution:** Make the script executable:
```bash
chmod +x setup.sh
./setup.sh
```

#### 3. Virtual environment activation not working on Windows PowerShell

**Solution:** Enable script execution:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 4. Port already in use

**Error:** `Address already in use`

**Solution:** Use a different port or kill the process:
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process (replace PID with actual process ID)
kill -9 PID

# Or use a different port
uvicorn main:app --reload --port 8080
```

#### 5. Module import errors after installing packages

**Solution:** Ensure virtual environment is activated:
```bash
source venv/bin/activate
which python  # Should point to venv/bin/python
```

#### 6. Docker container won't start

**Solution:** Check logs:
```bash
docker logs backend
```

Verify Dockerfile and ensure all files are present.

#### 7. "Package not found" during pip install

**Solution:** Upgrade pip:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Getting Help

- FastAPI Documentation: https://fastapi.tiangolo.com/
- Uvicorn Documentation: https://www.uvicorn.org/
- Python Virtual Environments: https://docs.python.org/3/tutorial/venv.html
- Docker Documentation: https://docs.docker.com/

---

## Contributing

### Development Guidelines

1. **Code Style:**
   - Follow PEP 8 guidelines
   - Use type hints for function parameters and return values
   - Write docstrings for functions and classes

2. **Branching Strategy:**
   - `main` - Production-ready code
   - `develop` - Integration branch
   - `feature/feature-name` - New features
   - `bugfix/bug-name` - Bug fixes

3. **Commit Messages:**
   - Use clear, descriptive commit messages
   - Format: `[Type] Brief description`
   - Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Example:
```bash
git commit -m "[feat] Add vocabulary flashcard API endpoint"
git commit -m "[fix] Resolve CORS issue in conversation module"
git commit -m "[docs] Update README with Docker instructions"
```

4. **Testing:**
   - Write tests for new features
   - Ensure all tests pass before committing
   - Aim for high code coverage

### Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request with a clear description

---

## Project Architecture

For detailed information about the project architecture, AI integration strategy, and development roadmap, see [technologies.md](technologies.md).

### Key Architectural Components

- **Client-Server Architecture:** Android app (Kotlin) communicates with Python backend via REST API
- **AI Integration:** Google Gemini for content generation, Google STT for speech recognition
- **Validation Pattern:** Generate-then-verify using dual AI model approach
- **Database:** PostgreSQL for user data and progress tracking
- **Deployment:** Dockerized backend, cloud deployment (AWS/GCP)

---

## Quick Reference Commands

```bash
# Setup
./setup.sh                                    # Automated setup
python3 -m venv venv                         # Create venv manually
source venv/bin/activate                     # Activate venv (macOS/Linux)

# Running
uvicorn main:app --reload                    # Development mode
uvicorn main:app --host 0.0.0.0 --port 80   # Production mode

# Docker
docker build -t language-learning-backend .  # Build image
docker run -d -p 80:80 language-learning-backend  # Run container

# Dependencies
pip install -r requirements.txt              # Install dependencies
pip freeze > requirements.txt                # Update requirements
pip install package-name                     # Install new package

# Documentation
http://127.0.0.1:8000/docs                  # Swagger UI
http://127.0.0.1:8000/redoc                 # ReDoc
```

---

