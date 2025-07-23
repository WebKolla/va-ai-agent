"""
Manager Agent for coordinating multiple specialised agents.
"""

import os

from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext
from pydantic_ai.settings import ModelSettings

from app.prompts import MANAGER_AGENT_PROMPT
from app.schemas import (
    ExperienceRecommendation,
    FlightRecommendation,
    HotelRecommendation,
    TravelAdvice,
)

load_dotenv()

manager_agent = Agent(
    os.getenv("GPT_MODEL"),
    deps_type=dict,
    output_type=TravelAdvice,
    model_settings=ModelSettings(temperature=0.5, max_tokens=500),
    instructions=(MANAGER_AGENT_PROMPT),
)


@manager_agent.tool
async def get_hotel_recommendations(
    ctx: RunContext[dict], query: str
) -> HotelRecommendation:
    """Get hotel recommendations from the hotel specialist."""
    hotel_agent = ctx.deps["hotel_agent"]
    result = await hotel_agent.run(query, deps=query)
    return result.output


@manager_agent.tool
async def get_flight_recommendations(
    ctx: RunContext[dict], query: str
) -> FlightRecommendation:
    """Get flight recommendations from the flight specialist."""
    flights_agent = ctx.deps["flights_agent"]
    result = await flights_agent.run(query, deps=query)
    return result.output


@manager_agent.tool
async def get_experience_recommendations(
    ctx: RunContext[dict], query: str
) -> ExperienceRecommendation:
    """Get experience recommendations from the experience specialist."""
    experience_agent = ctx.deps["experience_agent"]
    result = await experience_agent.run(query, deps=query)
    return result.output
