"""
Multi-Agent Travel Assistant API.

FastAPI application that coordinates specialised AI agents for hotels, flights,
and experiences to provide comprehensive travel recommendations using Virgin Atlantic
seed data.
"""

import json

from typing import Annotated

from fastapi import FastAPI, HTTPException, Depends
from app.services.logger import Logger, get_logger

from app.validators.api.api_key_validator import check_api_key
from app.validators.user_query.user_query_validator import validate_user_query
from app.validators.response.agents_response_validator import get_all_recommendations

from app.agents.experience_agent import experience_agent
from app.agents.flight_agent import flight_agent
from app.agents.hotel_agent import hotel_agent
from app.agents.manager_agent import manager_agent
from app.schemas import TravelAdvice, TravelQuery


app = FastAPI(
    title="Multi-Agent AI Travel Assistant",
    description="A travel assistant that uses multiple AI agents to plan a trip",
)

agent_deps = {
    "hotel_agent": hotel_agent,
    "flights_agent": flight_agent,
    "experience_agent": experience_agent,
}


@app.post("/travel-assistant", response_model=TravelAdvice)
async def travel_assistant(
    query: TravelQuery, logger: Annotated[Logger, Depends(get_logger)]
):
    """Travel assistant endpoint."""
    try:
        # Check if API key is set
        print("Checking API key")
        has_api_key = check_api_key()
        if not has_api_key:
            logger.error("OpenAI API key is not set")
            raise HTTPException(status_code=500, detail="OpenAI API key is not set")

        # Validate user query
        validation_result = await validate_user_query(query.query)
        logger.info("User query validated")

        if not validation_result["is_safe"]:
            logger.error("User query is not safe")
            raise HTTPException(status_code=400, detail=validation_result["message"])
        logger.info("User query is safe")

        # Run the manager agent
        result = await manager_agent.run(query.query, deps=agent_deps)

        # Validate the recommendations
        has_all_recommendations = get_all_recommendations(result.output)
        if not has_all_recommendations:
            logger.error("Recommendations are not valid")
            raise HTTPException(status_code=400, detail="Recommendations are not valid")
        logger.info("Recommendations are valid")

        print(
            f"Manager Agent Result: {json.dumps(result.output.model_dump(), indent=2)}"
        )

        # Return the result
        logger.info("Returning result")
        return result.output
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=f"API error: {str(e)}") from e


@app.get("/")
def read_root():
    """API is running"""
    return {"message": "Travel Assistant API is running"}


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
