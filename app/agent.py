from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


@dataclass
class KnowledgeEntry:
    entry_id: str
    source: str
    title: str
    text: str

    def tokens(self) -> set[str]:
        return set(re.findall(r"[\w\u4e00-\u9fff]+", self.text + " " + self.title))


class KnowledgeBase:
    def __init__(self, entries: Iterable[KnowledgeEntry]) -> None:
        self.entries = list(entries)

    @classmethod
    def from_json(cls, path: Path) -> "KnowledgeBase":
        payload = json.loads(path.read_text(encoding="utf-8"))
        entries = [
            KnowledgeEntry(
                entry_id=item["id"],
                source=item["source"],
                title=item["title"],
                text=item["text"],
            )
            for item in payload.get("corpus", [])
        ]
        return cls(entries)

    def search(self, query: str, limit: int = 3) -> List[KnowledgeEntry]:
        query_tokens = set(re.findall(r"[\w\u4e00-\u9fff]+", query))
        if not query_tokens:
            return []
        scored = []
        for entry in self.entries:
            overlap = query_tokens & entry.tokens()
            score = len(overlap)
            if score:
                scored.append((score, entry))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [entry for _, entry in scored[:limit]]


class LiBaiAgent:
    def __init__(self, knowledge_base: KnowledgeBase) -> None:
        self.knowledge_base = knowledge_base

    def answer(self, question: str) -> str:
        hits = self.knowledge_base.search(question)
        if not hits:
            return (
                "未检索到直接相关的记录。我可以从《全唐诗》、"
                "李白年谱或唐代地理志里继续查找，请换个问法。"
            )
        lines = ["根据资料，整理如下："]
        for entry in hits:
            lines.append(f"- 【{entry.source}·{entry.title}】{entry.text}")
        return "\n".join(lines)
