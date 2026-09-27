"""memory_notes — curated, durable facts about a user/project, as linkable markdown notes.

This is the "long-term curated" tier of Goldfish: not a transcript log (that's brain),
not a session-compression cache (that's claude-mem), but small hand-shaped notes an
agent writes when it learns something worth carrying into future sessions — a
preference, a project fact, a piece of feedback, a pointer to an external system.
"""

from .store import MemoryStore, Note

__all__ = ["MemoryStore", "Note"]
__version__ = "0.1.0"
