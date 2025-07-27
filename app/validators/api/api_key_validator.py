import os

from dotenv import load_dotenv


load_dotenv()


def check_api_key() -> bool:
    """Check if there is an API key."""
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key is None:
        raise ValueError("OPENAI_API_KEY is not set")
    elif len(api_key) < 10:
        raise ValueError("OPENAI_API_KEY is too short")
    else:
        return True
