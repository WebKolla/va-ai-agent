import os
import random
import re
from typing import Any, Dict, List, Optional
from uuid import uuid4

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from app.data import experiences, flights, hotels

load_dotenv()

embeddings = OpenAIEmbeddings(model=os.getenv("EMBEDDING_MODEL"))
DB_PATH = os.getenv("DB_PATH")

hotels_store = Chroma(
    collection_name="va_hotels_collection",
    embedding_function=embeddings,
    persist_directory=f"{DB_PATH}/hotels",
)

experiences_store = Chroma(
    collection_name="va_experiences_collection",
    embedding_function=embeddings,
    persist_directory=f"{DB_PATH}/experiences",
)

flights_store = Chroma(
    collection_name="va_flights_collection",
    embedding_function=embeddings,
    persist_directory=f"{DB_PATH}/flights",
)


def get_random_room_price() -> float:
    """Returns a random price for hotel room pricing."""
    return float(random.randint(100, 1000))


def get_random_cabin_price() -> float:
    """Returns a random price for cabin pricing."""
    return float(random.randint(100, 1000))


def convert_duration_to_string(duration_pt: str) -> str:
    """Convert PT duration format to readable string."""
    if not duration_pt or not duration_pt.startswith("PT"):
        raise ValueError(f"Invalid duration format: {duration_pt}")

    hours_match = re.search(r"(\d+)H", duration_pt)
    minutes_match = re.search(r"(\d+)M", duration_pt)

    hours = int(hours_match.group(1)) if hours_match else 0
    minutes = int(minutes_match.group(1)) if minutes_match else 0

    if hours and minutes:
        return f"{hours}h {minutes}m"
    elif hours:
        return f"{hours}h"
    elif minutes:
        return f"{minutes}m"
    else:
        raise ValueError(f"No valid duration found in: {duration_pt}")


def create_hotel_document(hotel: Dict[str, Any]) -> Document:
    """Create a Document from hotel data following HotelRecommendation schema."""

    name = hotel.get("hotel_name")
    city = hotel.get("city")
    rating = hotel.get("rating")
    rating = float(rating)
    price_per_night = get_random_room_price()

    content = f"""
    Hotel: {name}
    Description: {hotel.get('hotel_description')}
    Location: {city}, {hotel.get('country')}
    Rating: {rating} stars
    Price per night: ${price_per_night}
    Pricing Tier: {hotel.get('pricing_tier')}
    Amenities: {hotel.get('amenities')}
    """

    return Document(
        page_content=content.strip(),
        metadata={
            "hotel_id": hotel.get("hotel_id"),
            "name": name,
            "city": city,
            "price_per_night": price_per_night,
            "rating": rating,
            "pricing_tier": hotel.get("pricing_tier"),
            "type": "hotel",
        },
    )


def create_experience_document(experience: Dict[str, Any]) -> Document:
    """Create a Document from experience data following ExperienceRecommendation schema."""
    name = experience.get("title")
    city = experience.get("city")
    base_price = experience.get("base_price")
    price = float(base_price)
    duration_hours = experience.get("duration_hours")
    duration = f"{duration_hours} hours"

    content = f"""
    Experience: {name}
    Description: {experience.get('description')}
    Location: {city}, {experience.get('country')}
    Duration: {duration}
    Price: ${price}
    Tags: {experience.get('tags')}
    """

    return Document(
        page_content=content.strip(),
        metadata={
            "experience_id": experience.get("experience_id"),
            "name": name,
            "city": city,
            "price": price,
            "duration": duration,
            "tags": experience.get("tags"),
            "type": "experience",
        },
    )


def create_flight_document(flight: Dict[str, Any]) -> Document:
    """Create a Document from flight data following FlightRecommendation schema."""
    airline = flight.get("operating_airline")
    from_airport = flight.get("airport_depart")
    to_airport = flight.get("airport_arrive")
    date = flight.get("depart_date")
    flight_duration_pt = flight.get("flight_duration")
    duration = convert_duration_to_string(flight_duration_pt)
    price = get_random_cabin_price()
    depart_city = flight.get("city_depart")
    arrive_city = flight.get("city_arrive")

    content = f"""
    Flight: {airline} {flight.get('flight_number')}
    Route: {from_airport} ({depart_city}) to {to_airport} ({arrive_city})
    Departure: {flight.get('depart')}
    Arrival: {flight.get('arrive')}
    Date: {date}
    Duration: {duration}
    Price: ${price}
    Aircraft: {flight.get('plane_type')}
    """

    return Document(
        page_content=content.strip(),
        metadata={
            "flight_id": flight.get("flight_id"),
            "airline": airline,
            "from_airport": from_airport,
            "to_airport": to_airport,
            "price": price,
            "duration": duration,
            "date": date,
            "flight_number": flight.get("flight_number"),
            "type": "flight",
        },
    )


