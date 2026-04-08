# Support Ops OpenEnv

`support_ops_openenv` is a real-world simulation of customer support triage, where an agent classifies incoming tickets, chooses priority, and decides operational actions (reply/escalate/resolve/hold).

## Why this environment

Customer support triage is a high-impact operational workflow used in SaaS, enterprise helpdesks, and moderation teams. This environment focuses on safe, deterministic ticket handling under mixed urgency.

## OpenEnv compliance

The environment provides:

- Typed `Action`, `Observation`, `Reward`, and `State` models using Pydantic
- `step(action) -> (observation, reward, done, info)`
- `reset(task_id)` and `state()`
- `openenv.yaml` metadata manifest
- Deterministic graders with 0.0-1.0 per-step scores

## 2-minute judge quick test

Start the API:

```bash
python -m uvicorn server.app:app --host 0.0.0.0 --port 8000
```

Run these checks in order:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/tasks
curl -X POST http://127.0.0.1:8000/reset -H "Content-Type: application/json" -d "{\"task_id\":\"task_easy\"}"
curl http://127.0.0.1:8000/state
curl -X POST http://127.0.0.1:8000/step -H "Content-Type: application/json" -d "{\"ticket_id\":\"E-001\",\"category\":\"billing\",\"priority\":\"high\",\"action_type\":\"reply\",\"response_text\":\"We issued a refund invoice and completed billing review.\"}"
```

Expected:

- `/health` returns `{"status":"ok"}`
- `/tasks` returns a task list including `task_easy`, `task_medium`, `task_hard`
- `/reset` returns initial observation and state
- `/step` returns observation, reward, done, and info with deterministic score components

## Action space

`SupportAction` fields:

- `ticket_id` (str)
- `category` (`billing|technical|account|abuse|general`)
- `priority` (`low|medium|high`)
- `action_type` (`reply|escalate|resolve|hold|delete`)
- `response_text` (str)

## Observation space

`SupportObservation` fields:

- `success` (bool)
- `message` (str)
- `remaining_tickets` (int)
- `current_ticket_id` (optional str)
- `progress` (0.0 to 1.0)
- `feedback` (score breakdown dictionary)

## Tasks and difficulty

- `task_easy` (3 tickets): obvious billing/account/general routing
- `task_medium` (5 tickets): escalation decisions + richer response quality checks
- `task_hard` (7 tickets): security/abuse/high-risk edge cases with stricter grading

## Grading and reward design

Per-step grader (deterministic):

- category match
- priority match (partial credit for adjacent priority)
- action match
- response keyword overlap

The weighted formula varies by task difficulty and always returns `total_score` in `[0.0, 1.0]`.

Reward function provides trajectory feedback:

- Positive reward for incremental correct progress
- Penalty for invalid ticket IDs
- Penalty for repeated-ticket loops
- Strong penalty for destructive `delete` actions

## Local setup

```bash
cd support_ops_openenv
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn server.app:app --host 0.0.0.0 --port 8000
```

Check endpoints:

- `GET /health`
- `GET /tasks`
- `POST /reset` with `{"task_id":"task_easy"}`
- `GET /state`
- `POST /step` with `SupportAction`

## Example `/step` request and response

Request body:

```json
{
  "ticket_id": "E-001",
  "category": "billing",
  "priority": "high",
  "action_type": "reply",
  "response_text": "We issued a refund invoice and completed billing review."
}
```

Response shape:

```json
{
  "observation": {
    "success": true,
    "message": "Processed E-001.",
    "remaining_tickets": 2,
    "current_ticket_id": "E-001",
    "progress": 0.3333,
    "feedback": {
      "category_score": 1.0,
      "priority_score": 1.0,
      "action_score": 1.0,
      "response_score": 1.0,
      "total_score": 1.0
    }
  },
  "reward": {
    "value": 1.0,
    "reason": "incremental_progress"
  },
  "done": false,
  "info": {
    "category_score": 1.0,
    "priority_score": 1.0,
    "action_score": 1.0,
    "response_score": 1.0,
    "total_score": 1.0
  }
}
```

## Baseline inference script

```bash
set HF_TOKEN=your_hf_token
set API_BASE_URL=https://router.huggingface.co/v1
set MODEL_NAME=meta-llama/Llama-3.1-8B-Instruct
set ENV_BASE_URL=http://127.0.0.1:8000
python inference.py
```

`inference.py` uses the OpenAI Python client with `HF_TOKEN` from environment variables.

## Example baseline scores

These are typical deterministic-fallback baseline ranges:

- easy: `~0.35`
- medium: `~0.28`
- hard: `~0.22`

Scores vary by selected model and token availability.

## Docker

```bash
cd support_ops_openenv
docker build -t support-ops-openenv .
docker run -p 7860:7860 support-ops-openenv
```

## Hugging Face Spaces

Use a **Docker** Space and include tag `openenv` in repository metadata/topics.

Suggested app port: `7860` (already configured in `Dockerfile`).
