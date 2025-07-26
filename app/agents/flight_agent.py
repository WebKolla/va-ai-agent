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

    results = search_flights_with_score(search_query)

    if not results:
        return []

    formatted_results = []

    for doc, score in results:
        metadata = doc.metadata

        if max_price and metadata.get("price", 0) > max_price:
            continue

        formatted_results.append(
            {
                "airline": metadata.get("airline"),
                "from_airport": metadata.get("from_airport"),
                "to_airport": metadata.get("to_airport"),
                "price": metadata.get("price"),
                "duration": metadata.get("duration"),
                "date": metadata.get("date"),
                "similarity_score": score,
            }
        )

    return formatted_results
