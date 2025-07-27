"""
Tests for utility functions.
"""

from unittest.mock import Mock, patch

import pytest

from app.validators.api.api_key_validator import check_api_key
from app.validators.user_query.user_query_validator import validate_user_query


class TestCheckApiKey:
    """Test API key validation."""

    @patch.dict("os.environ", {"OPENAI_API_KEY": "valid-key-1234567890"})
    def test_check_api_key_valid(self):
        """Test check_api_key with valid key."""
        assert check_api_key() is True

    @patch.dict("os.environ", {}, clear=True)
    def test_check_api_key_missing(self):
        """Test check_api_key with missing key."""
        with pytest.raises(ValueError, match="OPENAI_API_KEY is not set"):
            check_api_key()

    @patch.dict("os.environ", {"OPENAI_API_KEY": "short"})
    def test_check_api_key_too_short(self):
        """Test check_api_key with too short key."""
        with pytest.raises(ValueError, match="OPENAI_API_KEY is too short"):
            check_api_key()


class TestValidateUserQuery:
    """Test user query validation."""

    @pytest.mark.asyncio
    async def test_validate_empty_query(self):
        """Test validation with empty query."""
        result = await validate_user_query("")
        assert result["is_safe"] is False
        assert "provide a travel query" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_validate_short_query(self):
        """Test validation with too short query."""
        result = await validate_user_query("hi")
        assert result["is_safe"] is False
        assert "too short" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_suspicious_xss_pattern(self):
        """Test with XSS pattern"""
        result = await validate_user_query("Find hotels <script>alert('xss')</script> ")

        assert result["is_safe"] is False
        assert "inappropriate content" in result["message"]

    @pytest.mark.asyncio
    async def test_suspicious_sql_injection_pattern(self):
        """Test with SQL injection pattern"""
        result = await validate_user_query("Find hotels union select * from users")

        assert result["is_safe"] is False
        assert "inappropriate content" in result["message"]

    @pytest.mark.asyncio
    async def test_suspicious_javascript_pattern(self):
        """Test with JavaScript pattern"""
        result = await validate_user_query(
            "Find hotels javascript:alert('hello world')"
        )

        assert result["is_safe"] is False
        assert "inappropriate content" in result["message"]

    @pytest.mark.asyncio
    async def test_gambling_keywords(self):
        """Test with gambling keywords"""
        gambling_queries = [
            "Find casinos in Las Vegas",
            "Where can I go gambling?",
            "Show me poker rooms",
            "I want to play blackjack",
        ]

        for query in gambling_queries:
            result = await validate_user_query(query)
            assert result["is_safe"] is False

    @pytest.mark.asyncio
    async def test_travel_related_query(self):
        """Test with travel related query"""
        result = await validate_user_query("Hi, how are you?")
        assert result["is_safe"] is False

    @pytest.mark.asyncio
    @patch("openai.OpenAI")
    async def test_validate_appropriate_query(self, mock_openai):
        """Test validation with appropriate travel query."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_result = Mock()
        mock_result.flagged = False
        mock_response.results = [mock_result]
        mock_client.moderations.create.return_value = mock_response

        result = await validate_user_query("I want to visit Paris for vacation")
        assert result["is_safe"] is True
        assert result["message"] == "Valid user query"

    @pytest.mark.asyncio
    @patch("openai.OpenAI")
    async def test_validate_flagged_content(self, mock_openai):
        """Test validation with flagged content."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_result = Mock()
        mock_result.flagged = True
        mock_response.results = [mock_result]
        mock_client.moderations.create.return_value = mock_response

        result = await validate_user_query("inappropriate content")
        assert result["is_safe"] is False