def populate_hotels_store():
    """Populate the hotels vector store with all hotel data."""
    if len(hotels_store.get()["documents"]) == 0:
        documents = [create_hotel_document(hotel) for hotel in hotels]
        uuids = [str(uuid4()) for _ in range(len(documents))]
        batch_size = 100
        total_added = 0

        for i in range(0, len(documents), batch_size):
            batch_documents = documents[i : i + batch_size]
            batch_uuids = uuids[i : i + batch_size]
            hotels_store.add_documents(documents=batch_documents, ids=batch_uuids)
            total_added += len(batch_documents)

    else:
        print(
            f"Hotels store is already populated with {len(hotels_store.get()['ids'])} documents"
        )


def populate_experiences_store():
    """Populate the experiences vector store with all experience data."""
    if len(experiences_store.get()["documents"]) == 0:
        documents = [create_experience_document(exp) for exp in experiences]
        uuids = [str(uuid4()) for _ in range(len(documents))]
        batch_size = 100
        total_added = 0

        for i in range(0, len(documents), batch_size):
            batch_documents = documents[i : i + batch_size]
            batch_uuids = uuids[i : i + batch_size]
            experiences_store.add_documents(documents=batch_documents, ids=batch_uuids)
            total_added += len(batch_documents)

    else:
        print(
            f"Experiences store is already populated with {len(experiences_store.get()['ids'])} documents"
        )


def populate_flights_store():
    """Populate the flights vector store with all flight data."""
    if len(flights_store.get()["documents"]) == 0:
        documents = [create_flight_document(flight) for flight in flights]
        uuids = [str(uuid4()) for _ in range(len(documents))]
        batch_size = 100
        total_added = 0

        for i in range(0, len(documents), batch_size):
            batch_documents = documents[i : i + batch_size]
            batch_uuids = uuids[i : i + batch_size]
            flights_store.add_documents(documents=batch_documents, ids=batch_uuids)
            total_added += len(batch_documents)
    else:
        print(
            f"Flights store is already populated with {len(flights_store.get()['ids'])} documents"
        )


def search_hotels(
    query: str, k: int = 5, filter_dict: Optional[Dict[str, Any]] = None
) -> List[Document]:
    """Search hotels using semantic similarity."""
    return hotels_store.similarity_search(query, k=k, filter=filter_dict)


def search_experiences(
    query: str, k: int = 5, filter_dict: Optional[Dict[str, Any]] = None
) -> List[Document]:
    """Search experiences using semantic similarity."""
    return experiences_store.similarity_search(query, k=k, filter=filter_dict)


def search_flights(
    query: str, k: int = 5, filter_dict: Optional[Dict[str, Any]] = None
) -> List[Document]:
    """Search flights using semantic similarity."""
    return flights_store.similarity_search(query, k=k, filter=filter_dict)


def search_hotels_with_score(
    query: str, k: int = 5, filter_dict: Optional[Dict[str, Any]] = None
) -> List[tuple]:
    """Search hotels with similarity scores."""
    return hotels_store.similarity_search_with_score(query, k=k, filter=filter_dict)


def search_experiences_with_score(
    query: str, k: int = 5, filter_dict: Optional[Dict[str, Any]] = None
) -> List[tuple]:
    """Search experiences with similarity scores."""
    return experiences_store.similarity_search_with_score(
        query, k=k, filter=filter_dict
    )


def search_flights_with_score(
    query: str, k: int = 5, filter_dict: Optional[Dict[str, Any]] = None
) -> List[tuple]:
    """Search flights with similarity scores."""
    return flights_store.similarity_search_with_score(query, k=k, filter=filter_dict)


def initialise_all_stores() -> Dict[str, int]:
    """Initialize all vector stores with data."""
    populate_hotels_store()
    populate_experiences_store()
    populate_flights_store()


def search_all_stores(query: str, k: int = 5) -> Dict[str, List[Document]]:
    """Search across all vector stores and return results."""
    return {
        "hotels": search_hotels(query, k),
        "experiences": search_experiences(query, k),
        "flights": search_flights(query, k),
    }


def delete_all_stores():
    """Delete all vector stores."""
    hotels_store.delete_collection()
    experiences_store.delete_collection()
    flights_store.delete_collection()
