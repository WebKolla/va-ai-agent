"""
Tests for the main FastAPI application and endpoints.
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas import (
    ExperienceRecommendation,
    FlightRecommendation,
    HotelRecommendation,
    TravelAdvice,
)


@pytest.fixture
def client():
    return TestClient(app)


class TestHealthEndpoints:
    """Test health and status endpoints."""

    def test_root_endpoint(self, client):
        """Test the root endpoint returns correct message."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Travel Assistant API is running"}

    def test_health_check_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


class TestTravelAssistantEndpoint:
    """Test the main travel assistant endpoint."""

    @patch("app.main.check_api_key")
    @patch("app.main.validate_user_query")
    @patch("app.main.manager_agent")
    def test_travel_assistant_success(
        self, mock_manager, mock_validate, mock_api_key, client
    ):
        """Test successful travel assistant request."""
        mock_api_key.return_value = True
        mock_validate.return_value = {"is_safe": True, "message": "Valid query"}

        mock_result = Mock()
        mock_result.output = TravelAdvice(
            destination="Paris",
            reason="Beautiful city with amazing culture",
            budget="Mid-range",
            tips=["Visit the Eiffel Tower", "Try local cuisine"],
            hotel=HotelRecommendation(
                name="Test Hotel", city="Paris", price_per_night=150.0, rating=4.0
            ),
            flight=FlightRecommendation(
                airline="Virgin Atlantic",
                from_airport="LHR",
                to_airport="CDG",
                price=300.0,
                duration="1h 30m",
                date="2024-07-01",
            ),
            experience=ExperienceRecommendation(
                name="Louvre Museum", city="Paris", price=25.0, duration="3 hours"
            ),
        )
        mock_manager.run = AsyncMock(return_value=mock_result)

        response = client.post(
            "/travel-assistant",
            json={"query": "I want to visit Paris for a romantic getaway"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["destination"] == "Paris"
        assert data["reason"] == "Beautiful city with amazing culture"
        assert data["budget"] == "Mid-range"
        assert len(data["tips"]) == 2
        assert data["hotel"]["name"] == "Test Hotel"
        assert data["flight"]["airline"] == "Virgin Atlantic"
        assert data["experience"]["name"] == "Louvre Museum"

    @patch("app.main.check_api_key")
    def test_travel_assistant_no_api_key(self, mock_api_key, client):
        """Test travel assistant when API key is missing."""
        mock_api_key.return_value = False

        response = client.post(
            "/travel-assistant", json={"query": "I want to visit Paris"}
        )

        assert response.status_code == 500
        assert "OpenAI API key is not set" in response.json()["detail"]

    @patch("app.main.check_api_key")
    @patch("app.main.validate_user_query")
    def test_travel_assistant_unsafe_query(self, mock_validate, mock_api_key, client):
        """Test travel assistant with unsafe user query."""
        mock_api_key.return_value = True
        mock_validate.return_value = {
            "is_safe": False,
            "message": "Inappropriate content detected",
        }

        response = client.post(
            "/travel-assistant", json={"query": "inappropriate content"}
        )

        assert response.status_code == 500
        assert "Inappropriate content detected" in response.json()["detail"]

    @patch("app.main.check_api_key")
    @patch("app.main.validate_user_query")
    @patch("app.main.manager_agent")
    def test_travel_assistant_agent_error(
        self, mock_manager, mock_validate, mock_api_key, client
    ):
        """Test travel assistant when manager agent throws error."""
        mock_api_key.return_value = True
        mock_validate.return_value = {"is_safe": True, "message": "Valid"}
        mock_manager.run = AsyncMock(side_effect=Exception("Agent processing error"))

        response = client.post(
            "/travel-assistant", json={"query": "I want to visit Paris"}
        )

        assert response.status_code == 500
        assert "API error: Agent processing error" in response.json()["detail"]

    def test_travel_assistant_invalid_json(self, client):
        """Test travel assistant with invalid request body."""
        response = client.post("/travel-assistant", json={})

        assert response.status_code == 422

    def test_travel_assistant_empty_query(self, client):
        """Test travel assistant with empty query."""
        response = client.post("/travel-assistant", json={"query": ""})

        assert response.status_code == 500
