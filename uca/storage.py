"""Local stores: explicit opt-in memory, SQLite FTS5, facts, and bounded runs."""
from __future__ import annotations

from collections import OrderedDict
from pathlib import Path
from typing import Any
import copy
import json
import re
import sqlite3


_WORD = re.compile(r"[\wÀ-ÿ'-]+", re.UNICODE)


def query_terms(text: str) -> list[str]:
    return [term.lower() for term in _WORD.findall(text) if len(term) > 2][:24]


class ExplicitMemoryStore:
    """Reads only entries whose owner explicitly marked them as storable."""
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def status(self) -> tuple[bool, str]:
        if not self.path.exists():
            return False, f"Memory file not found: {self.path}"
        return True, "Explicit-memory store available"

    def search(self, text: str, limit: int = 6) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        try:
            loaded = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        entries = loaded.get("entries", loaded if isinstance(loaded, list) else [])
        terms = set(query_terms(text))
        found: list[tuple[int, dict[str, Any]]] = []
        for item in entries:
            if not isinstance(item, dict) or item.get("explicit") is not True:
                continue
            body = " ".join([str(item.get("text", "")), " ".join(map(str, item.get("tags", [])))])
            score = len(terms & set(query_terms(body)))
            if score:
                found.append((score, item))
        return [item for _, item in sorted(found, key=lambda pair: pair[0], reverse=True)[:limit]]


def initialize_knowledge_db(path: str | Path, table: str = "documents") -> None:
    """Create an empty FTS5 schema. It deliberately imports no web content."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(destination) as connection:
        connection.execute(
            f"CREATE VIRTUAL TABLE IF NOT EXISTS {validate_table(table)} "
            "USING fts5(doc_id UNINDEXED, content, provenance UNINDEXED, metadata UNINDEXED)"
        )
        connection.commit()


def validate_table(table: str) -> str:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", table):
        raise ValueError("Invalid local SQLite table name")
    return table


def import_documents(path: str | Path, records: list[dict[str, Any]], table: str = "documents") -> int:
    """Insert operator-supplied records into the local FTS5 index.

    Expected fields are `doc_id`, `content`, `provenance`, and optional
    `metadata`. This function neither downloads nor labels a corpus as complete.
    """
    initialize_knowledge_db(path, table)
    rows: list[tuple[str, str, str, str]] = []
    for item in records:
        identifier = item.get("doc_id", item.get("document_id"))
        content = item.get("content")
        if not isinstance(identifier, (str, int)) or not isinstance(content, str) or not content.strip():
            continue
        provenance = str(item.get("provenance", "operator_import"))
        metadata = item.get("metadata", {})
        rows.append((str(identifier), content, provenance, json.dumps(metadata, ensure_ascii=False)))
    if not rows:
        return 0
    with sqlite3.connect(path) as connection:
        connection.executemany(f"INSERT INTO {validate_table(table)} (doc_id, content, provenance, metadata) VALUES (?, ?, ?, ?)", rows)
        connection.commit()
    return len(rows)


class FTSKnowledgeStore:
    def __init__(self, path: str | Path, table: str = "documents", cache_enabled: bool = False) -> None:
        self.path = Path(path)
        self.table = validate_table(table)
        self.cache_enabled = cache_enabled
        self._cache: OrderedDict[tuple[Any, ...], list[dict[str, Any]]] = OrderedDict()

    def status(self) -> tuple[bool, str, int]:
        if not self.path.exists():
            return False, f"SQLite FTS5 database not found: {self.path}", 0
        try:
            with sqlite3.connect(self.path) as connection:
                count = int(connection.execute(f"SELECT count(*) FROM {self.table}").fetchone()[0])
            return True, f"SQLite FTS5 index available ({count} passages)", count
        except sqlite3.Error as error:
            return False, f"SQLite FTS5 index unavailable: {error}", 0

    def search(self, text: str, limit: int = 6) -> list[dict[str, Any]]:
        terms = query_terms(text)
        if not terms or not self.path.exists():
            return []
        # Cache only document retrieval (never user memory or model generations). The
        # local database signature invalidates results after an import/update.
        stat = self.path.stat()
        cache_key = (stat.st_mtime_ns, stat.st_size, tuple(terms), limit)
        if self.cache_enabled and cache_key in self._cache:
            self._cache.move_to_end(cache_key)
            return copy.deepcopy(self._cache[cache_key])
        # Terms are extracted locally and quoted, rather than passing user FTS grammar.
        match = " OR ".join('"' + term.replace('"', '""') + '"' for term in terms)
        sql = (f"SELECT doc_id, content, provenance, metadata, bm25({self.table}) "
               f"FROM {self.table} WHERE {self.table} MATCH ? ORDER BY bm25({self.table}) LIMIT ?")
        try:
            with sqlite3.connect(self.path) as connection:
                rows = connection.execute(sql, (match, limit)).fetchall()
        except sqlite3.Error:
            return []
        records: list[dict[str, Any]] = []
        for doc_id, content, provenance, metadata, rank in rows:
            try:
                meta = json.loads(metadata) if metadata else {}
            except json.JSONDecodeError:
                meta = {"raw_metadata": metadata}
            records.append({"document_id": str(doc_id), "content": str(content),
                            "provenance": str(provenance), "metadata": meta, "rank": float(rank)})
        if self.cache_enabled:
            self._cache[cache_key] = copy.deepcopy(records)
            self._cache.move_to_end(cache_key)
            while len(self._cache) > 128:
                self._cache.popitem(last=False)
        return records


class OperatorFactStore:
    """A transparent JSON fact source, not a substitute for MeTTa inference."""
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def load(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        try:
            parsed = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        values = parsed.get("facts", parsed if isinstance(parsed, list) else [])
        return [item for item in values if isinstance(item, dict) and item.get("id")]


class RunStore:
    def __init__(self, limit: int = 30) -> None:
        self.limit = limit
        self._items: OrderedDict[str, dict[str, Any]] = OrderedDict()

    def put(self, request_id: str, run: dict[str, Any]) -> None:
        self._items[request_id] = run
        self._items.move_to_end(request_id)
        while len(self._items) > self.limit:
            self._items.popitem(last=False)

    def get(self, request_id: str) -> dict[str, Any] | None:
        return self._items.get(request_id)

    def summaries(self) -> list[dict[str, Any]]:
        return [{"request_id": key, "answer": value.get("answer"), "created_at": value.get("created_at")}
                for key, value in reversed(self._items.items())]
