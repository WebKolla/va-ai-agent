"""
Tests for AI agents and their functionality.
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from langchain_core.documents import Document
from pydantic_ai.models.test import TestModel

from app.agents.experience_agent import experience_agent, experience_search
from app.agents.flight_agent import flight_agent, flight_search
from app.agents.hotel_agent import hotel_agent, hotel_search
from app.agents.manager_agent import get_hotel_recommendations, manager_agent
from app.schemas import (
    ExperienceRecommendation,
    FlightRecommendation,
    HotelRecommendation,
)


class TestManagerAgent:
    """Test the manager agent coordination."""

    @pytest.mark.asyncio
    async def test_manager_agent_with_test_model(self):
        """Test manager agent using TestModel."""
        agent_deps = {
            "hotel_agent": Mock(),
            "flights_agent": Mock(),
            "experience_agent": Mock(),
        }

        hotel_result = Mock()
        hotel_result.output = HotelRecommendation(
            name="Test Hotel", city="Paris", price_per_night=200.0, rating=4.5
        )
        agent_deps["hotel_agent"].run = AsyncMock(return_value=hotel_result)

        flight_result = Mock()
        flight_result.output = FlightRecommendation(
            airline="Virgin Atlantic",
            from_airport="LHR",
            to_airport="CDG",
            price=300.0,
            duration="1h 30m",
            date="2024-07-01",
        )
        agent_deps["flights_agent"].run = AsyncMock(return_value=flight_result)

        experience_result = Mock()
        experience_result.output = ExperienceRecommendation(
            name="Eiffel Tower", city="Paris", price=25.0, duration="2 hours"
        )
        agent_deps["experience_agent"].run = AsyncMock(return_value=experience_result)

        with manager_agent.override(model=TestModel()):
            result = await manager_agent.run("I want to visit Paris", deps=agent_deps)

        assert result.output is not None
        assert hasattr(result.output, "destination")
        assert hasattr(result.output, "reason")
        assert hasattr(result.output, "budget")
        assert hasattr(result.output, "tips")

    @pytest.mark.asyncio
    async def test_get_hotel_recommendations_tool(self):
        """Test the hotel recommendations tool."""
        mock_hotel_agent = Mock()
        mock_result = Mock()
        mock_result.output = HotelRecommendation(
            name="Test Hotel", city="London", price_per_night=150.0, rating=4.0
        )
        mock_hotel_agent.run = AsyncMock(return_value=mock_result)

        agent_deps = {"hotel_agent": mock_hotel_agent}

        mock_ctx = Mock()
        mock_ctx.deps = agent_deps

        result = await get_hotel_recommendations(mock_ctx, "luxury hotel in London")

        assert isinstance(result, HotelRecommendation)
        assert result.name == "Test Hotel"
        assert result.city == "London"
        mock_hotel_agent.run.assert_called_once_with(
            "luxury hotel in London", deps="luxury hotel in London"
        )


class TestHotelAgent:
    """Test hotel agent functionality."""

    @pytest.mark.asyncio
    @patch("app.agents.hotel_agent.search_hotels_with_score")
    async def test_hotel_search_tool(self, mock_search):
        """Test hotel search tool."""
        mock_doc = Document(
            page_content="Test hotel content",
            metadata={
                "name": "Test Hotel",
                "city": "London",
                "price_per_night": 200.0,
                "rating": 4.5,
            },
        )
        mock_search.return_value = [(mock_doc, 0.9)]

        result = await hotel_search("luxury hotel", location="London")

        assert len(result) == 1
        assert result[0]["name"] == "Test Hotel"
        assert result[0]["city"] == "London"
        assert result[0]["price_per_night"] == 200.0
        assert result[0]["rating"] == 4.5
        assert result[0]["similarity_score"] == 0.9

    @pytest.mark.asyncio
    @patch("app.agents.hotel_agent.search_hotels_with_score")
    async def test_hotel_search_with_filters(self, mock_search):
        """Test hotel search with price and rating filters."""
        mock_doc1 = Document(
            page_content="Expensive hotel",
            metadata={
                "name": "Expensive Hotel",
                "city": "London",
                "price_per_night": 500.0,
                "rating": 5.0,
            },
        )
        mock_doc2 = Document(
            page_content="Budget hotel",
            metadata={
                "name": "Budget Hotel",
                "city": "London",
                "price_per_night": 100.0,
                "rating": 3.0,
            },
        )
        mock_search.return_value = [(mock_doc1, 0.9), (mock_doc2, 0.8)]
        result = await hotel_search("hotel", max_price=300.0, min_rating=3.5)
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_hotel_agent_with_test_model(self):
        """Test hotel agent using TestModel."""
        with hotel_agent.override(model=TestModel()):
            result = await hotel_agent.run(
                "Find me a luxury hotel in London",
                deps="Find me a luxury hotel in London",
            )

        assert isinstance(result.output, HotelRecommendation)
        assert result.output.name is not None
        assert result.output.city is not None
        assert result.output.price_per_night >= 0
        assert result.output.rating >= 0


class TestFlightAgent:
    """Test flight agent functionality."""

    @pytest.mark.asyncio
    @patch("app.agents.flight_agent.search_flights_with_score")
    async def test_flight_search_tool(self, mock_search):
        """Test flight search tool."""
        mock_doc = Document(
            page_content="Test flight content",
            metadata={
                "airline": "Virgin Atlantic",
                "from_airport": "LHR",
                "to_airport": "JFK",
                "price": 500.0,
                "duration": "8h 0m",
                "date": "2024-07-01",
            },
        )
        mock_search.return_value = [(mock_doc, 0.95)]

        result = await flight_search(
            "flight from London", from_city="London", to_city="New York"
        )

        assert len(result) == 1
        assert result[0]["airline"] == "Virgin Atlantic"
        assert result[0]["from_airport"] == "LHR"
        assert result[0]["to_airport"] == "JFK"
        assert result[0]["price"] == 500.0
        assert result[0]["similarity_score"] == 0.95

    @pytest.mark.asyncio
    async def test_flight_agent_with_test_model(self):
        """Test flight agent using TestModel."""
        with flight_agent.override(model=TestModel()):
            result = await flight_agent.run(
                "Find me flights from London to New York",
                deps="Find me flights from London to New York",
            )

        assert isinstance(result.output, FlightRecommendation)
        assert result.output.airline is not None
        assert result.output.from_airport is not None
        assert result.output.to_airport is not None
        assert result.output.price >= 0


class TestExperienceAgent:
    """Test experience agent functionality."""

    @pytest.mark.asyncio
    @patch("app.agents.experience_agent.search_experiences_with_score")
    async def test_experience_search_tool(self, mock_search):
        """Test experience search tool."""
        mock_doc = Document(
            page_content="Test experience content",
            metadata={
                "name": "London Eye",
                "city": "London",
                "price": 50.0,
                "duration": "2 hours",
            },
        )
        mock_search.return_value = [(mock_doc, 0.85)]

        result = await experience_search("sightseeing", location="London")

        assert len(result) == 1
        assert result[0]["name"] == "London Eye"
        assert result[0]["city"] == "London"
        assert result[0]["price"] == 50.0
        assert result[0]["duration"] == "2 hours"

    @pytest.mark.asyncio
    async def test_experience_agent_with_test_model(self):
        """Test experience agent using TestModel."""
        with experience_agent.override(model=TestModel()):
            result = await experience_agent.run(
                "Find me fun activities in Paris",
                deps="Find me fun activities in Paris",
            )

        assert isinstance(result.output, ExperienceRecommendation)
        assert result.output.name is not None
        assert result.output.city is not None
        assert result.output.price >= 0
        assert result.output.duration is not None
