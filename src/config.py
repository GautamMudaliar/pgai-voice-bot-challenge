"""
Places one outbound test call for a given scenario, waits for it to finish,
and saves both the transcript and the audio recording to recordings/.

Usage:
    python -m src.call_runner --scenario 01_simple_scheduling
    python -m src.call_runner --all
"""

import argparse
import json
import sys
import time
from pathlib import Path

from src.config import TEST_TARGET_NUMBER, load_settings
from src.elevenlabs_client import ElevenLabsClient
from src.scenarios import SCENARIOS, Scenario, get_scenario

RECORDINGS_DIR = Path(__file__).resolve().parent.parent / "recordings"


def run_scenario(client: ElevenLabsClient, scenario: Scenario) -> dict:
    print(f"\n=== Placing call for scenario: {scenario.id} ({scenario.category}) ===")

    dynamic_variables = {
        "persona_name": scenario.persona_name,
        "persona_goal": scenario.persona_goal,
        "persona_style": scenario.persona_style,
    }

    call_result = client.place_outbound_call(
        to_number=TEST_TARGET_NUMBER,
        dynamic_variables=dynamic_variables,
        first_message=scenario.first_message,
    )
    conversation_id = call_result.get("conversation_id")
    if not conversation_id:
        raise RuntimeError(f"No conversation_id returned for {scenario.id}: {call_result}")

    print(f"Call placed. conversation_id={conversation_id}. Waiting for completion...")
    conversation = client.wait_for_completion(conversation_id)

    save_transcript(scenario, conversation)
    save_audio(client, scenario, conversation_id)

    print(f"=== Finished scenario: {scenario.id} (status={conversation.get('status')}) ===")
    return conversation


def save_transcript(scenario: Scenario, conversation: dict) -> None:
    RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RECORDINGS_DIR / f"{scenario.id}.transcript.json"
    out_path.write_text(json.dumps(conversation, indent=2))

    # also write a human-readable .txt version for quick review / bug report references
    txt_path = RECORDINGS_DIR / f"{scenario.id}.transcript.txt"
    lines = [f"Scenario: {scenario.id} ({scenario.category})", f"Persona goal: {scenario.persona_goal}", ""]
    for turn in conversation.get("transcript", []):
        speaker = turn.get("role", "unknown")
        text = turn.get("message", "")
        lines.append(f"{speaker}: {text}")
    txt_path.write_text("\n".join(lines))
    print(f"Saved transcript to {out_path.name} and {txt_path.name}")


def save_audio(client: ElevenLabsClient, scenario: Scenario, conversation_id: str) -> None:
    RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)
    audio_bytes = client.get_conversation_audio(conversation_id)
    out_path = RECORDINGS_DIR / f"{scenario.id}.mp3"
    out_path.write_bytes(audio_bytes)
    print(f"Saved audio to {out_path.name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Place outbound test calls against the PGAI test line.")
    parser.add_argument("--scenario", help="Run a single scenario by id")
    parser.add_argument("--all", action="store_true", help="Run every scenario in scenarios.py")
    parser.add_argument(
        "--delay",
        type=int,
        default=10,
        help="Seconds to wait between calls when running --all, to avoid overlapping calls",
    )
    args = parser.parse_args()

    if not args.scenario and not args.all:
        parser.error("Pass --scenario <id> or --all")

    settings = load_settings()
    client = ElevenLabsClient(settings)

    if args.scenario:
        run_scenario(client, get_scenario(args.scenario))
        return

    for i, scenario in enumerate(SCENARIOS):
        try:
            run_scenario(client, scenario)
        except Exception as exc:
            print(f"[ERROR] Scenario {scenario.id} failed: {exc}")
            print("Continuing with remaining scenarios...")
        if i < len(SCENARIOS) - 1:
            time.sleep(args.delay)

    print(f"\nAll {len(SCENARIOS)} scenarios complete. See recordings/ for transcripts and audio.")


if __name__ == "__main__":
    sys.exit(main())