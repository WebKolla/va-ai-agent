from app.schemas import TravelAdvice

from app.datastore import (
    search_hotels_with_score,
    search_flights_with_score,
    search_experiences_with_score,
)


async def search_hotel_in_data(hotel_name: str, city: str) -> bool:
    """Search for a hotel in our seed data by name and city."""
    search_query = f"{hotel_name} {city}"
    results = search_hotels_with_score(search_query, k=5)

    if not results:
        return f"No hotels found for '{hotel_name}' in {city}"

    matches = []
    for doc, score in results:
        metadata = doc.metadata
        stored_name = metadata.get("name", "")
        stored_city = metadata.get("city", "")

        matches.append(
            {"name": stored_name, "city": stored_city, "similarity": f"{score:.3f}"}
        )

    if len(matches) > 0:
        return True
    else:
        return False


async def search_flight_in_data(
    airline: str, from_airport: str, to_airport: str, date: str
) -> bool:
    """Search for a flight route in our seed data."""
    search_query = f"{airline} {from_airport} {to_airport} {date}"
    results = search_flights_with_score(search_query, k=5)

    if not results:
        return f"No flights found for {airline} from {from_airport} to {to_airport} on {date}"

    matches = []
    for doc, score in results:
        metadata = doc.metadata
        stored_airline = metadata.get("airline", "")
        stored_from = metadata.get("from_airport", "")
        stored_to = metadata.get("to_airport", "")
        stored_date = metadata.get("date", "")

        matches.append(
            {
                "airline": stored_airline,
                "route": f"{stored_from}-{stored_to}",
                "date": stored_date,
                "similarity": f"{score:.3f}",
            }
        )

    if len(matches) > 0:
        return True
    else:
        return False


async def search_experience_in_data(experience_name: str, city: str) -> bool:
    """Search for an experience in our seed data by name and city."""
    search_query = f"{experience_name} {city}"
    results = search_experiences_with_score(search_query, k=5)

    if not results:
        return f"No experiences found for '{experience_name}' in {city}"

    matches = []
    for doc, score in results:
        metadata = doc.metadata
        stored_name = metadata.get("name", "")
        stored_city = metadata.get("city", "")

        matches.append(
            {"name": stored_name, "city": stored_city, "similarity": f"{score:.3f}"}
        )

    if len(matches) > 0:
        return True
    else:
        return False


def get_all_recommendations(recommendations: TravelAdvice) -> bool:
    """Get all recommendations from the manager agent."""
    has_hotel = search_hotel_in_data(
        recommendations.hotel.name, recommendations.hotel.city
    )
    has_flight = search_flight_in_data(
        recommendations.flight.airline,
        recommendations.flight.from_airport,
        recommendations.flight.to_airport,
        recommendations.flight.date,
    )
    has_experience = search_experience_in_data(
        recommendations.experience.name, recommendations.experience.city
    )

    if has_hotel and has_flight and has_experience:
        return True
    else:
        return False
