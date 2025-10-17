from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestMainEndpoints:
    """Test suite for main application endpoints"""

    def test_home_page_loads(self):
        """Test that the home page loads successfully"""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_home_page_contains_mystical_journeys(self):
        """Test that home page contains the app title"""
        response = client.get("/")
        assert "Mystical Journeys" in response.text
        assert "Describe Your Quest" in response.text

    def test_static_files_accessible(self):
        """Test that static files are accessible"""
        # Test CSS file
        response = client.get("/static/style.css")
        assert response.status_code == 200
        assert "text/css" in response.headers["content-type"]

        # Test JS file
        response = client.get("/static/app.js")
        assert response.status_code == 200
        assert (
            "javascript" in response.headers["content-type"]
            or "text/plain" in response.headers["content-type"]
        )


class TestRequestValidation:
    """Test suite for request validation"""

    def test_travel_request_model_validation(self):
        """Test TravelRequest model validation"""
        # Test with missing destination
        response = client.post(
            "/generate-comparison",
            json={"days": 7, "budget": "moderate", "interests": ["magical_creatures"]},
        )
        assert response.status_code == 422

        # Test with invalid days type
        response = client.post(
            "/generate-comparison",
            json={
                "destination": "Floating Islands of Aetheria",
                "days": "seven",  # Should be int
                "budget": "moderate",
                "interests": ["sky_adventures"],
            },
        )
        assert response.status_code == 422

    def test_interests_list_validation(self):
        """Test that interests field accepts list of strings"""
        response = client.post(
            "/generate-comparison",
            json={
                "destination": "Underwater Kingdom of Aquatillia",
                "days": 3,
                "budget": "luxury",
                "interests": "underwater_realms",  # Should be list
                "providers": ["claude"],
            },
        )
        assert response.status_code == 422


class TestErrorHandling:
    """Test suite for error handling scenarios"""

    def test_nonexistent_endpoint(self):
        """Test 404 for nonexistent endpoints"""
        response = client.get("/nonexistent")
        assert response.status_code == 404

    def test_invalid_method_on_comparison_endpoint(self):
        """Test that only POST is allowed on comparison endpoint"""
        response = client.get("/generate-comparison")
        assert response.status_code == 405  # Method not allowed

    def test_malformed_json_request(self):
        """Test handling of malformed JSON"""
        response = client.post(
            "/generate-comparison",
            data="{invalid json}",
            headers={"content-type": "application/json"},
        )
        assert response.status_code == 422


class TestEnvironmentConfiguration:
    """Test suite for environment and configuration"""

    @patch.dict("os.environ", {}, clear=True)
    def test_missing_api_key_handling(self):
        """Test that missing API key is handled gracefully"""
        # This should not crash the application
        response = client.get("/")
        assert response.status_code == 200


class TestBookingResponse:
    """Test suite for booking response functionality"""

    def test_booking_response_invalid_provider(self):
        """Test booking response with invalid provider"""
        response = client.post(
            "/generate-booking-response",
            json={"provider": "invalid_provider", "itinerary": "Test Itinerary"},
        )
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "Invalid provider" in data["error"]

    def test_booking_response_missing_provider(self):
        """Test booking response with missing provider"""
        response = client.post(
            "/generate-booking-response", json={"itinerary": "Test Itinerary"}
        )
        assert response.status_code == 422  # Unprocessable Entity
        data = response.json()
        assert "detail" in data
        # Check that the error message indicates the 'provider' field is missing
        assert any(
            "provider" in error["loc"] and "Field required" in error["msg"]
            for error in data["detail"]
        )


if __name__ == "__main__":
    pytest.main(["-v", "tests/"])
