"""
FastAPI Application for AI Agent with MCP Integration
Provides REST API endpoints for querying the agent
"""

import logging
from typing import Any
from pydantic import BaseModel, Field
import uvicorn

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.agent import run_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Agent API",
    description="REST API for querying AI Agent with MCP integration",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# MODELS
# ============================================================================

class QueryRequest(BaseModel):
    """Request model for agent query."""
    query: str = Field(..., min_length=1, description="User query for the agent")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Покажи все продукты в категории Электроника"
            }
        }


class QueryResponse(BaseModel):
    """Response model for agent query."""
    query: str = Field(description="The query that was processed")
    response: str = Field(description="The agent's response")
    status: str = Field(description="Status of the query processing")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Покажи все продукты в категории Электроника",
                "response": "Products in Электроника: {...}",
                "status": "success"
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    message: str


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    
    Returns:
        Health status of the API
    """
    return HealthResponse(
        status="healthy",
        message="API is running"
    )


@app.post("/api/v1/agent/query", response_model=QueryResponse, tags=["Agent"])
async def query_agent(request: QueryRequest) -> QueryResponse:
    """
    Send a query to the AI agent.
    
    This endpoint processes user queries through the LangGraph agent,
    which connects to the MCP server for product management operations.
    
    Args:
        request: Query request with user query string
        
    Returns:
        Agent response with query and result
        
    Raises:
        HTTPException: If query processing fails
    """
    try:
        logger.info(f"Received query: {request.query}")
        
        # Process query through agent
        response = run_agent(request.query)
        
        logger.info(f"Agent response: {response}")
        
        return QueryResponse(
            query=request.query,
            response=response,
            status="success"
        )
    
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


@app.get("/api/v1/examples", tags=["Examples"])
async def get_examples() -> dict[str, Any]:
    """
    Get example queries that can be used with the agent.
    
    Returns:
        List of example queries
    """
    return {
        "examples": [
            {
                "query": "Покажи все продукты",
                "description": "Get all products"
            },
            {
                "query": "Покажи все продукты в категории Электроника",
                "description": "Get products in Electronics category"
            },
            {
                "query": "Какая средняя цена продуктов?",
                "description": "Get average product price"
            },
            {
                "query": "Найди товар с ID 1",
                "description": "Get product by ID"
            },
            {
                "query": "Посчитай скидку 15% на товар с ID 1",
                "description": "Calculate 15% discount on product with ID 1"
            }
        ]
    }


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle ValueError exceptions."""
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )


# ============================================================================
# STARTUP/SHUTDOWN EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Handle startup events."""
    logger.info("API startup")


@app.on_event("shutdown")
async def shutdown_event():
    """Handle shutdown events."""
    logger.info("API shutdown")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )
