"""
One-time setup: creates (or updates) the ElevenLabs Conversational AI agent
that plays the role of "the patient" across every scenario.

Run this once before making any calls:
    python -m src.setup_agent

The prompt below is deliberately generic and leans on dynamic variables
({{persona_name}}, {{persona_goal}}, {{persona_style}}) so a single agent
can be reused for every scenario in scenarios.py instead of creating a new
agent per test case. This keeps the ElevenLabs side of the project small and
keeps all the actual test-case logic in Python, where it's easy to read,
diff, and extend.

Note: ElevenLabs' agent-creation schema evolves fairly often. If this script
errors on a field name, check the current shape at
https://elevenlabs.io/docs/api-reference/agents/create and adjust the
`payload` dict below. This does not affect the outbound-call or transcript
retrieval logic in elevenlabs_client.py, which are the parts we depend on
most heavily.
"""

import json

import requests

from src.config import load_settings

BASE_URL = "https://api.elevenlabs.io/v1"

AGENT_PROMPT = """You are role-playing as a patient calling a medical office's
AI phone assistant. You are NOT the assistant, you are the caller. Stay fully
in character for the entire call.

Your name: {{persona_name}}
Your goal for this call: {{persona_goal}}
Your speaking style: {{persona_style}}

Rules:
- Speak naturally, the way a real person talks on the phone, with normal
  pacing and the occasional filler word. Do not sound scripted.
- Pursue your goal actively. If the assistant goes off track, steer the
  conversation back toward what you called about.
- Answer any questions the assistant asks you as your persona would,
  improvising reasonable personal details (birthdate, phone number, etc.)
  if asked, since this is a test call.
- Let the call reach a natural conclusion (confirmation, a clear answer, or a
  clear next step) before ending. Do not hang up after only one exchange.
- Do not break character to mention that you are an AI, testing, or a bot.
"""


def build_agent_payload() -> dict:
    return {
        "name": "PGAI Challenge - Patient Caller",
        "conversation_config": {
            "agent": {
                "prompt": {
                    "prompt": AGENT_PROMPT,
                },
                "first_message": "Hi, I'm calling about an appointment.",
                "language": "en",
            },
        },
    }


def main() -> None:
    settings = load_settings()
    payload = build_agent_payload()

    resp = requests.post(
        f"{BASE_URL}/convai/agents/create",
        headers={"xi-api-key": settings.elevenlabs_api_key},
        json=payload,
    )

    if resp.status_code >= 400:
        print("Agent creation failed. Response body:")
        print(resp.text)
        resp.raise_for_status()

    data = resp.json()
    print("Agent created successfully.")
    print(json.dumps(data, indent=2))
    print("\nCopy the agent_id above into ELEVENLABS_AGENT_ID in your .env file.")


if __name__ == "__main__":
    main()
