import os

from dotenv import load_dotenv
from pydantic_ai import Agent

from app.datastore import search_experiences_with_score
from app.prompts import EXPERIENCE_AGENT_PROMPT
from app.schemas import ExperienceRecommendation

load_dotenv()

experience_agent = Agent(
    os.getenv("GPT_MODEL"),
    deps_type=str,
    output_type=ExperienceRecommendation,
    instructions=(EXPERIENCE_AGENT_PROMPT),
)


@experience_agent.tool_plain
async def experience_search(
    query: str, location: str = None, max_price: float = None
) -> str:
    """Search for experiences and activities based on user requirements."""
    search_query = query
    if location:
        search_query += f" in {location}"

    results = search_experiences_with_score(search_query)

    if not results:
        return []

    formatted_results = []

    for doc, score in results:
        metadata = doc.metadata

        if max_price and metadata.get("price", 0) > max_price:
            continue

        formatted_results.append(
            {
                "name": {metadata.get("name")},
                "city": {metadata.get("city")},
                "price": {metadata.get("price")},
                "duration": {metadata.get("duration")},
                "similarity_score": {score},
            }
        )

    return formatted_results
