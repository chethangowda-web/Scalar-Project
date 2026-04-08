from __future__ import annotations

from fastapi import FastAPI

from support_ops_openenv.environment import SupportOpsEnvironment
from support_ops_openenv.models import SupportAction

app = FastAPI(title="Support Ops OpenEnv")
env = SupportOpsEnvironment()


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/tasks")
async def tasks() -> dict:
    return {"tasks": env.available_tasks()}


@app.post("/reset")
async def reset(payload: dict | None = None) -> dict:
    payload = payload or {}
    task_id = payload.get("task_id", "task_easy")
    observation = env.reset(task_id=task_id)
    return {"observation": observation.model_dump(), "state": env.state().model_dump()}


@app.get("/state")
async def state() -> dict:
    return env.state().model_dump()


@app.post("/step")
async def step(action: SupportAction) -> dict:
    observation, reward, done, info = env.step(action)
    return {
        "observation": observation.model_dump(),
        "reward": reward.model_dump(),
        "done": done,
        "info": info,
    }
