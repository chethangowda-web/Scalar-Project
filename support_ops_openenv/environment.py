from __future__ import annotations

from typing import Dict, List, Set, Tuple

from .data import TASKS, get_task
from .models import (
    ActionType,
    EnvironmentState,
    RewardModel,
    SupportAction,
    SupportObservation,
    Ticket,
)


class SupportOpsEnvironment:
    """OpenEnv-style environment for customer support triage."""

    def __init__(self, max_steps: int = 30) -> None:
        self.max_steps = max_steps
        self.task_id = "task_easy"
        self.step_count = 0
        self.done = False
        self.tickets: List[Ticket] = []
        self.ticket_index: Dict[str, Ticket] = {}
        self.handled_ticket_ids: Set[str] = set()
        self.reset(task_id=self.task_id)

    def reset(self, task_id: str = "task_easy") -> SupportObservation:
        task = get_task(task_id)
        self.task_id = task_id
        self.step_count = 0
        self.done = False
        self.tickets = list(task["tickets"])
        self.ticket_index = {ticket.id: ticket for ticket in self.tickets}
        self.handled_ticket_ids = set()
        return self._make_observation(True, f"Task {task_id} reset.", feedback={})

    def state(self) -> EnvironmentState:
        return EnvironmentState(
            task_id=self.task_id,
            step_count=self.step_count,
            max_steps=self.max_steps,
            done=self.done,
            handled_ticket_ids=sorted(self.handled_ticket_ids),
            queue_snapshot=[
                {"id": t.id, "subject": t.subject, "body": t.body, "tier": t.customer_tier}
                for t in self.tickets
                if t.id not in self.handled_ticket_ids
            ],
        )

    def step(
        self, action: SupportAction
    ) -> Tuple[SupportObservation, RewardModel, bool, Dict[str, float]]:
        if self.done:
            obs = self._make_observation(False, "Episode already done.", feedback={})
            reward = RewardModel(value=-0.2, reason="action_after_done")
            return obs, reward, self.done, {}

        self.step_count += 1
        feedback: Dict[str, float] = {}

        if action.ticket_id not in self.ticket_index:
            obs = self._make_observation(False, "Invalid ticket_id.", feedback={})
            reward = RewardModel(value=-0.5, reason="invalid_ticket")
            self._update_done()
            return obs, reward, self.done, {"penalty_invalid": 0.5}

        if action.ticket_id in self.handled_ticket_ids:
            obs = self._make_observation(False, "Ticket already handled.", feedback={})
            reward = RewardModel(value=-0.25, reason="loop_repeated_ticket")
            self._update_done()
            return obs, reward, self.done, {"penalty_repeat": 0.25}

        ticket = self.ticket_index[action.ticket_id]
        feedback = self._grade_action(ticket, action)
        raw_score = feedback["total_score"]

        # Penalize destructive behavior strongly.
        if action.action_type == ActionType.delete:
            raw_score -= 0.6
            feedback["penalty_destructive_delete"] = 0.6

        reward_value = max(-1.0, min(1.0, (raw_score * 2.0) - 1.0))
        reward = RewardModel(
            value=reward_value,
            reason="incremental_progress" if reward_value >= 0 else "needs_correction",
        )

        if raw_score >= 0.4:
            self.handled_ticket_ids.add(ticket.id)

        self._update_done()
        obs = self._make_observation(
            success=True,
            message=f"Processed {ticket.id}.",
            current_ticket_id=ticket.id,
            feedback=feedback,
        )
        return obs, reward, self.done, feedback

    def available_tasks(self) -> List[Dict[str, str]]:
        return [
            {
                "id": task_id,
                "difficulty": str(task["difficulty"]),
                "objective": str(task["objective"]),
                "ticket_count": str(len(task["tickets"])),
            }
            for task_id, task in TASKS.items()
        ]

    def _grade_action(self, ticket: Ticket, action: SupportAction) -> Dict[str, float]:
        category_score = 1.0 if action.category == ticket.expected_category else 0.0
        priority_score = self._priority_score(str(action.priority), str(ticket.expected_priority))
        action_score = 1.0 if action.action_type == ticket.expected_action else 0.0
        response_score = self._keyword_overlap(action.response_text, ticket.required_keywords)

        if self.task_id == "task_easy":
            total = (category_score * 0.5) + (priority_score * 0.3) + (action_score * 0.2)
        elif self.task_id == "task_medium":
            total = (
                (category_score * 0.35)
                + (priority_score * 0.25)
                + (action_score * 0.25)
                + (response_score * 0.15)
            )
        else:
            total = (
                (category_score * 0.25)
                + (priority_score * 0.2)
                + (action_score * 0.25)
                + (response_score * 0.3)
            )

        return {
            "category_score": round(category_score, 4),
            "priority_score": round(priority_score, 4),
            "action_score": round(action_score, 4),
            "response_score": round(response_score, 4),
            "total_score": round(total, 4),
        }

    @staticmethod
    def _priority_score(got: str, expected: str) -> float:
        order = {"low": 0, "medium": 1, "high": 2}
        if got == expected:
            return 1.0
        if abs(order.get(got, -10) - order.get(expected, 10)) == 1:
            return 0.5
        return 0.0

    @staticmethod
    def _keyword_overlap(response_text: str, keywords: List[str]) -> float:
        if not keywords:
            return 1.0
        text = response_text.lower()
        matched = sum(1 for keyword in keywords if keyword.lower() in text)
        return matched / len(keywords)

    def _update_done(self) -> None:
        remaining = len(self.tickets) - len(self.handled_ticket_ids)
        if remaining == 0 or self.step_count >= self.max_steps:
            self.done = True

    def _make_observation(
        self,
        success: bool,
        message: str,
        current_ticket_id: str | None = None,
        feedback: Dict[str, float] | None = None,
    ) -> SupportObservation:
        feedback = feedback or {}
        remaining = len(self.tickets) - len(self.handled_ticket_ids)
        progress = 0.0 if not self.tickets else (len(self.handled_ticket_ids) / len(self.tickets))
        return SupportObservation(
            success=success,
            message=message,
            remaining_tickets=remaining,
            current_ticket_id=current_ticket_id,
            progress=round(progress, 4),
            feedback=feedback,
        )
