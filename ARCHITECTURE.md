# Architecture

The system has three parts, all orchestrated from Python: an ElevenLabs
Conversational AI agent that plays the "patient" caller, ElevenLabs' native
Twilio integration that places and carries the actual phone call, and a
lightweight analysis pass that turns saved transcripts into a bug report.

## Why ElevenLabs' native Twilio integration instead of a custom bridge

The obvious way to build this is to stand up our own server that opens a
Twilio Media Stream WebSocket, pipes audio to an STT model, runs it through
an LLM, generates speech, and streams it back, essentially rebuilding a
realtime voice pipeline from scratch. We considered this (and considered the
OpenAI Realtime API as the LLM layer for it), but rejected it for this
project. That approach adds a full extra hop of audio encoding, network
transport, and buffering logic that we would own and have to debug
ourselves, and the single highest-priority evaluation criterion here is
whether the call is a coherent, natural-sounding conversation. Every extra
hop is a place for latency spikes, clipped audio, or broken turn-taking to
creep in.

ElevenLabs exposes an outbound-call endpoint
(`POST /v1/convai/twilio/outbound_call`) that owns the entire Twilio call leg
internally: it dials the number, manages the media stream, and runs its own
STT -> LLM -> TTS loop, including its own interruption/turn-taking handling.
Our Python code's job shrinks to what actually matters for this challenge:
defining realistic patient personas, triggering calls against the correct
target number, and pulling structured results back out. We use dynamic
variables (`persona_name`, `persona_goal`, `persona_style`) to drive a single
ElevenLabs agent through twelve different scenarios rather than creating a
new agent per test case, which keeps the ElevenLabs-side configuration small
and keeps all the actual scenario logic, and all the diffable, reviewable
project logic, on the Python side of the system.

## Data flow

`call_runner.py` reads a scenario, calls the ElevenLabs API to place the
outbound call to `+1-805-439-8008`, and polls the conversation status until
it reaches a terminal state. Once done, it pulls the structured transcript
and the audio recording and writes both to `recordings/`. Separately,
`bug_analyzer.py` reads every saved transcript and asks Claude to flag
specific, concrete issues (impossible confirmations, dropped context,
mishandled interruptions, vague answers) against a fixed rubric modeled on
the challenge's own example bug report, then writes `bug_report.md`. This
pass is explicitly a draft aid, not a replacement for listening to the
calls, we call that out in the README so it's clear the human review step is
still expected before submission.

## Tradeoffs we accepted

Relying on ElevenLabs' hosted call handling means less visibility into the
raw audio pipeline if something goes wrong mid-call, and it ties telephony
quality to ElevenLabs' infrastructure rather than something we control end
to end. For a 6-hour project where the top evaluation criterion is
conversation coherence, we judged that tradeoff worth making. If we needed
finer control, for example custom barge-in thresholds beyond what the
platform exposes, the natural next step would be dropping to a raw Twilio
Media Stream bridge with OpenAI's Realtime API, which we scoped but did not
build.
