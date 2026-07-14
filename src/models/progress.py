"""Progress model: a snapshot of how far along a Project is."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Progress:
    id: str
    project_id: str
    completed_tasks: int = 0
    total_tasks: int = 0
    completion_rate: float = 0.0
    current_stage: str = ""
    last_update: datetime = field(default_factory=datetime.now)
