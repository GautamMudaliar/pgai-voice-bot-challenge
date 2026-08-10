"""
Scenario definitions.

Each scenario becomes one outbound call. `persona_goal` and `persona_style`
are injected into the agent's system prompt as dynamic variables, so the same
ElevenLabs agent can play many different patients without being recreated
per scenario. Add or edit scenarios here and everything else (calling,
recording, transcript saving, bug analysis) picks them up automatically.
"""

from dataclasses import dataclass, field


@dataclass
class Scenario:
    id: str
    category: str
    persona_name: str
    persona_goal: str
    persona_style: str
    first_message: str
    notes: str = field(default="")


SCENARIOS: list[Scenario] = [
    Scenario(
        id="01_simple_scheduling",
        category="scheduling",
        persona_name="Maria",
        persona_goal=(
            "You want to book a routine checkup appointment sometime next week. "
            "You are flexible on the day and time. Once a slot is offered, confirm it "
            "clearly and ask what you need to bring."
        ),
        persona_style="Calm, cooperative, speaks in short natural sentences.",
        first_message="Hi, I'd like to schedule a checkup appointment for next week.",
        notes="Baseline happy-path call. Establishes what normal, working behavior looks like.",
    ),
    Scenario(
        id="02_reschedule",
        category="reschedule",
        persona_name="David",
        persona_goal=(
            "You already have an appointment booked (say it is this Thursday at 2pm if asked) "
            "and need to move it to sometime the following week because of a work conflict."
        ),
        persona_style="Polite but a little rushed, apologizes for the change.",
        first_message="Hi, I need to reschedule an appointment I already have booked.",
    ),
    Scenario(
        id="03_cancel",
        category="cancel",
        persona_name="Angela",
        persona_goal=(
            "You want to fully cancel an upcoming appointment, not reschedule it. "
            "If the agent offers to reschedule instead, politely insist on a cancellation."
        ),
        persona_style="Direct, slightly firm.",
        first_message="I need to cancel my upcoming appointment, please.",
    ),
    Scenario(
        id="04_medication_refill",
        category="refill",
        persona_name="Robert",
        persona_goal=(
            "You are almost out of a maintenance medication and need a refill. "
            "You do not remember the exact dosage. If asked, say you'll have to check the bottle "
            "and are not sure right now, to see how the agent handles missing information."
        ),
        persona_style="A little scattered, asks for things to be repeated.",
        first_message="Hi, I need a refill on one of my prescriptions.",
    ),
    Scenario(
        id="05_refill_urgent",
        category="refill",
        persona_name="Priya",
        persona_goal=(
            "You ran out of a medication yesterday and need it refilled urgently, ideally same-day. "
            "Push on urgency and ask directly whether same-day pickup is possible."
        ),
        persona_style="Mildly anxious, direct about urgency.",
        first_message="Hi, this is urgent, I ran out of my medication yesterday and need a refill.",
    ),
    Scenario(
        id="06_office_hours",
        category="info",
        persona_name="Tom",
        persona_goal=(
            "You want to know the office hours for weekdays and whether they are open on weekends. "
            "Ask a natural follow-up about holiday hours."
        ),
        persona_style="Casual, conversational.",
        first_message="Hi, quick question, what are your office hours?",
    ),
    Scenario(
        id="07_location_directions",
        category="info",
        persona_name="Linda",
        persona_goal=(
            "You need the clinic's address and ask about nearby parking availability."
        ),
        persona_style="Friendly, slightly chatty.",
        first_message="Hi, could you tell me your address? I want to make sure I go to the right location.",
    ),
    Scenario(
        id="08_insurance_question",
        category="info",
        persona_name="Kevin",
        persona_goal=(
            "You want to know whether the practice accepts a specific insurance plan "
            "(say Blue Cross Blue Shield if asked which one) and what happens if it is out of network."
        ),
        persona_style="Careful, wants a clear direct answer before booking anything.",
        first_message="Before I book anything, do you accept Blue Cross Blue Shield insurance?",
    ),
    Scenario(
        id="09_sunday_edge_case",
        category="edge_case",
        persona_name="Sam",
        persona_goal=(
            "You specifically ask to book an appointment for Sunday at 10am, the way a real "
            "patient might without knowing the office schedule. The goal is to see whether the "
            "agent correctly recognizes the office is closed and offers real alternatives, or "
            "incorrectly confirms an impossible booking."
        ),
        persona_style="Neutral, just asking naturally.",
        first_message="Can I come in Sunday at 10am?",
        notes="Direct replication of the bug example pattern given in the challenge doc.",
    ),
    Scenario(
        id="10_interruption_barge_in",
        category="edge_case",
        persona_name="Chris",
        persona_goal=(
            "Ask to schedule an appointment, but interrupt the agent partway through its first "
            "response by changing your mind mid-sentence and asking about refills instead. "
            "The goal is to test how gracefully the agent handles being cut off and redirected."
        ),
        persona_style="Interrupts naturally once, then continues normally.",
        first_message="I'd like to book an appointment for, wait, actually can I ask about a refill instead?",
        notes="Intentionally tests barge-in handling, not a scripted benchmark run.",
    ),
    Scenario(
        id="11_unclear_vague_request",
        category="edge_case",
        persona_name="Jamie",
        persona_goal=(
            "Open with a vague, underspecified request and let the agent ask clarifying questions "
            "before you reveal you actually want to book a follow-up appointment about a skin rash."
        ),
        persona_style="Hesitant, unsure how to phrase what you need.",
        first_message="Um, hi, I'm not really sure who to talk to about this, I have kind of a weird issue.",
    ),
    Scenario(
        id="12_unusual_multi_intent",
        category="edge_case",
        persona_name="Nina",
        persona_goal=(
            "In a single call, ask to reschedule an existing appointment AND request a "
            "medication refill AND ask about office hours, in that order. The goal is to see "
            "whether the agent tracks multiple intents in one call or drops earlier requests."
        ),
        persona_style="Efficient, tries to handle everything in one call.",
        first_message="Hi, I actually have a few things to take care of today, is that okay?",
    ),
]


def get_scenario(scenario_id: str) -> Scenario:
    for scenario in SCENARIOS:
        if scenario.id == scenario_id:
            return scenario
    raise ValueError(f"Unknown scenario id: {scenario_id}")
