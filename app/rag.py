"""Retrieval over the fake company docs.

Baseline uses simple keyword overlap so the lab has no extra services.
TODO (next phase): swap in embeddings + a vector store (e.g. Chroma).
"""

import re
from dataclasses import dataclass
from pathlib import Path

from app.config import settings


@dataclass
class Chunk:
    source: str
    text: str


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def load_chunks(docs_dir: str | None = None) -> list[Chunk]:
    root = Path(docs_dir or settings.docs_dir)
    chunks = []
    for path in sorted(root.rglob("*.md")):
        source = path.relative_to(root).as_posix()
        if not settings.rag_include_internal and source.startswith("internal/"):
            continue  # access control: the bot can't leak a doc it never loads
        for para in path.read_text(encoding="utf-8").split("\n\n"):
            if para.strip():
                chunks.append(Chunk(source=source, text=para.strip()))
    return chunks


def retrieve(query: str, chunks: list[Chunk], k: int | None = None) -> list[Chunk]:
    q = _tokens(query)
    scored = [(len(q & _tokens(c.text)), c) for c in chunks]
    scored = [s for s in scored if s[0] > 0]
    scored.sort(key=lambda s: s[0], reverse=True)
    return [c for _, c in scored[: k or settings.top_k]]
