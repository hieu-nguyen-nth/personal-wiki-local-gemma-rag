from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import math
from pathlib import Path
import re
import sqlite3
from typing import Iterable


SUPPORTED_SUFFIXES = {".md", ".markdown", ".txt"}
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
TOKEN_RE = re.compile(r"[\w'-]+", re.UNICODE)
STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "do", "does", "for",
    "from", "how", "i", "in", "is", "it", "of", "on", "or", "that", "the",
    "this", "to", "was", "what", "when", "where", "which", "who", "why", "with",
}


@dataclass(frozen=True)
class Passage:
    rank: int
    path: str
    heading: str
    text: str
    score: float
    source_hash: str


@dataclass(frozen=True)
class IngestStats:
    scanned: int
    indexed: int
    unchanged: int
    removed: int
    chunks: int


def connect(database: Path) -> sqlite3.Connection:
    database.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    connection.executescript(
        """
        PRAGMA journal_mode=WAL;
        CREATE TABLE IF NOT EXISTS sources (
            path TEXT PRIMARY KEY,
            source_root TEXT NOT NULL,
            content_hash TEXT NOT NULL,
            modified_ns INTEGER NOT NULL,
            indexed_at TEXT NOT NULL
        );
        CREATE VIRTUAL TABLE IF NOT EXISTS chunks USING fts5(
            source_path UNINDEXED,
            heading,
            body,
            content_hash UNINDEXED,
            tokenize='unicode61 remove_diacritics 2'
        );
        """
    )
    return connection


def _source_files(source: Path) -> list[Path]:
    if source.is_file():
        return [source] if source.suffix.lower() in SUPPORTED_SUFFIXES else []
    return sorted(
        path for path in source.rglob("*")
        if path.is_file()
        and path.suffix.lower() in SUPPORTED_SUFFIXES
        and ".obsidian" not in path.parts
    )


def _relative_path(path: Path, source: Path) -> str:
    base = source if source.is_dir() else source.parent
    return path.relative_to(base).as_posix()


def _normalize_markdown(text: str) -> str:
    text = re.sub(r"^---\s*$.*?^---\s*$", "", text, count=1, flags=re.MULTILINE | re.DOTALL)
    text = re.sub(r"!\[\[([^]]+)\]\]", r"[attachment: \1]", text)
    text = re.sub(r"\[\[([^]|#]+)(?:#[^]|]+)?(?:\|([^]]+))?\]\]", lambda m: m.group(2) or m.group(1), text)
    text = re.sub(r"!\[([^]]*)\]\([^)]+\)", r"[image: \1]", text)
    return text.strip()


def chunk_markdown(text: str, fallback_heading: str, target_chars: int = 1_600) -> list[tuple[str, str]]:
    text = _normalize_markdown(text)
    heading = fallback_heading
    sections: list[tuple[str, list[str]]] = []
    current: list[str] = []
    for line in text.splitlines():
        match = HEADING_RE.match(line)
        if match:
            if any(part.strip() for part in current):
                sections.append((heading, current))
            heading = match.group(2).strip()
            current = []
        else:
            current.append(line)
    if any(part.strip() for part in current):
        sections.append((heading, current))

    chunks: list[tuple[str, str]] = []
    for section_heading, lines in sections:
        paragraphs = [part.strip() for part in re.split(r"\n\s*\n", "\n".join(lines)) if part.strip()]
        buffer = ""
        for paragraph in paragraphs:
            if buffer and len(buffer) + len(paragraph) + 2 > target_chars:
                chunks.append((section_heading, buffer.strip()))
                buffer = ""
            if len(paragraph) > target_chars:
                sentences = re.split(r"(?<=[.!?])\s+|\n(?=\s*[-*])", paragraph)
                for sentence in sentences:
                    if buffer and len(buffer) + len(sentence) + 1 > target_chars:
                        chunks.append((section_heading, buffer.strip()))
                        buffer = ""
                    buffer = f"{buffer} {sentence}".strip()
            else:
                buffer = f"{buffer}\n\n{paragraph}".strip()
        if buffer:
            chunks.append((section_heading, buffer.strip()))
    return [(heading, body) for heading, body in chunks if body]


