"""PaperResult: a single paper returned by a paper search tool."""

from dataclasses import dataclass, field


@dataclass
class PaperResult:
    title: str
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    summary: str = ""
    url: str = ""
    source: str = ""
