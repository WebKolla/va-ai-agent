import os

from dotenv import load_dotenv
from pydantic_ai import Agent

from app.datastore import search_flights_with_score
from app.prompts import FLIGHT_AGENT_PROMPT
from app.schemas import FlightRecommendation

load_dotenv()

flight_agent = Agent(
    os.getenv("GPT_MODEL"),
    deps_type=str,
    output_type=FlightRecommendation,
    instructions=(FLIGHT_AGENT_PROMPT),
)


@flight_agent.tool_plain
async def flight_search(
    query: str,
    from_city: str = None,
    to_city: str = None,
    max_price: float = None,
    month: str = None,
) -> str:
    """Search for flights based on user travel requirements."""
    search_components = [query]
    if from_city:
        search_components.append(f"from {from_city}")
    if to_city:
        search_components.append(f"to {to_city}")
    if month:
        search_components.append(f"in {month}")

    search_query = " ".join(search_components)

    results = search_flights_with_score(search_query, k=5)

    if not results:
        return "No flights found matching your criteria."

    formatted_results = []
    for doc, score in results:
        metadata = doc.metadata

        if max_price and metadata.get("price", 0) > max_price:
            continue

        formatted_results.append(
            f"Flight: {metadata.get('airline')} {metadata.get('flight_number', '')}\n"
            f"Route: {metadata.get('from_airport')} → {metadata.get('to_airport')}\n"
            f"Price: ${metadata.get('price')}\n"
            f"Duration: {metadata.get('duration')}\n"
            f"Date: {metadata.get('date')}\n"
            f"Similarity Score: {score:.3f}\n"
            f"Details: {doc.page_content[:250]}...\n"
        )

    if not formatted_results:
        return "No flights found within your price range."

    return "\n" + "=" * 50 + "\n".join(formatted_results)
