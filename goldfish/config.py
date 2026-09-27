from __future__ import annotations

import os
from pathlib import Path


def memory_home() -> Path:
    """Root directory for curated memory_notes .md files."""
    return Path(os.environ.get("GOLDFISH_MEMORY_HOME", "~/.goldfish/memory")).expanduser()


def claude_mem_db() -> Path:
    """SQLite DB written by claude-mem, if installed. Read-only, never written by goldfish."""
    return Path(os.environ.get("CLAUDE_MEM_DB", "~/.claude-mem/claude-mem.db")).expanduser()
