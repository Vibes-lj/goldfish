"""Goldfish MCP server — one set of tools over three memory tiers:

  goldfish_search    -> brain (full transcript history, cited file+line+sha256)
  goldfish_context   -> claude-mem (recent session-compression summaries)
  goldfish_remember  -> memory_notes (write a curated, durable note)
  goldfish_recall    -> memory_notes (read/search curated notes)
  goldfish_status    -> health across all three backends

brain-mcp and claude-mem each remain independently installable and useful; this
server does not replace them, it gives a caller one place to ask "what do we
know" without deciding up front which tier holds the answer.
"""

from __future__ import annotations

from typing import Any, Optional

from mcp.server.mcpserver import MCPServer

from . import config
from . import context_bridge
from memory_notes import MemoryStore, Note

mcp = MCPServer(
    "goldfish",
    title="goldfish — unified memory",
    instructions=(
        "One MCP server over three memory tiers for AI coding agents: "
        "goldfish_search (brain-mcp: full cited transcript history), "
        "goldfish_context (claude-mem: recent session-compression summaries), "
        "goldfish_remember/goldfish_recall (memory_notes: curated durable facts). "
        "goldfish_status reports which backends are actually installed and healthy."
    ),
)

_store = MemoryStore(config.memory_home())


@mcp.tool(title="Search full transcript history (cited or abstained)",
          annotations={"readOnlyHint": True})
def goldfish_search(query: str, agent: Optional[str] = None, limit: int = 10) -> dict[str, Any]:
    """Search full AI conversation history (Claude Code, Codex, etc.) via brain-mcp.

    Every result is a citation (file, line span, sha256) verifiable with the
    underlying brain-mcp toolset — never a synthesized/paraphrased claim.
    """
    try:
        from brain_mcp.recorder import api as brain_api
    except ImportError:
        return {"error": "brain-mcp not installed — see packages/brain in the goldfish repo"}
    return brain_api.search(query, agent=agent, limit=limit)


@mcp.tool(title="Recent session-compression summaries", annotations={"readOnlyHint": True})
def goldfish_context(limit: int = 5) -> dict[str, Any]:
    """Recent session-compression summaries from claude-mem, if installed."""
    db = config.claude_mem_db()
    if not context_bridge.is_available(db):
        return {"available": False, "reason": f"no claude-mem database at {db}"}
    return {"available": True, "summaries": context_bridge.recent_session_summaries(db, limit=limit)}


@mcp.tool(title="Write a curated, durable memory note")
def goldfish_remember(name: str, description: str, type: str, content: str) -> dict[str, Any]:
    """Write a curated, durable memory note (user/feedback/project/reference).

    Use this for facts worth carrying into future sessions — not for raw
    transcript (that's captured automatically by brain) or session summaries
    (that's claude-mem's job) — only hand-picked, still-true facts.
    """
    note = Note(name=name, description=description, type=type, body=content)
    path = _store.write(note)
    return {"written": str(path)}


@mcp.tool(title="Read or search curated memory notes", annotations={"readOnlyHint": True})
def goldfish_recall(name: Optional[str] = None, query: Optional[str] = None, type: Optional[str] = None) -> dict[str, Any]:
    """Read a curated memory note by name, or search/list curated notes."""
    if name:
        try:
            note = _store.read(name)
        except FileNotFoundError as e:
            return {"error": str(e)}
        return {"name": note.name, "description": note.description, "type": note.type, "body": note.body}
    if query:
        notes = _store.search(query)
    else:
        notes = _store.list(type=type)
    return {"notes": [{"name": n.name, "description": n.description, "type": n.type} for n in notes]}


@mcp.tool(title="Health across all three memory tiers", annotations={"readOnlyHint": True})
def goldfish_status() -> dict[str, Any]:
    """Health summary across all three memory tiers."""
    status: dict[str, Any] = {}

    try:
        from brain_mcp.recorder import api as brain_api
        status["brain"] = brain_api.health()
    except Exception as e:  # noqa: BLE001 - surface any backend failure as status, not a crash
        status["brain"] = {"ok": False, "error": str(e)}

    db = config.claude_mem_db()
    status["claude_mem"] = {"ok": context_bridge.is_available(db), "db_path": str(db)}

    notes = _store.list()
    status["memory_notes"] = {"ok": True, "count": len(notes), "root": str(_store.root)}

    return status


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
