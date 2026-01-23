PLEASE READ BEFORE TESTING THE APP



Important: If you are on Windows 11, follow furthersteps.md instead (the original /main used macOS-only libraries and PostgreSQL; a temporary SQLite setup was used for testing).

If you are not on Windows 11, continue below.



Quick step-by-step setup

1\. Environment configuration (.env)



The database connection string needs to be reverted from the local SQLite file to your PostgreSQL instance.



File: backend/.env

Change:



\# from

DATABASE\_URL=sqlite:///./test\_language\_app.db



\# to (replace with your real credentials)

DATABASE\_URL=postgresql://user:password@localhost:5432/language\_app



2\. Restore dependencies (requirements.txt)



macOS/PostgreSQL require the specific driver that was removed for the SQLite version.



File: backend/requirements.txt

Ensure the following lines are present:



psycopg2-binary==2.9.9  # Required for PostgreSQL driver

pydantic==2.12.5        # Keep this version (stability fix)

pydantic-settings==2.2.1





Note: You can safely remove aiosqlite if you are no longer testing with SQLite.



3\. Database engine adjustment (database.py)



SQLite required a special connect\_args={'check\_same\_thread': False} argument for concurrency; PostgreSQL does not.



File: backend/app/db/database.py

Update your engine creation logic:



\# If you see:

\# engine = create\_engine(DATABASE\_URL, connect\_args={'check\_same\_thread': False})



\# Change it back to the standard version:

engine = create\_engine(DATABASE\_URL)



4\. Standardizing UUIDs to strings (models.py)



To prevent AttributeError: 'str' object has no attribute 'hex' (common when switching between SQLite and Postgres), use strings for IDs instead of native UUID types.



File: backend/app/db/models.py

Ensure your ID columns look like this:



from sqlalchemy import Column, String

from uuid import uuid4



def get\_uuid\_str():

&nbsp;   return str(uuid4())



\# In your classes (User, ConversationSession, etc.):

id = Column(String, primary\_key=True, default=get\_uuid\_str)





Do not revert these to UUID types. Using strings is more robust for cross-platform development and avoids SQLAlchemy mapping errors.



5\. Pydantic v2 compatibility



The project was upgraded to Pydantic v2. These changes are permanent.



Rule 1: Use .model\_dump() instead of .dict() when converting models to dictionaries.



Rule 2: Use .model\_validate() instead of .from\_orm() or .parse\_obj().



These are required for the newer, faster Pydantic library.



6\. macOS terminal commands (clean \& start)



Run these in your project root to clean Windows-specific cache and start fresh (macOS example):



\# 1. Remove the SQLite DB if it exists

rm backend/test\_language\_app.db



\# 2. Create a fresh virtual environment

cd backend

python3 -m venv venv

source venv/bin/activate



\# 3. Install restored dependencies

pip install --upgrade pip

pip install -r requirements.txt



\# 4. Start the server

uvicorn app.main:app --reload



7\. PostgreSQL setup (if not already running)



If you need to restart local Postgres on macOS via Homebrew:



\# start the service

brew services start postgresql



\# create the database if you haven't already

createdb language\_app



Troubleshooting / Notes



Keep id columns as String for cross-platform compatibility.



Ensure psycopg2-binary is installed when connecting to Postgres.



Make sure your .env is not committed with real credentials (use environment-specific secrets).

