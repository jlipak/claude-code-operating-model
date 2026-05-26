# Claude Code Operating Model

> A complete operator stack for Claude Code, distilled from production use across multiple long-running projects.
> Memory architecture. Operating philosophy. Full architectural blueprint.
> Drop it in, adapt it, or just read it to skip the failures someone else already paid for.

---

## What This Is

Three documents that together describe how to run Claude Code as a serious daily-driver — not a toy, not a one-shot helper, but as the operating system for your engineering work.

The patterns here weren't designed in a vacuum. They emerged from running Claude Code across multiple long-running projects in different domains, hitting every failure mode possible, and turning each failure into a permanent rule.

This isn't a framework. It's not a product. It's a set of plain markdown files that capture an operating model you can adopt whole, adapt piecewise, or use as a reference for building your own.

## What This Is NOT

- **Not a quick-start tutorial** for Claude Code basics — assumes you've read the official docs
- **Not a plugin or library** — every component is plain text + bash
- **Not a one-size-fits-all template** — opinionated, operator-tuned, requires adaptation
- **Not a finished product** — actively maintained, accepts iteration based on real failure modes
- **Not a recommendation** to copy uncritically — pick what fits, leave the rest

---

## The Three Documents

### `memory-kit.md` (~1500 lines)

> Complete memory system specification. The 4 atom types (user/feedback/project/reference), atom anatomy, the MEMORY.md 200-line index cap, lifecycle, 10 failure modes, 5 hooks for memory discipline, and a 4-level quick start.

**Read when:** You want to understand how persistent memory works in Claude Code — generic enough to adopt as a pattern, specific enough to teach the mechanics.

**Key insight:** Memory is plain markdown files. Index (always loaded) + atoms (on-demand load). Pruned aggressively, age-stamped on read, governed by a strict lifecycle. No vector DB. No black box.

### `blueprint.md` (~2400 lines)

> Full operator stack architecture. The 3-root filesystem model. 3-tier CLAUDE.md hierarchy. settings.json anatomy. 13 hooks across 4 categories. 5 user-invocable skills. 3 cost-tiered custom agents. MCP server roster. Plugin decision rationale. Memory namespaces. Off-site backup pipeline. Provenance map. Full event-by-event integration timeline. 4-tier adoption levels. 8 named anti-patterns with mitigations.

**Read when:** You want to see how everything fits together — beyond memory, the complete operator setup.

**Key insight:** Mature stacks are ~80% custom, ~10% borrowed, ~10% native platform features. Each hook earns its place against a real failure mode. Tests for hooks are non-negotiable. Backup pipeline matters. Quarterly platform-feature review prevents drift.

### `ezekiel-kit.md` (~1450 lines)

> Operating philosophy. The 10 Holy Rules. The Failure Database. Anti-complexity bible. Identity templates. Behavioral law. Operational checklists. Built on the ashes of a predecessor system (SHIKA) that collapsed at 968 sessions because complexity compounded unchecked.

**Read when:** You want the *why* behind the architecture. The cautionary tale. The philosophy that informs every other choice.

**Key insight:** Simplicity is the strategy. 636 lines of code at 96.4% win rate beats 4,977 lines at 46%. Rules without enforcement get violated; structural hooks that `exit 2` actually work. Every "safety check" addition added a new failure mode until the system collapsed.

---

## Recommended Reading Order

### Want depth in one sitting (~2-3 hours)

```
1. ezekiel-kit.md   →  Grounds you in the WHY. The cautionary tale.
2. memory-kit.md    →  The memory architecture. Heart of the system.
3. blueprint.md     →  The full operator stack. Body around the heart.
```

### Want quick orientation (~30 minutes)

```
1. This README                            5 min
2. blueprint.md Part 1-3 (filesystem + CLAUDE.md + settings)  15 min
3. blueprint.md Part 13-14 (adoption + anti-patterns)         10 min
```

### Want adoption template (~1 hour)

```
1. blueprint.md Part 13 — Adoption Levels (pick your level)   15 min
2. memory-kit.md Part 14 — Quick Start (memory specifically)  10 min
3. ezekiel-kit.md Part 1 — The 10 Holy Rules (operating principles)  15 min
4. Skim blueprint.md Part 4 (hooks) for the discipline patterns   20 min
```

### Want to evaluate this as a hiring/governance signal

```
1. blueprint.md Part 11 — Provenance Map (custom vs borrowed vs native)
2. blueprint.md Part 14 — Anti-Patterns and Trade-offs
3. memory-kit.md Part 12 — Failure Modes Catalog
4. ezekiel-kit.md Part 2 — The Failure Database
```

---

## Origin

This is documentation of an actual operating setup that's been running daily across multiple projects. The patterns earned their keep through repeated failure and iteration.

The repository is sanitized for sharing — no project-specific intel, no infrastructure identifiers, no personal data. The structure is what's valuable; the specifics are operator-tuned.

If you adopt patterns from here: track what works for *your* workflow, not what worked for someone else's. The discipline is more transferable than the specifics.

---

## License & Attribution

MIT License. Use freely, attribute when reasonable.

See `NOTICE.md` for attribution to concept patterns that inspired specific design choices (the operator stack draws on patterns from several public Claude Code ecosystem repos, with the code itself written from scratch).

---

## A Final Note

This is opinionated documentation. Some patterns will fit your workflow; some won't. The point isn't to convert you to one operator's choices — it's to show you that a coherent operating model is possible, and to give you concrete patterns to evaluate against your own needs.

If you read all three documents and adopt nothing — you've still seen what mature Claude Code use can look like, which raises the bar for what you build yourself.

If you adopt the patterns wholesale — track the trade-offs in `blueprint.md Part 14` and revisit quarterly.

Either way: build deliberately.

```
┌────────────────────────────────────────────────┐
│                                                 │
│   The blueprint is not the building.            │
│   But every building that lasts                 │
│   started with one.                             │
│                                                 │
└────────────────────────────────────────────────┘
```

---

*Maintained by SHIKA — feedback and patches welcome via issues.*
