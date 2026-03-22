"""
Unit tests for the API Health Check endpoint.

Run with:
    cd backend && uv run pytest tests/test_health.py -v
"""

import pytest
from app import create_app


@pytest.fixture
def client():
    """Create a test Flask client."""
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestHealthEndpoint:
    """Test the /api/health/check endpoint."""

    def test_endpoint_exists(self, client):
        """Health check endpoint should be reachable."""
        response = client.get("/api/health/check")
        assert response.status_code == 200

    def test_returns_json(self, client):
        """Response should be valid JSON."""
        response = client.get("/api/health/check")
        data = response.get_json()
        assert data is not None
        assert isinstance(data, dict)

    def test_has_overall_status(self, client):
        """Response should have an overall_status field."""
        response = client.get("/api/health/check")
        data = response.get_json()
        assert "overall_status" in data
        assert data["overall_status"] in ("healthy", "degraded")

    def test_has_services_list(self, client):
        """Response should have a services list with 2 entries."""
        response = client.get("/api/health/check")
        data = response.get_json()
        assert "services" in data
        assert isinstance(data["services"], list)
        assert len(data["services"]) == 2

    def test_llm_service_present(self, client):
        """LLM API service should be in the response."""
        response = client.get("/api/health/check")
        data = response.get_json()
        names = [s["name"] for s in data["services"]]
        assert "LLM API" in names

    def test_zep_service_present(self, client):
        """Zep Cloud service should be in the response."""
        response = client.get("/api/health/check")
        data = response.get_json()
        names = [s["name"] for s in data["services"]]
        assert "Zep Cloud" in names

    def test_service_has_required_fields(self, client):
        """Each service should have name, configured, status fields."""
        response = client.get("/api/health/check")
        data = response.get_json()
        for service in data["services"]:
            assert "name" in service
            assert "configured" in service
            assert "status" in service
            assert isinstance(service["configured"], bool)

    def test_has_config_section(self, client):
        """Response should have a config section."""
        response = client.get("/api/health/check")
        data = response.get_json()
        assert "config" in data
        config = data["config"]
        assert "llm_model" in config
        assert "llm_base_url" in config
        assert "max_retries" in config
        assert "max_wait_seconds" in config

    def test_valid_service_statuses(self, client):
        """Service status should be one of the expected values."""
        valid = {
            "healthy",
            "rate_limited",
            "auth_error",
            "connection_error",
            "not_configured",
            "error",
            "unknown",
        }
        response = client.get("/api/health/check")
        data = response.get_json()
        for service in data["services"]:
            assert service["status"] in valid, (
                f"Unexpected status '{service['status']}' for {service['name']}"
            )


class TestHealthModule:
    """Test the health check module functions."""

    def test_parse_retry_after_import(self):
        """_parse_retry_after should be importable."""
        from app.utils.llm_client import _parse_retry_after

        assert callable(_parse_retry_after)

    def test_health_blueprint_registered(self):
        """Health blueprint should be registered on the app."""
        app = create_app()
        rules = [r.rule for r in app.url_map.iter_rules()]
        assert "/api/health/check" in rules
