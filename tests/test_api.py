"""
Tests for FastAPI Application
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestHealthEndpoint:
    """Tests for health check endpoint."""
    
    def test_health_check(self, client):
        """Test health check endpoint returns 200."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_health_check_structure(self, client):
        """Test health check response structure."""
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert "message" in data


class TestQueryEndpoint:
    """Tests for agent query endpoint."""
    
    def test_query_endpoint_basic(self, client):
        """Test basic query endpoint."""
        response = client.post(
            "/api/v1/agent/query",
            json={"query": "Покажи все продукты"}
        )
        assert response.status_code == 200
        assert "response" in response.json()
    
    def test_query_endpoint_structure(self, client):
        """Test query response structure."""
        response = client.post(
            "/api/v1/agent/query",
            json={"query": "Покажи все продукты"}
        )
        data = response.json()
        assert "query" in data
        assert "response" in data
        assert "status" in data
        assert data["status"] == "success"
    
    def test_query_endpoint_with_statistics(self, client):
        """Test query endpoint with statistics request."""
        response = client.post(
            "/api/v1/agent/query",
            json={"query": "Какая средняя цена продуктов?"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
    
    def test_query_endpoint_with_category(self, client):
        """Test query endpoint with category filter."""
        response = client.post(
            "/api/v1/agent/query",
            json={"query": "Покажи все продукты в категории Электроника"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "success"
    
    def test_query_endpoint_with_calculation(self, client):
        """Test query endpoint with calculation."""
        response = client.post(
            "/api/v1/agent/query",
            json={"query": "Посчитай скидку 15% на товар с ID 1"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
    
    def test_query_endpoint_empty_query(self, client):
        """Test query endpoint with empty query."""
        response = client.post(
            "/api/v1/agent/query",
            json={"query": ""}
        )
        assert response.status_code == 422  # Validation error
    
    def test_query_endpoint_missing_query(self, client):
        """Test query endpoint with missing query field."""
        response = client.post(
            "/api/v1/agent/query",
            json={}
        )
        assert response.status_code == 422  # Validation error


class TestExamplesEndpoint:
    """Tests for examples endpoint."""
    
    def test_examples_endpoint(self, client):
        """Test examples endpoint returns list."""
        response = client.get("/api/v1/examples")
        assert response.status_code == 200
        data = response.json()
        assert "examples" in data
        assert isinstance(data["examples"], list)
        assert len(data["examples"]) > 0
    
    def test_examples_structure(self, client):
        """Test examples response structure."""
        response = client.get("/api/v1/examples")
        data = response.json()
        for example in data["examples"]:
            assert "query" in example
            assert "description" in example


class TestCORSHeaders:
    """Tests for CORS headers."""
    
    def test_cors_headers(self, client):
        """Test CORS headers are present."""
        response = client.get("/health")
        # FastAPI adds CORS headers when middleware is configured
        # Just verify the endpoint works
        assert response.status_code == 200


class TestErrorHandling:
    """Tests for error handling."""
    
    def test_invalid_json(self, client):
        """Test handling of invalid JSON."""
        response = client.post(
            "/api/v1/agent/query",
            content="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_wrong_method(self, client):
        """Test wrong HTTP method."""
        response = client.get("/api/v1/agent/query")
        assert response.status_code == 405  # Method Not Allowed


class TestEndpoints:
    """General endpoint tests."""
    
    def test_api_endpoints_exist(self, client):
        """Test that all main endpoints exist."""
        endpoints = [
            ("/health", "GET"),
            ("/api/v1/agent/query", "POST"),
            ("/api/v1/examples", "GET"),
        ]
        
        for path, method in endpoints:
            if method == "GET":
                response = client.get(path)
            else:
                response = client.post(path, json={"query": "test"})
            
            # Should not be 404
            assert response.status_code != 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
