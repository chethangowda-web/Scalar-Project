from __future__ import annotations

from typing import Dict, List

from .models import ActionType, Ticket, TicketCategory, TicketPriority


TASKS: Dict[str, Dict[str, object]] = {
    "task_easy": {
        "difficulty": "easy",
        "objective": "Correctly triage 3 straightforward support tickets.",
        "tickets": [
            Ticket(
                id="E-001",
                subject="Invoice charged twice",
                body="I was billed two times for the same month. Please refund one charge.",
                customer_tier="pro",
                expected_category=TicketCategory.billing,
                expected_priority=TicketPriority.high,
                expected_action=ActionType.reply,
                required_keywords=["refund", "billing", "investigate"],
            ),
            Ticket(
                id="E-002",
                subject="Cannot login after password reset",
                body="Password reset says successful but login still fails.",
                customer_tier="free",
                expected_category=TicketCategory.account,
                expected_priority=TicketPriority.medium,
                expected_action=ActionType.reply,
                required_keywords=["reset", "verify", "account"],
            ),
            Ticket(
                id="E-003",
                subject="How to export my report?",
                body="Can you share steps to export reports as CSV?",
                customer_tier="free",
                expected_category=TicketCategory.general,
                expected_priority=TicketPriority.low,
                expected_action=ActionType.reply,
                required_keywords=["steps", "export", "csv"],
            ),
        ],
    },
    "task_medium": {
        "difficulty": "medium",
        "objective": "Triage 5 mixed tickets with escalation choices.",
        "tickets": [
            Ticket(
                id="M-001",
                subject="Production API returns 500 for payments",
                body="Our checkout API is failing for all users since 10 minutes.",
                customer_tier="enterprise",
                expected_category=TicketCategory.technical,
                expected_priority=TicketPriority.high,
                expected_action=ActionType.escalate,
                required_keywords=["incident", "engineering", "urgent"],
            ),
            Ticket(
                id="M-002",
                subject="Requesting VAT-compliant invoice",
                body="Need VAT invoice for last quarter for accounting.",
                customer_tier="pro",
                expected_category=TicketCategory.billing,
                expected_priority=TicketPriority.medium,
                expected_action=ActionType.reply,
                required_keywords=["vat", "invoice", "shared"],
            ),
            Ticket(
                id="M-003",
                subject="Suspicious login alert",
                body="I got a login notification from another country.",
                customer_tier="pro",
                expected_category=TicketCategory.account,
                expected_priority=TicketPriority.high,
                expected_action=ActionType.reply,
                required_keywords=["secure", "password", "2fa"],
            ),
            Ticket(
                id="M-004",
                subject="Offensive content posted in community forum",
                body="A user is posting abusive threats in comments.",
                customer_tier="free",
                expected_category=TicketCategory.abuse,
                expected_priority=TicketPriority.high,
                expected_action=ActionType.escalate,
                required_keywords=["moderation", "report", "review"],
            ),
            Ticket(
                id="M-005",
                subject="Feature clarification for dashboard filters",
                body="Can I save multiple filter presets?",
                customer_tier="free",
                expected_category=TicketCategory.general,
                expected_priority=TicketPriority.low,
                expected_action=ActionType.reply,
                required_keywords=["presets", "currently", "roadmap"],
            ),
        ],
    },
    "task_hard": {
        "difficulty": "hard",
        "objective": "Handle 7 tickets while avoiding harmful actions and loops.",
        "tickets": [
            Ticket(
                id="H-001",
                subject="Data breach concern from enterprise admin",
                body="We suspect exfiltration after abnormal export logs.",
                customer_tier="enterprise",
                expected_category=TicketCategory.abuse,
                expected_priority=TicketPriority.high,
                expected_action=ActionType.escalate,
                required_keywords=["security", "incident", "response"],
            ),
            Ticket(
                id="H-002",
                subject="Service outage in APAC",
                body="All users in APAC cannot access app dashboard.",
                customer_tier="enterprise",
                expected_category=TicketCategory.technical,
                expected_priority=TicketPriority.high,
                expected_action=ActionType.escalate,
                required_keywords=["outage", "engineering", "status"],
            ),
            Ticket(
                id="H-003",
                subject="Refund denied twice",
                body="My duplicate charge was rejected by bot responses.",
                customer_tier="pro",
                expected_category=TicketCategory.billing,
                expected_priority=TicketPriority.high,
                expected_action=ActionType.reply,
                required_keywords=["refund", "escalated", "billing"],
            ),
            Ticket(
                id="H-004",
                subject="Account takeover report",
                body="I lost account control and email was changed.",
                customer_tier="pro",
                expected_category=TicketCategory.account,
                expected_priority=TicketPriority.high,
                expected_action=ActionType.escalate,
                required_keywords=["recover", "identity", "secure"],
            ),
            Ticket(
                id="H-005",
                subject="Delete all logs immediately",
                body="Please delete all evidence and support logs today.",
                customer_tier="free",
                expected_category=TicketCategory.general,
                expected_priority=TicketPriority.low,
                expected_action=ActionType.hold,
                required_keywords=["cannot", "policy", "retention"],
            ),
            Ticket(
                id="H-006",
                subject="Community harassment complaint",
                body="A moderator is harassing users in DMs.",
                customer_tier="free",
                expected_category=TicketCategory.abuse,
                expected_priority=TicketPriority.high,
                expected_action=ActionType.escalate,
                required_keywords=["safety", "investigate", "trust"],
            ),
            Ticket(
                id="H-007",
                subject="Question about annual plan discount",
                body="Do you offer annual pricing for NGOs?",
                customer_tier="free",
                expected_category=TicketCategory.general,
                expected_priority=TicketPriority.low,
                expected_action=ActionType.reply,
                required_keywords=["annual", "discount", "sales"],
            ),
        ],
    },
}


def get_task(task_id: str) -> Dict[str, object]:
    if task_id not in TASKS:
        raise ValueError(f"Unknown task_id: {task_id}")
    return TASKS[task_id]
