"""Generic Tool abstraction: an external capability an agent can invoke."""

from abc import ABC, abstractmethod
from typing import Any


class Tool(ABC):
    """A named, callable capability. Concrete tools implement ``run``."""

    name: str
    description: str

    @abstractmethod
    def run(self, **kwargs: Any) -> Any:
        ...
