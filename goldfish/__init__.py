"""goldfish — unified memory system for AI coding agents.

Combines three tiers behind one MCP server:
  - brain-mcp    : full cited transcript history (vendored, packages/brain)
  - claude-mem   : session-compression context cache (vendored, packages/claude-mem)
  - memory_notes : curated, durable facts (new, this repo)

See README.md for architecture and ATTRIBUTION.md for upstream credit.
"""

__version__ = "0.1.0"
