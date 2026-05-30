from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class SearchHit:
    id: str
    title: str
    content: str
    source: str
    provider: str
    court: str | None = None
    date: datetime | None = None
    url: str | None = None
    relevance_score: float = 0.5
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "source": self.source,
            "court": self.court,
            "date": self.date.isoformat() if self.date else None,
            "area": None,
            "relevance_score": self.relevance_score,
            "url": self.url,
            "metadata": {**self.metadata, "provider": self.provider},
        }
