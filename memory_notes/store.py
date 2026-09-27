from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

MEMORY_TYPES = ("user", "feedback", "project", "reference")

_FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?(.*)\Z", re.DOTALL)
_LINK_RE = re.compile(r"\[\[([a-zA-Z0-9_-]+)\]\]")


@dataclass
class Note:
    name: str
    description: str
    type: str
    body: str
    path: Path | None = None
    updated: str = field(default_factory=lambda: datetime.now(timezone.utc).date().isoformat())

    def links(self) -> list[str]:
        return _LINK_RE.findall(self.body)

    def to_markdown(self) -> str:
        frontmatter = (
            f"---\n"
            f"name: {self.name}\n"
            f"description: {self.description}\n"
            f"metadata:\n"
            f"  type: {self.type}\n"
            f"  updated: {self.updated}\n"
            f"---\n\n"
        )
        return frontmatter + self.body.strip() + "\n"

    @classmethod
    def from_markdown(cls, text: str, path: Path | None = None) -> "Note":
        m = _FRONTMATTER_RE.match(text)
        if not m:
            raise ValueError(f"no frontmatter block found in {path or '<string>'}")
        header, body = m.groups()
        fields: dict[str, str] = {}
        note_type = "reference"
        for line in header.splitlines():
            line = line.strip()
            if line.startswith("type:"):
                note_type = line.split(":", 1)[1].strip()
            elif ":" in line and not line.startswith(" "):
                key, _, value = line.partition(":")
                fields[key.strip()] = value.strip()
        return cls(
            name=fields.get("name", path.stem if path else "unknown"),
            description=fields.get("description", ""),
            type=note_type,
            body=body.strip(),
            path=path,
        )


class MemoryStore:
    """A directory of Note files plus a generated MEMORY.md index.

    Layout matches the convention already used by hand: one markdown file per
    note (frontmatter + body), and a flat MEMORY.md index of one-line pointers,
    kept under ~150 chars each so it stays cheap to keep loaded in context.
    """

    def __init__(self, root: Path | str):
        self.root = Path(root).expanduser()
        self.root.mkdir(parents=True, exist_ok=True)
        self.index_path = self.root / "MEMORY.md"

    def _slug_path(self, name: str) -> Path:
        return self.root / f"{name}.md"

    def write(self, note: Note) -> Path:
        if note.type not in MEMORY_TYPES:
            raise ValueError(f"type must be one of {MEMORY_TYPES}, got {note.type!r}")
        path = self._slug_path(note.name)
        path.write_text(note.to_markdown())
        self._rebuild_index()
        return path

    def read(self, name: str) -> Note:
        path = self._slug_path(name)
        if not path.exists():
            raise FileNotFoundError(f"no memory named {name!r} in {self.root}")
        return Note.from_markdown(path.read_text(), path=path)

    def delete(self, name: str) -> bool:
        path = self._slug_path(name)
        if not path.exists():
            return False
        path.unlink()
        self._rebuild_index()
        return True

    def list(self, type: str | None = None) -> list[Note]:
        notes = []
        for path in sorted(self.root.glob("*.md")):
            if path.name == "MEMORY.md":
                continue
            try:
                note = Note.from_markdown(path.read_text(), path=path)
            except ValueError:
                continue
            if type is None or note.type == type:
                notes.append(note)
        return notes

    def search(self, query: str) -> list[Note]:
        q = query.lower()
        return [
            n for n in self.list()
            if q in n.name.lower() or q in n.description.lower() or q in n.body.lower()
        ]

    def _rebuild_index(self) -> None:
        lines = ["# Memory index", ""]
        for note in self.list():
            lines.append(f"- [{note.name}]({note.path.name}) — {note.description}")
        self.index_path.write_text("\n".join(lines) + "\n")
