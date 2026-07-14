"""Resource model: an external reference (paper, article, etc.) relevant to a Project."""

from dataclasses import dataclass

from .enums import ResourceStatus, ResourceType


@dataclass
class Resource:
    id: str
    title: str
    type: ResourceType = ResourceType.OTHER
    source: str = ""
    summary: str = ""
    relevance: str = ""
    status: ResourceStatus = ResourceStatus.NEW
