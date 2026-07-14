"""Shared enumerations for fields with a fixed set of valid values."""

from enum import Enum


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    BLOCKED = "blocked"


class ResourceType(str, Enum):
    PAPER = "paper"
    BOOK = "book"
    ARTICLE = "article"
    VIDEO = "video"
    OTHER = "other"


class ResourceStatus(str, Enum):
    NEW = "new"
    REVIEWED = "reviewed"
    USED = "used"
    IGNORED = "ignored"


class FeedbackStatus(str, Enum):
    OPEN = "open"
    ADDRESSED = "addressed"
    DISMISSED = "dismissed"
