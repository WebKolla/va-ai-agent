import os

import openai
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


async def validate_user_query(text: str) -> dict:
    """
    Validate user input for inappropriate content and length requirements.
    """
    if not text or not text.strip():
        return {
            "is_safe": False,
            "message": "Please provide a travel query. Tell me where you'd like to go or what you're looking for!",
        }

    if len(text.strip()) < 3:
        return {
            "is_safe": False,
            "message": "Your query is too short. Please provide more details about your travel plans.",
        }

    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = client.moderations.create(input=text)
        result = response.results[0]

        if result.flagged:
            return {
                "is_safe": False,
                "message": "Your query contains inappropriate content. Please rephrase your travel request.",
            }

        gambling_keywords = [
            "casino",
            "gambling",
            "poker",
            "blackjack",
            "roulette",
            "slot machine",
            "betting",
            "lottery",
            "jackpot",
            "baccarat",
            "craps",
            "sports betting",
        ]

        text_lower = text.lower()
        gambling_detected = any(keyword in text_lower for keyword in gambling_keywords)

        if gambling_detected:
            return {
                "is_safe": False,
                "message": "I'm a travel assistant and cannot help with gambling-related requests. Please ask about travel destinations, hotels, flights, or activities instead.",
            }

        return {"is_safe": True, "message": "Content is appropriate"}

    except Exception as e:
        print(f"Content validation error: {e}")
        return {"is_safe": True, "message": "Validation service unavailable"}
