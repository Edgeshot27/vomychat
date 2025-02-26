import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

KEY = os.getenv("SECRET_KEY", "your_default_secret_key")
algorithm = os.getenv("ALGORITHM", "HS256")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite+aiosqlite:///./testing.db")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
