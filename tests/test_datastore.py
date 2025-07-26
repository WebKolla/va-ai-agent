"""
Tests for datastore functionality and data processing.
"""

from unittest.mock import patch

import pytest
from langchain_core.documents import Document

from app.datastore import (
    convert_duration_to_string,
    create_experience_document,
    create_flight_document,
    create_hotel_document,
    get_random_cabin_price,
    get_random_room_price,
    search_experiences,
    search_flights,
    search_hotels,
)


class TestDurationConversion:
    """Test duration string conversion."""

    def test_convert_duration_hours_minutes(self):
        """Test conversion with hours and minutes."""
        result = convert_duration_to_string("PT2H30M")
        assert result == "2h 30m"

    def test_convert_duration_hours_only(self):
        """Test conversion with hours only."""
        result = convert_duration_to_string("PT5H")
        assert result == "5h"

    def test_convert_duration_minutes_only(self):
        """Test conversion with minutes only."""
        result = convert_duration_to_string("PT45M")
        assert result == "45m"

    def test_convert_duration_invalid_format(self):
        """Test conversion with invalid format."""
        with pytest.raises(ValueError, match="Invalid duration format"):
            convert_duration_to_string("invalid")

    def test_convert_duration_no_time_found(self):
        """Test conversion with no valid time components."""
        with pytest.raises(ValueError, match="No valid duration found"):
            convert_duration_to_string("PT")


class TestPriceGeneration:
    """Test random price generation."""

    @patch("app.datastore.random.randint")
    def test_get_random_room_price(self, mock_randint):
        """Test random room price generation."""
        mock_randint.return_value = 250
        price = get_random_room_price()
        assert price == 250.0
        mock_randint.assert_called_once_with(100, 1000)

    @patch("app.datastore.random.randint")
    def test_get_random_cabin_price(self, mock_randint):
        """Test random cabin price generation."""
        mock_randint.return_value = 500
        price = get_random_cabin_price()
        assert price == 500.0
        mock_randint.assert_called_once_with(100, 1000)


class TestDocumentCreation:
    """Test document creation functions."""

    @patch("app.datastore.get_random_room_price")
    def test_create_hotel_document(self, mock_price):
        """Test hotel document creation."""
        mock_price.return_value = 200.0

        hotel_data = {
            "hotel_id": "hotel_123",
            "hotel_name": "Test Hotel",
            "hotel_description": "A lovely test hotel",
            "city": "London",
            "country": "UK",
            "rating": "4.5",
            "pricing_tier": "luxury",
            "amenities": "WiFi, Pool, Spa",
        }

        doc = create_hotel_document(hotel_data)

        assert isinstance(doc, Document)
        assert "Test Hotel" in doc.page_content
        assert "London, UK" in doc.page_content
        assert "4.5 stars" in doc.page_content
        assert "$200" in doc.page_content

        assert doc.metadata["hotel_id"] == "hotel_123"
        assert doc.metadata["name"] == "Test Hotel"
        assert doc.metadata["city"] == "London"
        assert doc.metadata["price_per_night"] == 200.0
        assert doc.metadata["rating"] == 4.5
        assert doc.metadata["type"] == "hotel"

    def test_create_experience_document(self):
        """Test experience document creation."""
        experience_data = {
            "experience_id": "exp_123",
            "title": "London Eye",
            "description": "Iconic observation wheel",
            "city": "London",
            "country": "UK",
            "base_price": "50.0",
            "duration_hours": "2",
            "tags": ["sightseeing", "landmark"],
        }

        doc = create_experience_document(experience_data)

        assert isinstance(doc, Document)
        assert "London Eye" in doc.page_content
        assert "London, UK" in doc.page_content
        assert "2 hours" in doc.page_content
        assert "$50" in doc.page_content

        assert doc.metadata["experience_id"] == "exp_123"
        assert doc.metadata["name"] == "London Eye"
        assert doc.metadata["city"] == "London"
        assert doc.metadata["price"] == 50.0
        assert doc.metadata["duration"] == "2 hours"
        assert doc.metadata["type"] == "experience"

    @patch("app.datastore.get_random_cabin_price")
    def test_create_flight_document(self, mock_price):
        """Test flight document creation."""
        mock_price.return_value = 500.0

        flight_data = {
            "flight_id": "flight_123",
            "operating_airline": "Virgin Atlantic",
            "flight_number": "VS123",
            "airport_depart": "LHR",
            "airport_arrive": "JFK",
            "city_depart": "London",
            "city_arrive": "New York",
            "depart": "10:00",
            "arrive": "18:00",
            "depart_date": "2024-07-01",
            "flight_duration": "PT8H0M",
            "plane_type": "Boeing 787",
        }

        doc = create_flight_document(flight_data)

        assert isinstance(doc, Document)
        assert "Virgin Atlantic VS123" in doc.page_content
        assert "LHR (London) to JFK (New York)" in doc.page_content
        assert "8h" in doc.page_content
        assert "$500" in doc.page_content

        assert doc.metadata["flight_id"] == "flight_123"
        assert doc.metadata["airline"] == "Virgin Atlantic"
        assert doc.metadata["from_airport"] == "LHR"
        assert doc.metadata["to_airport"] == "JFK"
        assert doc.metadata["price"] == 500.0
        assert doc.metadata["duration"] == "8h"
        assert doc.metadata["type"] == "flight"


class TestSearchFunctions:
    """Test vector store search functions."""

    @patch("app.datastore.hotels_store")
    def test_search_hotels(self, mock_store):
        """Test hotel search functionality."""
        mock_doc = Document(page_content="Test hotel", metadata={"name": "Test Hotel"})
        mock_store.similarity_search.return_value = [mock_doc]

        results = search_hotels("luxury hotel in London", k=3)

        assert len(results) == 1
        assert results[0].metadata["name"] == "Test Hotel"
        mock_store.similarity_search.assert_called_once_with(
            "luxury hotel in London", k=3, filter=None
        )

    @patch("app.datastore.experiences_store")
    def test_search_experiences(self, mock_store):
        """Test experience search functionality."""
        mock_doc = Document(
            page_content="Test experience", metadata={"name": "Test Experience"}
        )
        mock_store.similarity_search.return_value = [mock_doc]

        results = search_experiences("sightseeing in Paris", k=5)

        assert len(results) == 1
        assert results[0].metadata["name"] == "Test Experience"
        mock_store.similarity_search.assert_called_once_with(
            "sightseeing in Paris", k=5, filter=None
        )

    @patch("app.datastore.flights_store")
    def test_search_flights(self, mock_store):
        """Test flight search functionality."""
        mock_doc = Document(
            page_content="Test flight", metadata={"airline": "Test Airline"}
        )
        mock_store.similarity_search.return_value = [mock_doc]

        results = search_flights("London to New York", k=10)

        assert len(results) == 1
        assert results[0].metadata["airline"] == "Test Airline"
        mock_store.similarity_search.assert_called_once_with(
            "London to New York", k=10, filter=None
        )
