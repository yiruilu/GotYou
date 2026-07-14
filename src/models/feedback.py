"""Feedback model: a piece of input (from a reviewer, user, or agent) about a Project."""

from dataclasses import dataclass

from .enums import FeedbackStatus, Priority


@dataclass
class Feedback:
    id: str
    source: str
    content: str
    category: str = ""
    priority: Priority = Priority.MEDIUM
    status: FeedbackStatus = FeedbackStatus.OPEN
