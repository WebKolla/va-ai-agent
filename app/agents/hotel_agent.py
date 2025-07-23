"""
Hotel Agent for finding hotels based on user requirements.
"""

import os

from dotenv import load_dotenv
from pydantic_ai import Agent

from app.datastore import search_hotels_with_score
from app.prompt import HOTEL_AGENT_PROMPT
from app.schemas import HotelRecommendation

load_dotenv()


hotel_agent = Agent(
    os.getenv("GPT_MODEL"),
    deps_type=str,
    output_type=HotelRecommendation,
    instructions=(HOTEL_AGENT_PROMPT),
)


@hotel_agent.tool_plain
async def hotel_search(
    query: str,
    location: str = None,
    max_price: float = None,
    min_rating: float = None,
) -> str:
    """Search for hotels based on user accommodation requirements."""
    search_query = query
    if location:
        search_query += f" in {location}"

    results = search_hotels_with_score(search_query, k=5)

    if not results:
        return "No hotels found matching your criteria."

    formatted_results = []
    for doc, score in results:
        metadata = doc.metadata

        if max_price and metadata.get("price_per_night", 0) > max_price:
            continue
        if min_rating and metadata.get("rating", 0) < min_rating:
            continue

        formatted_results.append(
            f"Hotel: {metadata.get('name')}\n"
            f"Location: {metadata.get('city')}\n"
            f"Rating: {metadata.get('rating')} stars\n"
            f"Price: ${metadata.get('price_per_night')}/night\n"
            f"Pricing Tier: {metadata.get('pricing_tier')}\n"
            f"Similarity Score: {score:.3f}\n"
            f"Description: {doc.page_content[:300]}...\n"
        )

    if not formatted_results:
        return "No hotels found matching your filters."

    return "\n" + "=" * 50 + "\n".join(formatted_results)
