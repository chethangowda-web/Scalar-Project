from __future__ import annotations

from enum import Enum
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class TicketCategory(str, Enum):
    billing = "billing"
    technical = "technical"
    account = "account"
    abuse = "abuse"
    general = "general"


class TicketPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class ActionType(str, Enum):
    reply = "reply"
    escalate = "escalate"
    resolve = "resolve"
    hold = "hold"
    delete = "delete"


class Ticket(BaseModel):
    id: str
    subject: str
    body: str
    customer_tier: Literal["free", "pro", "enterprise"]
    expected_category: TicketCategory
    expected_priority: TicketPriority
    expected_action: ActionType
    required_keywords: List[str] = Field(default_factory=list)


class SupportAction(BaseModel):
    ticket_id: str
    category: TicketCategory
    priority: TicketPriority
    action_type: ActionType
    response_text: str = ""


class SupportObservation(BaseModel):
    success: bool
    message: str
    remaining_tickets: int
    current_ticket_id: Optional[str] = None
    progress: float = 0.0
    feedback: Dict[str, float] = Field(default_factory=dict)


class RewardModel(BaseModel):
    value: float = Field(ge=-1.0, le=1.0)
    reason: str


class EnvironmentState(BaseModel):
    task_id: str
    step_count: int
    max_steps: int
    done: bool
    handled_ticket_ids: List[str]
    queue_snapshot: List[Dict[str, str]]
