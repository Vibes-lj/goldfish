# 🐠 Goldfish

Unified memory for AI coding agents. One MCP server, three tiers, no more
guessing which tool remembers what:

```
                    ┌──────────────────────┐
   your agent  ───► │   goldfish (MCP)     │
                    └──────────┬───────────┘
                               │
        ┌──────────────────────┼──────────────────────────┐
        ▼                      ▼                           ▼
┌───────────────┐     ┌────────────────────┐     ┌──────────────────┐
│  brain         │     │  claude-mem         │     │  memory_notes      │
│  full history  │     │  session context    │     │  curated facts     │
│  cited search  │     │  auto-compressed    │     │  hand-written      │
│  (vendored)    │     │  (vendored)         │     │  (new)             │
└───────────────┘     └────────────────────┘     └──────────────────┘
```

Three different jobs, three different tools, one thing you actually call:

| Tier | Tool | What it answers | Backing store |
|---|---|---|---|
| Transcript history | `goldfish_search` | "did we ever discuss X" — cited, never hallucinated | [brain-mcp](https://github.com/mordechaipotash/brain-mcp)'s DuckDB + append-only JSONL lake |
| Session context | `goldfish_context` | "what was I just doing" — recent auto-generated summaries | [claude-mem](https://github.com/thedotmack/claude-mem)'s SQLite store (read-only) |
| Curated notes | `goldfish_remember` / `goldfish_recall` | "what do we know about this user/project" — small, hand-picked, durable | plain frontmatter markdown, this repo |
| Everything | `goldfish_status` | is each tier actually installed and healthy | aggregates all three |

Goldfish doesn't replace brain-mcp or claude-mem — it vendors them as-is and
gives you one server to point an agent at instead of three. See
[ATTRIBUTION.md](ATTRIBUTION.md) for full upstream credit and licenses.

## Install

```bash
git clone https://github.com/Vibes-lj/goldfish.git
cd goldfish
uv sync
uv run goldfish status
```

Register it as an MCP server (e.g. in `~/.claude.json` or `.mcp.json`):

```json
{
  "mcpServers": {
    "goldfish": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/goldfish", "goldfish", "serve"]
    }
  }
}
```

claude-mem's own hooks/worker need to already be installed separately for
`goldfish_context` to have anything to read (goldfish only reads its database,
it doesn't run claude-mem itself). brain-mcp's capture hooks likewise need
their own install step — see each package's README under `packages/`.

## CLI

```bash
uv run goldfish status                                    # health across all 3 tiers
uv run goldfish remember my-note "one-liner" --type project --content "..."
uv run goldfish recall --query "my-note"
```

## Repo layout

```
goldfish/
├── goldfish/          # the unifying MCP server + CLI (new)
├── memory_notes/       # curated-note store: frontmatter .md + index (new)
├── packages/
│   ├── brain/          # vendored from mordechaipotash/brain-mcp (MIT)
│   └── claude-mem/      # vendored from thedotmack/claude-mem (Apache-2.0)
├── ATTRIBUTION.md
└── LICENSE              # MIT, covers goldfish/ + memory_notes/ only
```

## Why

Most setups end up with two or three memory tools installed for different
reasons (a transcript recorder, a session-compression plugin, some markdown
notes) and no single place to ask "what do we know." Goldfish is that single
place — a thin, honest layer on top of tools that already do the hard parts
well.
