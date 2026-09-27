# Attribution

Goldfish combines two independent open-source projects, vendored in full under
`packages/`, with new original code (`goldfish/`, `memory_notes/`) that unifies
them behind one MCP server. Both upstream projects remain independently
useful and maintained — Goldfish is a derivative work, not a replacement.

## packages/brain — brain-mcp

- **Upstream**: [mordechaipotash/brain-mcp](https://github.com/mordechaipotash/brain-mcp)
- **Author**: Mordechai Potash
- **License**: MIT (full text preserved at `packages/brain/LICENSE`)
- **What it does here**: transcript recorder + cited search (`goldfish_search`,
  and the `brain` half of `goldfish_status`), imported directly as a Python
  dependency — unmodified from upstream.

## packages/claude-mem — claude-mem

- **Upstream**: [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem)
- **Author**: Alex Newman
- **License**: Apache License 2.0 (full text preserved at
  `packages/claude-mem/LICENSE`, `packages/claude-mem/NOTICE`)
- **What it does here**: session-compression context cache, read read-only
  from its own SQLite store by `goldfish/context_bridge.py` (`goldfish_context`)
  — vendored unmodified from upstream; goldfish never writes to its database
  or runs its own workers/hooks.

## New in this repo

- `memory_notes/` — curated durable-note store (frontmatter markdown + index),
  new code.
- `goldfish/` — the unifying MCP server (`goldfish_search`, `goldfish_context`,
  `goldfish_remember`, `goldfish_recall`, `goldfish_status`) and CLI, new code.

Both are original work, MIT licensed under this repo's top-level `LICENSE`.

If you maintain either upstream project and would like different attribution,
different vendoring terms, or removal, please open an issue.
