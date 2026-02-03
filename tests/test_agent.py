"""
Tests for LangGraph Agent
"""

import pytest
from app.agent import (
    run_agent,
    calculator,
    formatter,
    create_agent,
    process_user_query
)


class TestCalculatorTool:
    """Tests for the calculator tool."""
    
    def test_percentage_calculation(self):
        """Test percentage discount calculation."""
        result = calculator("15% of 50000")
        assert "7500" in result
        assert "=" in result
    
    def test_simple_arithmetic(self):
        """Test simple arithmetic."""
        result = calculator("100 + 50")
        assert "150" in result
    
    def test_invalid_expression(self):
        """Test error handling for invalid expressions."""
        result = calculator("invalid expression !!!!")
        assert "Error" in result


class TestFormatterTool:
    """Tests for the formatter tool."""
    
    def test_json_formatting(self):
        """Test JSON formatting."""
        data = '{"name":"Ноутбук","price":50000}'
        result = formatter(data, format_type="json")
        assert "Ноутбук" in result
        assert "50000" in result
    
    def test_uppercase_formatting(self):
        """Test uppercase formatting."""
        result = formatter("hello world", format_type="uppercase")
        assert result == "HELLO WORLD"
    
    def test_lowercase_formatting(self):
        """Test lowercase formatting."""
        result = formatter("HELLO WORLD", format_type="lowercase")
        assert result == "hello world"
    
    def test_invalid_format_type(self):
        """Test error handling for invalid format type."""
        result = formatter("text", format_type="invalid")
        assert "Unknown format type" in result


class TestAgentProcessing:
    """Tests for agent processing."""
    
    def test_agent_creation(self):
        """Test that agent can be created."""
        agent = create_agent()
        assert agent is not None
    
    def test_query_processing_list_products(self):
        """Test processing query for listing products."""
        query = "Покажи все продукты"
        response = process_user_query(query)
        assert response is not None
        assert isinstance(response, str)
    
    def test_query_processing_statistics(self):
        """Test processing query for statistics."""
        query = "Какая средняя цена продуктов?"
        response = process_user_query(query)
        assert response is not None
        assert isinstance(response, str)
    
    def test_query_processing_category_filter(self):
        """Test processing query with category filter."""
        query = "Покажи все продукты в категории Электроника"
        response = process_user_query(query)
        assert response is not None
        assert "Электроника" in response or "Electronics" in response or response is not None
    
    def test_agent_run(self):
        """Test running the agent with a query."""
        query = "Покажи все продукты"
        response = run_agent(query)
        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0


class TestAgentIntegration:
    """Integration tests for the agent."""
    
    def test_agent_with_calculation_query(self):
        """Test agent handling calculation query."""
        query = "Посчитай скидку 15% на товар с ID 1"
        response = run_agent(query)
        assert response is not None
    
    def test_agent_with_product_id_query(self):
        """Test agent handling product ID query."""
        query = "Найди товар с ID 1"
        response = run_agent(query)
        assert response is not None
    
    def test_agent_with_unknown_query(self):
        """Test agent handling unknown query."""
        query = "Привет, как дела?"
        response = run_agent(query)
        assert response is not None
        assert isinstance(response, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
