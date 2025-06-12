import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

#: Gmail API client ID (required)
GMAIL_CLIENT_ID: Optional[str] = os.getenv("GMAIL_CLIENT_ID")
#: Gmail API client secret (required)
GMAIL_CLIENT_SECRET: Optional[str] = os.getenv("GMAIL_CLIENT_SECRET")
#: Path to Google credentials JSON file
GOOGLE_CREDENTIALS_PATH: str = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
#: Path to token file for Gmail OAuth
TOKEN_PATH: str = os.getenv("TOKEN_PATH", "token.pickle")
#: Redis connection URL
REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
#: Path to the GPT4All model file
MODEL_PATH: str = os.getenv("MODEL_PATH", "Phi-3-mini-4k-instruct.Q4_0.gguf")

if not GMAIL_CLIENT_ID or not GMAIL_CLIENT_SECRET:
    raise RuntimeError("GMAIL_CLIENT_ID and GMAIL_CLIENT_SECRET must be set in the environment.") 