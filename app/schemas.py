from typing import List, Optional

from pydantic import BaseModel, Field


class TravelQuery(BaseModel):
    """Request body schema for user travel query."""

    query: str = Field(
        ..., example="Looking for a romantic beach getaway in Europe during July"
    )


class HotelRecommendation(BaseModel):
    name: str = Field(..., example="The Savoy")
    city: str = Field(..., example="London")
    price_per_night: float = Field(..., example=100)
    rating: float = Field(..., example=4.5)


class FlightRecommendation(BaseModel):
    airline: str = Field(..., example="Virgin Atlantic")
    from_airport: str = Field(..., example="London")
    to_airport: str = Field(..., example="Paris")
    price: float = Field(..., example=100)
    duration: str = Field(..., example="1h 30m")
    date: str = Field(..., example="2025-08-01")


class ExperienceRecommendation(BaseModel):
    name: str = Field(..., example="Eiffel Tower")
    city: str = Field(..., example="Paris")
    price: float = Field(..., example=100)
    duration: str = Field(..., example="1h 30m")


class TravelAdvice(BaseModel):
    """Structured response returned by the Gen-AI Travel Assistant."""

    destination: str = Field(..., example="Paris")
    reason: str = Field(..., example="The Eiffel Tower is a beautiful landmark")
    budget: str = Field(..., example="Budget")
    tips: List[str] = Field(
        ...,
        example=[
            "Visit the Eiffel Tower at night",
            "Take a boat tour on the Seine",
            "Visit the Louvre",
        ],
    )

    # Optional enrichments
    hotel: Optional[HotelRecommendation] = None
    flight: Optional[FlightRecommendation] = None
    experience: Optional[ExperienceRecommendation] = None
