import os
from dotenv import load_dotenv

# load the environment variables from the .env file
load_dotenv()

class Settings:
    # try to read the key. If it's missing, it returns None.
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    # DATABASE_URL = os.getenv("DATABASE_URL")

# create a single instance to use everywhere (global class instance)
settings = Settings()