"""
Central configuration for the voice bot challenge.

All values are pulled from environment variables so no secrets ever land in
source control. See .env.example for the full list of required variables.
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


# The only number we are permitted to call for this assessment.
TEST_TARGET_NUMBER = "+18054398008"


@dataclass(frozen=True)
class Settings:
    elevenlabs_api_key: str
    elevenlabs_agent_id: str
    elevenlabs_agent_phone_number_id: str
    anthropic_api_key: str
    caller_number: str  # the single number we use for all outbound test calls
    poll_interval_seconds: int = 5
    poll_timeout_seconds: int = 300


def load_settings() -> Settings:
    missing = []

    def require(name: str) -> str:
        value = os.environ.get(name)
        if not value:
            missing.append(name)
        return value or ""

    settings = Settings(
        elevenlabs_api_key=require("ELEVENLABS_API_KEY"),
        elevenlabs_agent_id=require("ELEVENLABS_AGENT_ID"),
        elevenlabs_agent_phone_number_id=require("ELEVENLABS_AGENT_PHONE_NUMBER_ID"),
        anthropic_api_key=require("ANTHROPIC_API_KEY"),
        caller_number=require("CALLER_NUMBER"),
    )

    if missing:
        raise EnvironmentError(
            "Missing required environment variables: "
            + ", ".join(missing)
            + ". Copy .env.example to .env and fill these in."
        )

    return settings
