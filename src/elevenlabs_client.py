"""
Wrapper around the ElevenLabs Conversational AI REST API.

We rely on ElevenLabs' native Twilio integration rather than building our own
Twilio Media Streams <-> WebSocket bridge. ElevenLabs owns the Twilio call leg
end to end (POST /v1/convai/twilio/outbound_call), which removes an entire
class of latency and audio-glitch risk from our system. This was the single
biggest architectural decision in this project, see ARCHITECTURE.md.
"""

import time
from typing import Any, Optional

import requests

from src.config import Settings

BASE_URL = "https://api.elevenlabs.io/v1"


class ElevenLabsClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.session = requests.Session()
        self.session.headers.update({"xi-api-key": settings.elevenlabs_api_key})

    def place_outbound_call(
        self,
        to_number: str,
        dynamic_variables: dict[str, str],
        first_message: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Places an outbound call through ElevenLabs' Twilio integration.

        dynamic_variables lets us reuse a single agent across every scenario:
        the agent's system prompt references {{persona_goal}}, {{persona_name}},
        and {{persona_style}}, which we swap out per call.
        """
        payload: dict[str, Any] = {
            "agent_id": self.settings.elevenlabs_agent_id,
            "agent_phone_number_id": self.settings.elevenlabs_agent_phone_number_id,
            "to_number": to_number,
            "conversation_initiation_client_data": {
                "dynamic_variables": dynamic_variables,
            },
        }
        if first_message:
            payload["conversation_initiation_client_data"]["conversation_config_override"] = {
                "agent": {"first_message": first_message}
            }

        resp = self.session.post(f"{BASE_URL}/convai/twilio/outbound_call", json=payload)
        resp.raise_for_status()
        return resp.json()

    def get_conversation(self, conversation_id: str) -> dict[str, Any]:
        resp = self.session.get(f"{BASE_URL}/convai/conversations/{conversation_id}")
        resp.raise_for_status()
        return resp.json()

    def get_conversation_audio(self, conversation_id: str) -> bytes:
        resp = self.session.get(f"{BASE_URL}/convai/conversations/{conversation_id}/audio")
        resp.raise_for_status()
        return resp.content

    def wait_for_completion(self, conversation_id: str) -> dict[str, Any]:
        """
        Polls until the conversation reaches a terminal status (done/failed)
        or we hit the configured timeout.
        """
        elapsed = 0
        while elapsed < self.settings.poll_timeout_seconds:
            data = self.get_conversation(conversation_id)
            status = data.get("status")
            if status in ("done", "failed"):
                return data
            time.sleep(self.settings.poll_interval_seconds)
            elapsed += self.settings.poll_interval_seconds

        raise TimeoutError(
            f"Conversation {conversation_id} did not complete within "
            f"{self.settings.poll_timeout_seconds}s (last status unknown)."
        )
