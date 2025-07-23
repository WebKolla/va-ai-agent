import os

from dotenv import load_dotenv
from pydantic_ai import Agent

from app.datastore import search_experiences_with_score
from app.schemas import ExperienceRecommendation
from app.prompts import EXPERIENCE_AGENT_PROMPT

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

    results = search_experiences_with_score(search_query, k=5)

    if not results:
        return "No experiences found matching your criteria."

    formatted_results = []
    for doc, score in results:
        metadata = doc.metadata

        if max_price and metadata.get("price", 0) > max_price:
            continue

        formatted_results.append(
            f"Experience: {metadata.get('name')}\n"
            f"Location: {metadata.get('city')}\n"
            f"Price: ${metadata.get('price')}\n"
            f"Duration: {metadata.get('duration')}\n"
            f"Tags: {metadata.get('tags')}\n"
            f"Similarity Score: {score:.3f}\n"
            f"Description: {doc.page_content[:300]}...\n"
        )

    if not formatted_results:
        return "No experiences found within your price range."

    return "\n" + "=" * 50 + "\n".join(formatted_results)