def ingest(source: Path, database: Path) -> IngestStats:
    source = source.expanduser().resolve()
    if not source.exists():
        raise FileNotFoundError(f"Source does not exist: {source}")
    files = _source_files(source)
    source_root = str(source if source.is_dir() else source.parent)
    now = datetime.now(timezone.utc).isoformat()
    indexed = unchanged = total_chunks = 0
    seen: set[str] = set()

    with connect(database) as connection:
        for path in files:
            relative = _relative_path(path, source)
            seen.add(relative)
            raw = path.read_text(encoding="utf-8", errors="replace")
            digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
            existing = connection.execute(
                "SELECT content_hash FROM sources WHERE path = ?", (relative,)
            ).fetchone()
            if existing and existing["content_hash"] == digest:
                unchanged += 1
                continue

            connection.execute("DELETE FROM chunks WHERE source_path = ?", (relative,))
            pieces = chunk_markdown(raw, path.stem)
            connection.executemany(
                "INSERT INTO chunks(source_path, heading, body, content_hash) VALUES (?, ?, ?, ?)",
                ((relative, heading, body, digest) for heading, body in pieces),
            )
            connection.execute(
                """
                INSERT INTO sources(path, source_root, content_hash, modified_ns, indexed_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(path) DO UPDATE SET
                    source_root=excluded.source_root,
                    content_hash=excluded.content_hash,
                    modified_ns=excluded.modified_ns,
                    indexed_at=excluded.indexed_at
                """,
                (relative, source_root, digest, path.stat().st_mtime_ns, now),
            )
            indexed += 1
            total_chunks += len(pieces)

        known = {
            row["path"]
            for row in connection.execute(
                "SELECT path FROM sources WHERE source_root = ?", (source_root,)
            )
        }
        removed_paths = sorted(known - seen) if source.is_dir() else []
        for relative in removed_paths:
            connection.execute("DELETE FROM chunks WHERE source_path = ?", (relative,))
            connection.execute("DELETE FROM sources WHERE path = ?", (relative,))
    return IngestStats(len(files), indexed, unchanged, len(removed_paths), total_chunks)


def _query_tokens(query: str) -> list[str]:
    return [
        token for token in TOKEN_RE.findall(query.lower())
        if len(token) > 1 and token not in STOP_WORDS
    ]


def _fts_query(query: str) -> str:
    tokens = _query_tokens(query)
    terms = []
    for token in tokens[:24]:
        clean = token.replace('"', "")
        terms.append(f'"{clean}"*' if len(clean) >= 4 else f'"{clean}"')
    return " OR ".join(terms)


def search(
    database: Path,
    query: str,
    limit: int = 5,
    *,
    original_only: bool = False,
) -> list[Passage]:
    expression = _fts_query(query)
    if not expression or not database.exists():
        return []
    with connect(database) as connection:
        rows = connection.execute(
            """
            SELECT source_path, heading, body, content_hash, bm25(chunks, 0.0, 1.5, 1.0) AS rank_score
            FROM chunks
            WHERE chunks MATCH ?
            ORDER BY rank_score
            LIMIT ?
            """,
            (expression, max(limit * 4, 20)),
        ).fetchall()
    query_tokens = _query_tokens(query)
    required_overlap = max(1, min(4, math.ceil(len(set(query_tokens)) * 0.5)))
    passages: list[Passage] = []
    for row in rows:
        source_path = row["source_path"]
        if source_path == "index.md":
            continue
        if original_only and not source_path.startswith("raw/"):
            continue
        haystack = " ".join((row["source_path"], row["heading"], row["body"])).lower()
        overlap = sum(1 for token in set(query_tokens) if token in haystack)
        if overlap < required_overlap:
            continue
        passages.append(
            Passage(
                rank=len(passages) + 1,
                path=source_path,
                heading=row["heading"],
                text=row["body"],
                score=float(-row["rank_score"]),
                source_hash=row["content_hash"],
            )
        )
        if len(passages) >= limit:
            break
    return passages


def format_evidence(passages: Iterable[Passage], max_chars: int) -> str:
    blocks: list[str] = []
    used = 0
    for passage in passages:
        block = f"[{passage.rank}] PATH: {passage.path}\nHEADING: {passage.heading}\n{passage.text}"
        if blocks and used + len(block) > max_chars:
            break
        blocks.append(block[: max_chars - used])
        used += len(block)
    return "\n\n".join(blocks)
