from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List
import json
import os


@dataclass
class FetchedItem:
    id: str
    title: str
    url: str
    published: str
    summary: str
    category_hint: str

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "published": self.published,
            "summary": self.summary,
            "category_hint": self.category_hint,
        }


@dataclass
class FetchResult:
    source: str
    fetched_at: str
    items: List[FetchedItem]

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "fetched_at": self.fetched_at,
            "items": [item.to_dict() for item in self.items],
        }


class BaseFetcher(ABC):
    def __init__(self, name: str, config: dict):
        self.name = name
        self.config = config

    @abstractmethod
    def fetch(self) -> FetchResult:
        pass

    def save(self, result: FetchResult, output_dir: str) -> str:
        os.makedirs(output_dir, exist_ok=True)
        date_stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
        filename = f"{self.name}_{date_stamp}.json"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w") as f:
            json.dump(result.to_dict(), f, indent=2)
        return filepath
