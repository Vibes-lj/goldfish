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

Paste this repo's link to Claude Code and say "use this" — it'll run the
installer itself. Or run it yourself:

```bash
curl -fsSL https://raw.githubusercontent.com/Vibes-lj/goldfish/master/install.sh | bash
```

That one command clones goldfish, syncs its Python env, turns on brain-mcp's
transcript-capture hooks for Claude Code, and registers `goldfish` as an MCP
server via `claude mcp add` — restart Claude Code (or run `/mcp`) afterward
and the five tools below are live. Re-running it is safe (idempotent).

Prefer to wire it up by hand instead? See [manual setup](#manual-setup) below.

claude-mem's own hooks/worker aren't installed by the script — that's a
separate project with its own setup. `goldfish_context` just reads its
database read-only if you've already installed it yourself; see
`packages/claude-mem/README.md`.

## Manual setup

```bash
git clone https://github.com/Vibes-lj/goldfish.git
cd goldfish
uv sync
uv run --directory packages/brain brain-mcp install cc   # optional: transcript capture hooks
claude mcp add goldfish -s user -- uv run --directory "$(pwd)" goldfish serve
```

Or hand-edit your MCP config (e.g. `~/.claude.json` or a project `.mcp.json`):

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

## Roadmap

Rough priority order, none of this started yet unless marked:

- [x] One-command install (`install.sh` — clone, sync, hooks, `claude mcp add`)
- [ ] `install.sh` also registers goldfish for Codex (`~/.codex/config.toml`), not just Claude Code
- [ ] `goldfish uninstall` — clean removal mirroring `brain-mcp uninstall` (hooks, scheduler, MCP registration)
- [ ] Package goldfish as an installable Claude Code plugin (marketplace `.mcp.json` + `hooks.json`) instead of raw MCP config editing
- [ ] Optional claude-mem auto-install path in `install.sh`, for people who want `goldfish_context` populated out of the box
- [ ] `goldfish_remember` commits `memory_notes/` to a local git repo automatically, so curated notes get real version history
- [ ] Semantic (embedding) search over curated notes and recent context, not just brain's BM25 over raw transcript
- [ ] Surface brain's other capture lanes (Cursor, ChatGPT, Pi) through `goldfish_status` more prominently — the data's already there, just under-exposed
- [ ] A small local dashboard to browse all three tiers side by side, for people who don't want to think in tool calls

Have an idea or a use case this doesn't cover? Open an issue.

## Why

Most setups end up with two or three memory tools installed for different
reasons (a transcript recorder, a session-compression plugin, some markdown
notes) and no single place to ask "what do we know." Goldfish is that single
place — a thin, honest layer on top of tools that already do the hard parts
well.
