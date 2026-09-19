# Claude Code Operating Model

Three markdown documents that describe one way to run Claude Code every day, across several projects, for months. They were written in May 2026 from the author's own setup. They stay here as a reference, with a section at the end on what he would do differently now.

## What this is

| File | Size | What it covers |
|------|------|----------------|
| `ezekiel-kit.md` | ~1,550 lines | The operating philosophy: ten rules, a failure database from about a thousand sessions, identity and CLAUDE.md templates, checklists, and the story of a first system (v1) that collapsed under its own complexity. |
| `memory-kit.md` | ~1,600 lines | The memory system: four atom types, the MEMORY.md index and its 200-line cap, atom lifecycle, what not to save, stale protection, ten failure modes, five hooks. |
| `blueprint.md` | ~2,400 lines | The full stack around it: three filesystem roots, three CLAUDE.md tiers, settings.json, 13 hooks, 5 skills, 3 agents, MCP servers, plugins, backup, provenance, adoption levels, anti-patterns. |

Everything in them is plain text and bash. No plugin, no library, no framework. Each kit opens with a two-line header that says when it was written and that it is a historical reference.

## Who it is for

Someone who runs Claude Code daily on more than one project and has met the three problems these documents answer: the session forgets everything, rules written in text get ignored, and every "one more safety check" makes the setup heavier. If you use Claude Code for one-off tasks, you do not need this.

The documents assume you have read the official Claude Code documentation. They are not a tutorial.

## How to adopt it

Read in this order:

1. `ezekiel-kit.md`, Part 1 (the ten rules) and Part 13 (the anti-complexity chapter). This is the why.
2. `memory-kit.md`, Parts 3 to 6 (atoms, the index, lifecycle) and Part 8 (what not to save).
3. `blueprint.md`, Parts 1 to 3 (roots, CLAUDE.md tiers, settings.json), then Part 4 (hooks) only for the hooks you decide to copy.

Copy first:

- A global `~/.claude/CLAUDE.md` of 30 to 60 lines with behavioral rules only (blueprint Part 2).
- One hook, `block-git-push.sh` (blueprint Part 4, hook A1), with the one-line test from the same part.
- A per-project `CLAUDE.md` with critical constraints and validation commands at the top (ezekiel-kit Part 11).
- The index format and the four atom types (memory-kit Parts 3 to 5).

Skip, or read later:

- The backup pipeline (blueprint Part 10), until you have memory worth losing.
- The war room pattern (memory-kit Part 10), until you run three or more projects at once.
- The research swarm and the multi-agent audit (blueprint Part 5). See the next section.
- Level 4 of any quick start.

Adapt everything. The documents describe one operator's setup, and the numbers in them (session counts, win rates, hook counts) are that operator's numbers from that time.

## What I would change today

The first system described in `ezekiel-kit.md` (v1) ran 968 sessions and collapsed under its own complexity. The setup in these three documents replaced it. The kit itself records the first relapse (S34: 21 hooks, 14 scripts, 7 plugins, cut back to 11 hooks). On 2026-09-15 the author cut it down again, harder. The current setup (v3) differs from the blueprint in five ways:

1. **Two hooks, not thirteen.** Only the ones that block a failure that actually happened. Everything advisory went.
2. **Four skills, not five plus swarms.** Status, wrap, research and new-project. A research question gets one agent; two or three only when comparing options. The 8-10-agent audit is gone.
3. **One hand-off file per task.** A `TASK.md`, written by the coordinating session and deleted by the project session when the task is done, replaces the verb vocabulary and the digest-plus-plan pair.
4. **One status file per project.** A `STATUS.md` (Updated, State, Next), rewritten at the end of each session, replaces `SESSION-DIGEST.md`, the project `MEMORY.md` and `PLAN.md`. Memory atoms remain, for corrections, decisions and surprising facts only.
5. **A doctor script that repairs the setup.** One script runs at every session start, checks the setup and fixes what drifted. The blueprint relies on quarterly reviews; a script that runs every time does not depend on anyone remembering.

Three agents remain (architect, researcher, verifier), used on demand, never by default. The hub's `CLAUDE.md` carries a written complexity budget: at most 2 hooks, 4 skills and 3 agents, and anything new must name the failure it prevents. That last rule is the one sentence the author would keep if he could keep only one.

## Attribution and license

MIT, see `LICENSE`. The public repositories whose ideas shaped some design choices are credited in `NOTICE.md`; the code in the documents was written from scratch. Corrections are welcome, see `CONTRIBUTING.md`. `scripts/check_links.py` checks that the links and anchors in the four documents resolve.

Maintained by Josip Lipak ([jlipak](https://github.com/jlipak)).
