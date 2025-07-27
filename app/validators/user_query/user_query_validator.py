import os
import re

import openai
from dotenv import load_dotenv


load_dotenv()


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

    if len(text.strip()) > 1000:
        return {
            "is_safe": False,
            "message": "Your query is too long. Please provide a shorter query.",
        }

    if validate_query_for_injection(text)["is_safe"] is False:
        return {
            "is_safe": False,
            "message": "Your query contains inappropriate content. Please rephrase your travel request.",
        }

    if validate_query_for_gambling(text)["is_safe"] is False:
        return {
            "is_safe": False,
            "message": "I'm a travel assistant and cannot help with gambling-related requests. Please ask about travel destinations, hotels, flights, or activities instead.",
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

        return {"is_safe": True, "message": "Valid user query"}

    except Exception as e:
        print(f"Content validation error: {e}")
        return {"is_safe": True, "message": "Validation service unavailable"}


def validate_query_for_injection(query: str) -> dict:
    """Enhanced query validation with multiple checks."""

    suspicious_patterns = [
        r"<script.*?>.*?</script>",  # XSS
        r"union.*select",  # SQL injection
        r"javascript:",  # JavaScript execution
        r"eval\s*\(",  # Code execution
    ]

    for pattern in suspicious_patterns:
        if re.search(pattern, query, re.IGNORECASE):
            return {"is_safe": False}

    return {"is_safe": True}


def validate_query_for_gambling(query: str) -> dict:
    """Validate query for gambling."""
    gambling_keywords = [
        "casino",
        "gambling",
        "poker",
        "blackjack",
    ]

    text_lower = query.lower()
    gambling_detected = any(keyword in text_lower for keyword in gambling_keywords)

    if gambling_detected:
        return {
            "is_safe": False,
        }

    return {"is_safe": True}
