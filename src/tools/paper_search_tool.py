"""PaperSearchTool: searches arXiv for papers relevant to a text query.

Uses arXiv's free public API (no key required). Stdlib only — no new
third-party dependency.
"""

import re
import ssl
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

import certifi

from .paper_result import PaperResult
from .tool import Tool

_ARXIV_API_URL = "https://export.arxiv.org/api/query"
_ATOM_NS = "{http://www.w3.org/2005/Atom}"
_DEFAULT_MAX_RESULTS = 5
_DEFAULT_TIMEOUT = 10.0
# Some Python installs (notably python.org builds on macOS) ship without a
# wired-up system CA bundle. certifi's is always present as an openai/httpx
# transitive dependency, so use it explicitly rather than relying on a
# one-time "Install Certificates.command" step on the host machine.
_SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())


class PaperSearchError(RuntimeError):
    """Raised when the paper search API cannot be reached or parsed."""


class PaperSearchTool(Tool):
    """Searches arXiv and returns structured paper results."""

    name = "paper_search"
    description = "Searches arXiv for papers relevant to a free-text query."

    def __init__(self, max_results: int = _DEFAULT_MAX_RESULTS, timeout: float = _DEFAULT_TIMEOUT):
        self._max_results = max_results
        self._timeout = timeout

    def run(self, query: str) -> list[PaperResult]:
        """Search arXiv for `query` and return matching papers.

        Raises PaperSearchError on network or parse failure. Returns an
        empty list (not an error) when the search succeeds but matches
        nothing.
        """
        # arXiv's default "all:" search ORs bare whitespace-separated terms,
        # which returns mostly irrelevant results for multi-word queries.
        # ANDing each term keeps matches on-topic.
        terms = query.split()
        search_query = " AND ".join(f"all:{term}" for term in terms) if terms else query

        params = urllib.parse.urlencode(
            {"search_query": search_query, "max_results": self._max_results, "sortBy": "relevance"}
        )
        url = f"{_ARXIV_API_URL}?{params}"

        try:
            with urllib.request.urlopen(url, timeout=self._timeout, context=_SSL_CONTEXT) as response:
                raw = response.read()
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            raise PaperSearchError(f"arXiv search failed for query '{query}': {exc}") from exc

        try:
            root = ET.fromstring(raw)
        except ET.ParseError as exc:
            raise PaperSearchError(f"arXiv returned an unparseable response: {exc}") from exc

        return [self._parse_entry(entry) for entry in root.findall(f"{_ATOM_NS}entry")]

    def _parse_entry(self, entry: ET.Element) -> PaperResult:
        title = re.sub(r"\s+", " ", (entry.findtext(f"{_ATOM_NS}title") or "")).strip()
        summary = re.sub(r"\s+", " ", (entry.findtext(f"{_ATOM_NS}summary") or "")).strip()
        published = entry.findtext(f"{_ATOM_NS}published") or ""
        year = int(published[:4]) if published[:4].isdigit() else None
        authors = [
            (author.findtext(f"{_ATOM_NS}name") or "").strip()
            for author in entry.findall(f"{_ATOM_NS}author")
        ]

        url = ""
        for link in entry.findall(f"{_ATOM_NS}link"):
            if link.get("rel") == "alternate":
                url = link.get("href", "")
                break
        if not url:
            url = (entry.findtext(f"{_ATOM_NS}id") or "").strip()

        return PaperResult(
            title=title,
            authors=[a for a in authors if a],
            year=year,
            summary=summary,
            url=url,
            source="arxiv",
        )
