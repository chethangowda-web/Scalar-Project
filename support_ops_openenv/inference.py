from __future__ import annotations

import json
import os
from typing import Dict

import requests
from openai import OpenAI


API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "meta-llama/Llama-3.1-8B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN")
ENV_BASE_URL = os.getenv("ENV_BASE_URL", "http://127.0.0.1:8000")


def ask_model(ticket: Dict[str, str]) -> Dict[str, str]:
    if not HF_TOKEN:
        # Deterministic fallback if token is not set.
        return {
            "ticket_id": ticket["id"],
            "category": "general",
            "priority": "medium",
            "action_type": "reply",
            "response_text": "Thanks. We are reviewing your request and will follow up.",
        }

    client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)
    prompt = (
        "You are a support triage agent. Return strict JSON with keys: "
        "ticket_id, category, priority, action_type, response_text.\n\n"
        f"Ticket:\nID: {ticket['id']}\nSubject: {ticket['subject']}\nBody: {ticket['body']}\n"
    )
    response = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "Be safe, concise, and policy-compliant."},
            {"role": "user", "content": prompt},
        ],
    )
    return json.loads(response.choices[0].message.content)


def run_task(task_id: str) -> float:
    requests.post(f"{ENV_BASE_URL}/reset", json={"task_id": task_id}, timeout=30)
    total_score = 0.0
    actions = 0

    while True:
        state = requests.get(f"{ENV_BASE_URL}/state", timeout=30).json()
        if state["done"]:
            break
        if not state["queue_snapshot"]:
            break
        ticket = state["queue_snapshot"][0]
        action = ask_model(ticket)
        action["ticket_id"] = ticket["id"]
        step_out = requests.post(f"{ENV_BASE_URL}/step", json=action, timeout=30).json()
        total_score += step_out["info"].get("total_score", 0.0)
        actions += 1
        if step_out["done"]:
            break
    return 0.0 if actions == 0 else round(total_score / actions, 4)


def main() -> None:
    scores = {}
    for task_id in ("task_easy", "task_medium", "task_hard"):
        scores[task_id] = run_task(task_id)
    print(json.dumps(scores, indent=2))


if __name__ == "__main__":
    main()
