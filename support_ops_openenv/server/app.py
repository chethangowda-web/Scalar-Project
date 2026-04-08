from __future__ import annotations

from fastapi import FastAPI, Request

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
async def reset(request: Request) -> dict:
    task_id = "task_easy"

    # Accept task_id from JSON body, form body, query param, or empty body.
    try:
        payload = await request.json()
        if isinstance(payload, dict):
            task_id = str(payload.get("task_id", task_id))
    except Exception:
        try:
            form_data = await request.form()
            if "task_id" in form_data:
                task_id = str(form_data.get("task_id"))
        except Exception:
            pass

    query_task_id = request.query_params.get("task_id")
    if query_task_id:
        task_id = query_task_id

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
