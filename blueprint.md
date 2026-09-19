# The Blueprint Kit — Complete Operator Architecture for Claude Code

> Written: May 2026, for Claude Code 2.x of that time (hook events, settings keys and built-in names as they were then).
> Status: historical reference; superseded in parts by the "What I would change today" section of the README.

> What lives where, why it lives there, and how it all connects.
> The complete operator stack — beyond memory atoms, beyond philosophy.
> The skeleton of a mature Claude Code setup, sanitized so anyone can adopt or evaluate.

> *"By the grace God has given me, I laid a foundation as a wise builder, and someone else is building on it. But each one should build with care."* — 1 Corinthians 3:10

---

## What This Document Is

A complete architectural reference for running Claude Code as a daily-driver across multiple long-running projects. Where the [memory-kit] taught the heart (memory atoms, lifecycle, failure modes), this blueprint shows the body — hooks, skills, agents, MCPs, backups, integration patterns, adoption paths.

If you've ever wondered:

- "What does a mature Claude Code setup actually look like?"
- "How do hooks, skills, and agents fit together?"
- "When should I use a plugin vs build my own?"
- "How do operators handle multi-project memory at scale?"
- "What's the difference between custom-built and platform-native components?"

This document answers those questions with a complete architectural walkthrough.

The patterns shown here emerged from running Claude Code as a daily driver across multiple long-running projects in different domains. They survived because they earned it. Each component documented here either prevents a real failure mode, accelerates a real workflow, or maintains a real continuity guarantee.

## What This Document Is NOT

- **Not a quick-start guide** — for that, see Part 13 (Adoption Levels)
- **Not a memory system spec** — for that, see [memory-kit]
- **Not a philosophy treatise** — for that, see [ezekiel-kit]
- **Not a tutorial on Claude Code basics** — assumes you've read the official docs
- **Not a recommendation for every operator** — pick what fits your workflow; not every component is universally valuable
- **Not a "drop this in and it works" template** — adoption requires deliberate adaptation to your context

The patterns here are evidence-based but operator-tuned. Your mileage will vary. Adopt or adapt with intent.

---

## Table of Contents

1. [Part 1: The Three-Root Model](#part-1-the-three-root-model)
2. [Part 2: CLAUDE.md Hierarchy](#part-2-claudemd-hierarchy)
3. [Part 3: settings.json — The Configuration Spine](#part-3-settingsjson--the-configuration-spine)
4. [Part 4: The Hook Layer](#part-4-the-hook-layer)
5. [Part 5: The Skill Vocabulary](#part-5-the-skill-vocabulary)
6. [Part 6: The Custom Agents — Cost-Tiered Subagents](#part-6-the-custom-agents--cost-tiered-subagents)
7. [Part 7: MCP Server Roster](#part-7-mcp-server-roster)
8. [Part 8: The Plugin Decision](#part-8-the-plugin-decision)
9. [Part 9: Memory Namespace Pattern](#part-9-memory-namespace-pattern)
10. [Part 10: The Backup Pipeline](#part-10-the-backup-pipeline)
11. [Part 11: Provenance Map — Custom vs Borrowed vs Native](#part-11-provenance-map--custom-vs-borrowed-vs-native)
12. [Part 12: Integration Diagram — Event by Event](#part-12-integration-diagram--event-by-event)
13. [Part 13: Adoption Levels](#part-13-adoption-levels)
14. [Part 14: Anti-Patterns and Trade-offs](#part-14-anti-patterns-and-trade-offs)

---

# Part 1: The Three-Root Model

A mature operator stack lives in exactly three filesystem roots. Understanding this layout is the foundation for everything else.

## The Big Picture

```
═══════════════════════════════════════════════════════════════════════════
                       OPERATOR STACK — FILESYSTEM ROOTS
═══════════════════════════════════════════════════════════════════════════

  ~/.claude/                          ← GLOBAL Claude Code installation
                                        Applies to ALL projects and machines
                                        Behavioral rules, hooks, skills, agents

  ~/<strategy-hub>/.claude/           ← WAR ROOM working directory
                                        Cross-project coordination
                                        Strategic memory namespace

  ~/<project-X>/                      ← PER-PROJECT working directory
                                        Execution context for ONE project
                                        Project-specific rules, memory, code

═══════════════════════════════════════════════════════════════════════════

  ~/.claude/
  │
  ├── CLAUDE.md                       Global behavioral rules
  ├── settings.json                   Permissions, env, hooks, statusline
  │
  ├── hooks/                          Custom shell scripts (typical: 8-15)
  ├── scripts/                        Off-hook automation (backup, sync)
  ├── skills/                         User-invocable rituals (typical: 3-7)
  ├── agents/                         Custom subagent definitions (typical: 2-5)
  │
  ├── projects/                       Per-working-directory memory namespaces
  │   ├── <war-room-slug>/memory/
  │   ├── <project-a-slug>/memory/
  │   ├── <project-b-slug>/memory/
  │   └── <project-n-slug>/memory/
  │
  ├── plugins/                        Plugin marketplace + cache
  │   ├── marketplaces/
  │   └── cache/
  │
  ├── shell-snapshots/                Bash session history (auto-managed)
  │
  └── (logs, telemetry, meta files)

═══════════════════════════════════════════════════════════════════════════

  ~/<strategy-hub>/                   ← Pick any directory to be your strategy hub
  │                                     (often a top-level config directory)
  │
  ├── CLAUDE.md                       Machine-level identity + project inventory
  ├── .claude/                        War room scope identifier
  ├── docs/                           Architectural documentation (this kit lives here)
  └── (your strategy artifacts)

═══════════════════════════════════════════════════════════════════════════

  ~/<project-X>/                      ← One per project
  │
  ├── CLAUDE.md                       Project identity + constraints
  ├── .claude/
  │   ├── settings.json               Project-scoped overrides (optional)
  │   ├── rules/                      Path-scoped behavioral rules
  │   └── skills/                     Project-specific skills (optional)
  │
  ├── SESSION-DIGEST.md               Per-session handoff (overwritten at /wrap)
  ├── MEMORY.md                       Project-specific operational state (optional)
  ├── PLAN.md                         Phase plan (optional)
  │
  └── (your code, tests, configs)

═══════════════════════════════════════════════════════════════════════════
```

## The Mental Model

Three roots map to three concerns:

```
ROOT 1: ~/.claude/                  ROOT 2: <strategy-hub>/          ROOT 3: <project>/
─────────────────                   ────────────────────             ─────────────────

GLOBAL                              STRATEGIC                        EXECUTION
Applies to all projects             Cross-project coordination       Single project

What lives here:                    What lives here:                 What lives here:
- Behavioral rules                  - War room memory                - Project identity
- Hooks (all projects)              - Cross-project intel            - Project rules
- Skills (all projects)             - Architecture docs              - Project memory
- Custom agents                     - Strategy artifacts             - Per-project tools
- Permissions + env                                                  - Project code
- Memory namespaces                  Why separate from global:        - Per-session handoff
- Plugin marketplace                 - Strategy is YOUR specific
- Backup pipeline                      operating model               Why separate from
                                     - May not apply to others        strategy hub:
Why separate from project:          - Higher concentration of         - Project-specific
- Survives machine moves              identifying intel                  constraints
- Shared across projects                                              - Lifecycle bound to
- Operator-level concerns                                                project lifecycle
                                                                      - Multiple operators
                                                                        may share these
```

## Why This Pattern Wins

**One root per concern.** Mixing concerns (e.g., putting project-specific behavioral rules into `~/.claude/CLAUDE.md`) creates drift. Each root has a clear ownership boundary, which makes the system survive moves, audits, and operator changes.

**Global stays portable.** If you move to a new machine, `~/.claude/` is your operating system. Backup, rsync, restore — your full Claude operating model travels with you.

**Strategy hub is private.** The war room can be excluded from public sharing while individual project repos can be public. This separation enables a public/private mix without leaking strategic intel.

**Projects stay focused.** Each project repo has its own CLAUDE.md + memory + session digest. A new contributor joining the project gets project-scoped context without needing access to operator-level strategy.

## Common Misconfigurations

```
ANTI-PATTERN                        SYMPTOM
────────────                        ────────

Everything in ~/.claude/CLAUDE.md   60+ project-specific rules pollute global
                                    behavioral baseline; hard to onboard new machine

No strategy hub                     Cross-project intel duplicates into every
                                    project memory; drift accumulates

Per-project hooks duplicated        Same hook copied into N project/.claude/
                                    directories; updating means N edits

CLAUDE.md mixed with code           Reviewers can't tell behavioral rules from
                                    code conventions; rules get treated as docs
```

The three-root model resolves all of these.

---

# Part 2: CLAUDE.md Hierarchy

CLAUDE.md files are the **first thing Claude reads on every prompt.** They define identity, behavioral rules, and constraints. They are the single most powerful lever in the entire stack — small files with outsized influence.

## The Three Tiers

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  TIER 1A: ~/.claude/CLAUDE.md  (USER-GLOBAL)                            │
│  ─────────────────────────────────────                                  │
│                                                                         │
│  Scope: Every project, every machine that syncs ~/.claude/              │
│                                                                         │
│  Owns:                                                                  │
│    · Behavioral guarantees (verify before claim done; faithful          │
│      reporting; comment discipline; assertiveness)                      │
│    · Communication style preferences                                    │
│    · Tool-use discipline (Read before Edit, Grep before assert)         │
│    · Subagent cost-tiering policy                                       │
│    · Things that should be true in EVERY conversation                   │
│                                                                         │
│  Does NOT own:                                                          │
│    · Identity ("I am X")                                                │
│    · Project inventory                                                  │
│    · Machine-specific paths or hostnames                                │
│                                                                         │
│  Typical size: 30-60 lines                                              │
│  Effect: Shapes EVERY response in EVERY project                         │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  TIER 1B: <strategy-hub>/CLAUDE.md  (MACHINE-LEVEL)                     │
│  ─────────────────────────────────────────                              │
│                                                                         │
│  Scope: This machine's Desktop tree (or wherever the hub lives)         │
│                                                                         │
│  Owns:                                                                  │
│    · Operator identity ("I am X, my role is Y")                         │
│    · Active project inventory (table of projects + status)              │
│    · Workflow vocabulary (cook / suggest / status / wrap)               │
│    · Top-level rules ("never push without explicit OK")                 │
│    · Infrastructure references (servers, accounts, platforms)           │
│                                                                         │
│  Does NOT own:                                                          │
│    · Behavioral guarantees (those live in Tier 1A)                      │
│    · Project-specific code conventions                                  │
│                                                                         │
│  Typical size: 50-100 lines                                             │
│  Effect: Establishes WHO is operating and WHAT they're operating on     │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  TIER 1C: <project>/CLAUDE.md  (PROJECT-SPECIFIC)                       │
│  ────────────────────────────────────────                               │
│                                                                         │
│  Scope: One project directory                                           │
│                                                                         │
│  Owns:                                                                  │
│    · Project identity and one-line purpose                              │
│    · Critical constraints (non-negotiable rules for this code)          │
│    · Validation commands (exact commands to verify code works)          │
│    · Codebase map (top 5 files/modules)                                 │
│    · Project-specific workflow notes                                    │
│                                                                         │
│  Does NOT own:                                                          │
│    · Anything that applies across projects                              │
│    · Operator identity                                                  │
│                                                                         │
│  Typical size: 30-100 lines                                             │
│  Effect: Project-specific constraints applied automatically             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Loading Order and Cascade

When a session starts in any project directory:

```
1. Read ~/.claude/CLAUDE.md            ← Global behavioral baseline
2. Read <strategy-hub>/CLAUDE.md       ← Machine identity (if in hub tree)
3. Read <project>/CLAUDE.md            ← Project specifics (if exists)
4. Apply: more specific overrides less specific
```

The cascade is intentional. Global rules are stable across years. Machine rules change per setup. Project rules change per task. Each layer can refine the layer above without polluting it.

## The Critical Asymmetry

Most operators put **everything in `~/.claude/CLAUDE.md`** — behavioral rules, identity, projects, validation commands, codebase maps. This is a mistake.

The three-tier split is *intentional separation of concerns*:

- **~/.claude/CLAUDE.md** = ONLY behavioral rules that apply to every conversation, every project, every machine. If you started using Claude Code tomorrow on a different machine, these rules should still apply unchanged.
- **<strategy-hub>/CLAUDE.md** = identity + projects + workflow vocabulary that's specific to THIS machine and THIS operator. Different machine, different file.
- **<project>/CLAUDE.md** = constraints unique to ONE project. Other projects don't need to know about them.

A different machine can have a different <strategy-hub>/CLAUDE.md. A different project can override workflow vocabulary. The global behavioral baseline stays constant.

This pattern shows up in many production systems: stable inner core, mutable outer layers.

## Anti-Patterns in CLAUDE.md Design

**Anti-pattern 1: The mega-file.**
One CLAUDE.md, 600+ lines, mixes everything. Hard to maintain, hard to reason about, hard to onboard new machines.

**Anti-pattern 2: Duplication across tiers.**
Same rule appears in global and project CLAUDE.md. Drift inevitable — one gets updated, the other doesn't. Wasted tokens on every prompt.

**Anti-pattern 3: Aspirational rules.**
"Write clean code." "Be thorough." Empty calories. Rules need to be specific + actionable. "Run `pytest tests/` after modifying any `.py` file" is a rule. "Be thorough" is wishful thinking.

**Anti-pattern 4: Metadata-first ordering.**
Leading with crate name, version, or folder structure before constraints. The model gives most attention to what comes first. Critical constraints come first; metadata comes last (or moves to docs/).

**Anti-pattern 5: "See also" sections.**
If it's not actionable, delete it. CLAUDE.md is read on every prompt — every line costs tokens. "See docs/architecture.md for more" wastes tokens for no behavioral effect.

---

# Part 3: settings.json — The Configuration Spine

`~/.claude/settings.json` is the registry for everything: permissions, environment variables, hook registrations, status line, plugin enablement. It is the operator's central configuration file.

## Section 1: Environment Variables

Mature setups configure 4-8 environment variables to tune Claude Code's behavior:

```json
{
  "env": {
    "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "80",
    "CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR": "1",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
    "CLAUDE_CODE_DISABLE_FAST_MODE": "1",
    "CLAUDE_CODE_MAX_TOOL_USE_CONCURRENCY": "15",
    "CLAUDE_CODE_SUBAGENT_MODEL": "sonnet"
  }
}
```

| Variable | Effect | Trade-off |
|----------|--------|-----------|
| `AUTOCOMPACT_PCT_OVERRIDE=80` | Context compacts at 80% capacity (later than default) | More room before flush; risk of running out if very long session |
| `BASH_MAINTAIN_PROJECT_WORKING_DIR=1` | Bash tool keeps cwd across calls (no `cd` reset) | Cleaner multi-step bash flows; behavior differs from default |
| `DISABLE_NONESSENTIAL_TRAFFIC=1` | Less telemetry, less network noise | Slightly less debugging info; privacy gain |
| `DISABLE_FAST_MODE=1` | Always full thinking depth, never streamlined output | Higher latency, much higher quality per response |
| `MAX_TOOL_USE_CONCURRENCY=15` | Up to 15 parallel tool calls per turn (vs default lower) | Faster batch reads; risk of token burn if abused |
| `SUBAGENT_MODEL=sonnet` | Subagents run on Sonnet (cheaper than Opus) | 60% cost savings on subagent work; sufficient quality for research |

The `DISABLE_FAST_MODE=1` is the most consequential — it means EVERY response goes through deep thinking. Higher latency, much higher quality. For director-level operators where the value of one good output exceeds 100x the API cost, this is correct. For junior dev work, would be wasteful.

## Section 2: Permissions (Allow/Deny)

A mature setup has ~20-30 allow entries and ~10 deny entries. The DENY list should be focused (specific risks) rather than bloated (everything that might go wrong).

```
ALLOW (typical)                        DENY (typical)
─────                                  ────

Built-in tools (15):                   Git destructive (5):
  Read, Edit, Write, Agent              git push *
  Bash, Glob, Grep                      git push
  WebSearch, WebFetch                   git reset --hard *
  NotebookEdit                          git clean -f *
  TaskCreate/Update/Get/List/Stop       git checkout -- *
  EnterPlanMode / ExitPlanMode
  EnterWorktree / ExitWorktree          Filesystem destructive (3):
  CronCreate / CronDelete / CronList     rm -rf /
  AskUserQuestion                        rm -rf ~
  Skill, ToolSearch                      rm -rf /*
  ListMcpResourcesTool
  ReadMcpResourceTool                   Privilege escalation (2):
                                         sudo *
MCP wildcards (one per server):         chmod 777 *
  mcp__<server-1>__*
  mcp__<server-2>__*
  ...
```

**Design principle for DENY list:**

The DENY list should target operations that genuinely cause unrecoverable damage. A bloated DENY list leads to permission fatigue. A focused DENY list catches the things that matter.

Specifically:
- **Hard-to-reverse operations** belong in DENY (git push, git reset --hard, rm -rf /, sudo)
- **Reversible operations** don't (file edits, reads, normal bash commands)
- **Operations easily reverted** can be allowed (commit creates, branch creates)

**Belt-and-suspenders pattern:**

Note that `git push *` and `git push` are both denied. This is intentional — the permission layer denies, AND a hook (see Part 4) also blocks. Two independent gates on the same operation. Reason: pushing the wrong branch is unrecoverable on a public remote. The cost of a redundant check is zero. The cost of one missed push is hours.

## Section 3: Hook Registry

The hook registry maps events to scripts. A mature setup wires 8-15 hooks into 6-10 lifecycle events.

```json
{
  "hooks": {
    "SessionStart": [
      { "matcher": "", "hooks": [{ "type": "command", "command": "bash ~/.claude/hooks/session-start.sh" }] }
    ],
    "UserPromptSubmit": [
      { "matcher": "", "hooks": [{ "type": "command", "command": "bash ~/.claude/hooks/scan-secrets.sh" }] }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "bash ~/.claude/hooks/block-git-push.sh" },
          { "type": "command", "command": "bash ~/.claude/hooks/block-git-add-all.sh" }
        ]
      },
      {
        "matcher": "Write|Edit",
        "hooks": [
          { "type": "command", "command": "bash ~/.claude/hooks/block-versioned-files.sh" },
          { "type": "command", "command": "bash ~/.claude/hooks/block-secrets-in-code.sh" }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [{ "type": "command", "command": "bash ~/.claude/hooks/auto-format.sh" }]
      }
    ],
    "PostToolUseFailure": [
      {
        "matcher": "Bash",
        "hooks": [{ "type": "command", "command": "bash ~/.claude/hooks/post-bash-failure.sh" }]
      }
    ],
    "Stop": [
      { "matcher": "", "hooks": [{ "type": "command", "command": "bash ~/.claude/hooks/stop-checklist.sh" }] }
    ],
    "PreCompact": [
      { "matcher": "", "hooks": [{ "type": "command", "command": "bash ~/.claude/hooks/precompact-save.sh" }] }
    ],
    "PostCompact": [
      { "matcher": "", "hooks": [{ "type": "command", "command": "bash ~/.claude/hooks/post-compact-recover.sh" }] }
    ],
    "TaskCompleted": [
      { "matcher": "", "hooks": [{ "type": "command", "command": "bash ~/.claude/hooks/task-completed-verify.sh" }] }
    ],
    "SessionEnd": [
      {
        "matcher": "",
        "hooks": [
          { "type": "command", "command": "bash ~/.claude/hooks/session-end-digest.sh" },
          { "type": "command", "command": "bash ~/.claude/scripts/backup-state.sh" }
        ]
      }
    ]
  }
}
```

Full hook details in Part 4.

## Section 4: Status Line

A custom status line gives operator visibility into model, context usage, and identity. Typical render:

```
Claude Opus 4.7  [████████░░] 80%  <operator-tag>
```

The script reads JSON from Claude Code stdin, extracts `display_name`, `used_percentage`, token counts, and prints with ANSI color codes. Always ends with an operator identification tag.

## Section 5: Plugin Enablement

The marketplace ships dozens of plugins. Mature setups typically enable 0-3. Why so few? Most plugin functionality can be replicated with custom hooks/skills, with full control over edge cases.

```json
{
  "enabledPlugins": {
    "<plugin-name>@claude-plugins-official": true
  }
}
```

Common exception: LSPs (language servers) like `rust-analyzer-lsp`, `pyright-lsp`, `typescript-lsp` — these are too much work to roll custom, and the plugin abstraction is the right one.

## Section 6: Top-Level Configs

```json
{
  "effortLevel": "high",
  "skipDangerousModePermissionPrompt": true,
  "verbose": true
}
```

- `effortLevel: "high"` — max reasoning depth on every response. Default is typically "medium." High is appropriate for director-level operators.
- `skipDangerousModePermissionPrompt: true` — operator has acknowledged the trade-off, doesn't want repeated prompts. Use carefully.
- `verbose: true` — detailed tool call output for transparency. Trade-off: more text, more clarity.

## Configuration Maturity Score

```
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│  Default Claude Code install:    0 hooks, 0 env vars        │
│  Minimal setup (Level 1):        3 hooks, 1 env var          │
│  Standard setup (Level 2):       8 hooks, 3 env vars         │
│  Full Power setup (Level 3):     13 hooks, 6 env vars        │
│  Godmode setup (Level 4):        13 hooks, 6+ env vars       │
│                                                              │
│  Each level adds discipline at the cost of complexity.       │
│  Pick the level your workflow can sustain.                   │
└─────────────────────────────────────────────────────────────┘
```

---

# Part 4: The Hook Layer

Hooks are the **structural enforcement** layer. They run as shell commands at specific Claude Code lifecycle events. Text rules get violated at a high rate; hooks that `exit 2` cannot be violated — the operation is physically blocked at the shell level.

A mature operator setup typically has 8-15 hooks wired into 6-10 lifecycle events. This blueprint shows the canonical 13-hook pattern.

## The Four Hook Categories

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  CATEGORY A: BLOCK  (exit 2)                                        │
│  ─────────────────                                                  │
│  Stops the operation entirely. Physically prevents harm.            │
│  Use sparingly — only for genuinely unrecoverable actions.          │
│                                                                     │
│  CATEGORY B: INJECT (exit 0, stdout becomes model context)          │
│  ─────────────────                                                  │
│  Adds information to the conversation. Used for state recovery,     │
│  boot orientation, post-compact recovery.                           │
│                                                                     │
│  CATEGORY C: ADVISORY (exit 0, stdout shown as guidance)            │
│  ─────────────────                                                  │
│  Warns without blocking. Steers behavior toward better patterns     │
│  without forcing them. Lower friction than BLOCK.                   │
│                                                                     │
│  CATEGORY D: WORKFLOW (exit 0, file mutations or housekeeping)      │
│  ─────────────────                                                  │
│  Automated tasks that don't need model output — auto-format,        │
│  auto-digest, post-action cleanup.                                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Category A: BLOCK Hooks (6 hooks)

### Hook A1: `block-git-push.sh` — Anti-Push Guard

**Event:** `PreToolUse:Bash`
**Exit semantics:** `exit 2` = HARD BLOCK
**Purpose:** Prevent accidental git push to remote.

```bash
#!/bin/bash
# Prevents accidental git push — all work stays local unless explicitly told
INPUT=$(cat)
CMD=$(echo "$INPUT" | python -c "
import json, sys
try:
    d = json.load(sys.stdin)
    print(d.get('tool_input', {}).get('command', ''))
except Exception:
    print('')
" 2>/dev/null)
if echo "$CMD" | grep -qP 'git\s+push'; then
    echo "BLOCKED: git push is not allowed. LOCAL ONLY — never push unless explicitly told."
    exit 2
fi
```

**Why it exists:** Pushing the wrong branch to a public remote is unrecoverable. This hook + the matching DENY entry in settings.json create double-gate protection.

### Hook A2: `block-git-add-all.sh` — No-Add-All Guard

**Event:** `PreToolUse:Bash`
**Exit semantics:** `exit 2` = HARD BLOCK
**Purpose:** Force staging specific files instead of bulk `-A`/`--all`/`.`.

The regex matches `git add -A`, `git add --all`, and `git add .` (with optional trailing whitespace). Forces the operator (or Claude) to specify which files to stage, preventing accidental staging of `.env`, credentials, or large binaries.

**Failure prevented:** Staging garbage. By forcing `git add <file>`, you read what you're staging.

### Hook A3: `scan-secrets.sh` — Pre-Submission Prompt Scanner

**Event:** `UserPromptSubmit`
**Exit semantics:** `exit 2` = BLOCK submission
**Purpose:** Prevent the operator from accidentally pasting secrets into a prompt.

The regex matches canonical credential prefixes — Anthropic keys, AWS access keys, GitHub personal access tokens, PEM-armored key file headers, Slack tokens — by their distinctive prefixes plus length requirements. When matched, the prompt is blocked before it leaves the operator's terminal.

This is *operator self-protection.* It catches the moment when a debug log paste contains a credential.

### Hook A4: `block-secrets-in-code.sh` — Write/Edit Secret Scanner

**Event:** `PreToolUse:Write|Edit`
**Exit semantics:** `exit 2` = HARD BLOCK
**Purpose:** Prevent Claude from writing secrets into files.

Different from Hook A3 — A3 catches operator-submitted prompts, A4 catches model-generated code. Both gates needed: operator can paste a secret accidentally, model can hallucinate one.

**Skip if file is `.env*`** — those files are SUPPOSED to have secrets.

**Patterns detected (described generically):**
- API keys with `sk-` prefix followed by 20+ alphanumeric characters
- OAuth tokens with `ghp_` / `gho_` / `github_pat_` prefix
- PEM-armored private key file headers
- 64-character hexadecimal strings (common for crypto private keys)
- Slack tokens with `xox[bpoas]-` prefix

**Battle-test note:** Writing documentation about this hook will, ironically, trigger the hook if the documentation contains literal credential patterns. Obfuscate literal patterns in docs (use descriptive text or regex placeholders) to avoid self-blocking when documenting the system.

### Hook A5: `block-versioned-files.sh` — No-Copies Guard

**Event:** `PreToolUse:Write|Edit`
**Exit semantics:** `exit 2` = HARD BLOCK
**Purpose:** Prevent creation of `_v2`, `_backup`, `_new`, `_old`, `_copy`, `(1)`, `(2)` versioned copies.

```bash
#!/bin/bash
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | grep -oP '"file_path"\s*:\s*"[^"]*"' | head -1 | sed 's/.*: *"//;s/"$//')
[ -z "$FILE_PATH" ] && exit 0
BASENAME=$(basename "$FILE_PATH")

if echo "$BASENAME" | grep -qiE '_(v[0-9]+|backup|new|old|copy|temp|bak|orig)\.[^.]+$'; then
  echo "BLOCKED: Do not create versioned/backup files ($BASENAME). Edit the original file instead." >&2
  exit 2
fi

if echo "$BASENAME" | grep -qiE '\([0-9]+\)\.|[\s_]copy\b'; then
  echo "BLOCKED: Do not create numbered copies ($BASENAME). Edit the original file instead." >&2
  exit 2
fi

exit 0
```

**Failure prevented:** The "I'll just create a v2 to be safe" antipattern. Versioned copies fragment the codebase, drift from the original, and never get deleted.

### Hook A6: `stop-checklist.sh` — Pre-Stop Verification

**Event:** `Stop`
**Exit semantics:** `exit 2` = CONTINUE conversation (don't stop yet)
**Purpose:** Force a hygiene check before allowing session stop with uncommitted changes.

```bash
#!/bin/bash
# Reads stdin JSON; on retry attempts (after we already blocked once),
# stop_hook_active will be true — we MUST return success to avoid
# infinite retry loop (default cap is 9 retries).

INPUT=""
if [ ! -t 0 ]; then
  INPUT=$(cat)
fi

# Retry attempt — Claude already saw the message, allow stop
if echo "$INPUT" | grep -q '"stop_hook_active"[[:space:]]*:[[:space:]]*true'; then
  exit 0
fi

# Check for uncommitted changes in current git repo
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  CHANGES=$(git status --porcelain 2>/dev/null | head -5)
  if [ -n "$CHANGES" ]; then
    echo "BEFORE STOPPING: You have uncommitted changes. Did you commit? Did you update MEMORY.md? Did you update SESSION-DIGEST.md?" >&2
    exit 2
  fi
fi

exit 0
```

**Critical fix:** the `stop_hook_active` check. Without it, the Stop hook can retry up to 9 times, wasting minutes per session. This single line of bash, born from a real incident, prevents the loop.

## Category B: INJECT Hooks (3 hooks)

### Hook B1: `precompact-save.sh` — Pre-Compaction State Snapshot

**Event:** `PreCompact`
**Purpose:** Before context auto-compacts (typically at 80% capacity), inject load-bearing state into the compaction summary.

```bash
#!/bin/bash
CWD=$(pwd)
PROJECT_NAME=$(basename "$CWD")

echo "=== PRE-COMPACT CONTEXT SAVE ==="
echo "Project: $PROJECT_NAME"
echo "Working directory: $CWD"
echo "Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo ""
  echo "Git branch: $(git branch --show-current)"
  echo "Last commit: $(git log --oneline -1)"
  echo "Uncommitted files: $(git status --porcelain | wc -l)"
fi

if [ -f "memory/MEMORY.md" ]; then
  echo ""
  echo "=== MEMORY.md SNAPSHOT ==="
  head -50 memory/MEMORY.md
fi

if [ -f "SESSION-DIGEST.md" ]; then
  echo ""
  echo "=== SESSION-DIGEST SNAPSHOT ==="
  head -30 SESSION-DIGEST.md
fi

echo ""
echo "=== CRITICAL: Preserve all above context through compaction ==="

exit 0
```

**This is the anti-amnesia hook.** Before Claude Code summarizes old messages, this hook dumps git state, memory index, and digest. The summary that survives compaction includes this state — so the post-compact Claude knows where it is.

### Hook B2: `post-compact-recover.sh` — Post-Compaction Recovery

**Event:** `PostCompact`
**Purpose:** After compaction completes, inject recovery context so the post-compact Claude immediately re-grounds.

Partner hook to B1. PreCompact saves the snapshot, PostCompact reinjects it. Together they bridge the discontinuity that compaction creates.

### Hook B3: `session-start.sh` — Boot Banner

**Event:** `SessionStart`
**Purpose:** Inject project orientation at the start of every session.

```bash
#!/bin/bash
CWD=$(pwd)
PROJECT_NAME=$(basename "$CWD")

echo "=== SESSION START: $PROJECT_NAME ==="
echo "Directory: $CWD"
echo "Time: $(date '+%Y-%m-%d %H:%M')"

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Git: $(git branch --show-current) | $(git log --oneline -1) | $(git status --porcelain 2>/dev/null | wc -l) uncommitted"
fi

[ -f "CLAUDE.md" ] && echo "CLAUDE.md: present"
[ -f "memory/MEMORY.md" ] && echo "MEMORY.md: present"
[ -f "SESSION-DIGEST.md" ] && echo "SESSION-DIGEST.md: present — read for last session context"

exit 0
```

**This is the boot brief.** Every session starts with this banner — Claude knows immediately what project, what git state, and which context files to read.

## Category C: ADVISORY Hooks (2 hooks)

### Hook C1: `post-bash-failure.sh` — Bash Failure Alert

**Event:** `PostToolUseFailure:Bash`
**Purpose:** When a bash command fails, surface the failure with diagnostic guidance to prevent blind retries.

```bash
#!/bin/bash
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
EXIT_CODE=$(echo "$INPUT" | jq -r '.tool_result.exitCode // .exit_code // empty')
STDERR=$(echo "$INPUT" | jq -r '.tool_result.stderr // empty')

[ -z "$COMMAND" ] && exit 0

echo "BASH COMMAND FAILED (exit $EXIT_CODE): $COMMAND"
[ -n "$STDERR" ] && echo "STDERR: $(echo "$STDERR" | head -5)"
echo "GUIDANCE: Diagnose the root cause before retrying. Do NOT retry the same command blindly."

exit 0
```

**Failure prevented:** The blind-retry loop. Without this hook, Claude can retry a failing command 3-5 times before re-evaluating.

### Hook C2: `task-completed-verify.sh` — Task Completion Guard

**Event:** `TaskCompleted`
**Purpose:** Warn when marking a task complete with many uncommitted files (suggests work isn't really done).

Currently warning-only. Could be upgraded to BLOCK if completion claims drift. Operator chose warning mode for ergonomic reasons.

## Category D: WORKFLOW Hooks (2 hooks)

### Hook D1: `session-end-digest.sh` — Auto-Digest Stub

**Event:** `SessionEnd`
**Constraint:** 1.5-second timeout — must be FAST, no git ops/network
**Purpose:** Write a placeholder SESSION-DIGEST.md so post-session there is at minimum a timestamped marker.

```bash
#!/bin/bash
CWD=$(pwd)
PROJECT_NAME=$(basename "$CWD")
TIMESTAMP=$(date '+%Y-%m-%d %H:%M')

[ ! -f "$CWD/CLAUDE.md" ] && [ ! -d "$CWD/.claude" ] && exit 0

DIGEST_FILE="$CWD/SESSION-DIGEST.md"

{
  echo "# Session Digest — $TIMESTAMP"
  echo ""
  echo "## Quick State"
  echo "- Project: $PROJECT_NAME"
  echo "- Directory: $CWD"
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "- Branch: $(git branch --show-current 2>/dev/null)"
    echo "- Last commit: $(git log --oneline -1 2>/dev/null)"
    echo "- Uncommitted files: $(git status --porcelain 2>/dev/null | wc -l)"
  fi
  echo ""
  echo "## Note"
  echo "Auto-generated at session end. Update manually with session details."
} > "$DIGEST_FILE" 2>/dev/null

exit 0
```

**Known limitation:** This produces a near-empty placeholder. The substantive digest (what got done, key decisions, NEXT items) is captured manually via the `/wrap` skill. The auto-stub is a fallback, not a replacement for `/wrap`.

### Hook D2: `auto-format.sh` — Post-Write Formatter

**Event:** `PostToolUse:Write|Edit`
**Purpose:** Auto-format written files based on extension.

```bash
#!/bin/bash
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_input.filePath // empty')

[ -z "$FILE_PATH" ] || [ ! -f "$FILE_PATH" ] && exit 0

case "$FILE_PATH" in
  *.py) command -v ruff &>/dev/null && { ruff format "$FILE_PATH" 2>/dev/null; ruff check --fix "$FILE_PATH" 2>/dev/null; } ;;
  *.rs) command -v rustfmt &>/dev/null && rustfmt "$FILE_PATH" 2>/dev/null ;;
  *.js|*.ts|*.jsx|*.tsx)
    command -v npx &>/dev/null && [ -f "node_modules/.bin/prettier" ] && npx prettier --write "$FILE_PATH" 2>/dev/null
    ;;
esac

exit 0
```

Promoted from project-scoped to global because it's universally useful. Classic pattern: start scoped, promote when broadly valuable.

## The 13-Hook Summary Table

```
┌────┬──────────────────────────┬─────────────────────────┬──────────┐
│ #  │ Hook                     │ Event                   │ Exit     │
├────┼──────────────────────────┼─────────────────────────┼──────────┤
│ A1 │ block-git-push.sh        │ PreToolUse:Bash         │ 2 BLOCK  │
│ A2 │ block-git-add-all.sh     │ PreToolUse:Bash         │ 2 BLOCK  │
│ A3 │ scan-secrets.sh          │ UserPromptSubmit        │ 2 BLOCK  │
│ A4 │ block-secrets-in-code.sh │ PreToolUse:Write|Edit   │ 2 BLOCK  │
│ A5 │ block-versioned-files.sh │ PreToolUse:Write|Edit   │ 2 BLOCK  │
│ A6 │ stop-checklist.sh        │ Stop                    │ 2 RETRY  │
│ B1 │ precompact-save.sh       │ PreCompact              │ 0 INJECT │
│ B2 │ post-compact-recover.sh  │ PostCompact             │ 0 INJECT │
│ B3 │ session-start.sh         │ SessionStart            │ 0 INJECT │
│ C1 │ post-bash-failure.sh     │ PostToolUseFailure:Bash │ 0 GUIDE  │
│ C2 │ task-completed-verify.sh │ TaskCompleted           │ 0 WARN   │
│ D1 │ session-end-digest.sh    │ SessionEnd              │ 0 WRITE  │
│ D2 │ auto-format.sh           │ PostToolUse:Write|Edit  │ 0 MUTATE │
└────┴──────────────────────────┴─────────────────────────┴──────────┘

BLOCK hooks (exit 2):    6  (anti-push, anti-add-all, anti-secrets x2,
                              anti-versioning, anti-uncommitted-stop)
INJECT hooks (exit 0):   3  (precompact, postcompact, session-start)
ADVISORY hooks:          2  (post-bash-failure, task-completed-verify)
WORKFLOW hooks:          2  (session-end-digest, auto-format)
```

**6 of 13 are HARD BLOCKS.** The remainder are advisory/integration. This is a healthy ratio — too many BLOCK hooks creates permission fatigue; too few means real failures slip through.

## The Enforcement Hierarchy

```
STRUCTURAL ENFORCEMENT    ← Hooks that exit 2 — physically impossible to violate
   ↑ most reliable
AUTOMATED CHECKS          ← Hooks that exit 1 — warn, but allow
   ↑
CHECKLISTS                ← Boot/wrap rituals followed every time
   ↑
TEXT RULES                ← Written guidelines (high violation rate ~86%)
   ↑ least reliable
VERBAL PROMISES           ← "I'll remember to..." (~0% enforcement)
```

For anything that genuinely matters, use the highest level possible. A `exit 2` hook is worth ten paragraphs of well-meaning rules.

## Testing Discipline (Often Missing)

Most operator hook collections lack automated tests. This is the biggest gap in the typical hook discipline.

**Minimal hook test pattern:**

```bash
# tests/hooks/block-git-push.test.sh
INPUT='{"tool_input":{"command":"git push origin main"}}'
echo "$INPUT" | bash ../../hooks/block-git-push.sh
ACTUAL=$?
[ "$ACTUAL" -eq 2 ] && echo "PASS" || echo "FAIL: expected 2, got $ACTUAL"
```

Adding a hook = adding a test. Without tests, hook regex gaps slip through silently until a real failure hits.

---

# Part 5: The Skill Vocabulary

Skills are user-invocable rituals. Operator types `/<name>` and Claude follows the skill's protocol. They are the *workflow vocabulary* — the verbs that drive the session lifecycle.

A mature operator skill set typically has 3-7 skills covering the full session lifecycle.

## The Five Canonical Skills

```
┌────────────┬─────────────────────┬───────────────────────────────────┐
│ SKILL      │ ANSWERS THE Q       │ WHEN TO INVOKE                    │
├────────────┼─────────────────────┼───────────────────────────────────┤
│ /boot      │ "Where are we?"     │ First message of new session      │
│ /wrap      │ "What just happened?"│ End of session, before /stop     │
│ /status    │ "Current state?"    │ Mid-day check-in (read-only)      │
│ /research  │ "What do I learn?"  │ New domain investigation          │
│ /audit     │ "What could break?" │ Pre-deploy, pre-PR quality gate   │
└────────────┴─────────────────────┴───────────────────────────────────┘
```

## Skill Frontmatter Format

```markdown
---
name: skill-name
description: One-line summary
argument-hint: "[optional argument prompt]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - Agent
  - WebSearch
  - WebFetch
---

# Skill Name

Optional inline bash:
!echo "Project: $(basename $(pwd))"

Execute in order:

1. Step one
2. Step two
3. Step three

Rules:
- Constraint A
- Constraint B
```

The `allowed-tools` field scopes what the skill can do. `argument-hint` helps the operator (and Claude) understand what to pass.

The `!command` syntax injects bash output as context at the top of the skill — useful for orientation.

## Skill 1: /boot — Session Start Ritual

```markdown
---
name: boot
description: Full project boot — load context, verify state, present dashboard
allowed-tools: [Read, Glob, Grep, Bash, Agent, WebFetch]
---

# Boot Protocol

!echo "=== BOOT CONTEXT ===" && echo "CWD: $(pwd)" && echo "Project: $(basename $(pwd))" && git rev-parse --is-inside-work-tree >/dev/null 2>&1 && echo "Git: $(git branch --show-current) | $(git log --oneline -1) | $(git status --porcelain 2>/dev/null | wc -l) uncommitted" || echo "Git: not a repo"

Execute in order:

1. **Read SESSION-DIGEST.md** — understand what was last done
2. **Read memory/MEMORY.md** — understand operational state
3. **Read all memory/ files** — load full context
4. **Check project health:**
   - Git status (uncommitted changes?)
   - Any running services (servers, integrations?)
   - Test suite status (last run? passing?)
5. **Reconcile stale data** — verify numbers in MEMORY.md match reality
6. **Present dashboard** in ASCII box format:
   - Current state
   - What was last done
   - What needs doing next (from MEMORY.md NEXT section)
   - Any alerts or issues
7. **Act on highest priority item** unless told otherwise
```

## Skill 2: /wrap — Session End Ritual

```markdown
---
name: wrap
description: Session wrap-up — commit, update memory, write digest
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep]
---

# Wrap-Up Protocol

Execute ALL steps in order. Do not skip any.

1. **Stage and commit** all meaningful changes (specific files, not git add -A)
2. **Update memory/MEMORY.md** with:
   - Current state (exact numbers, not approximations)
   - NEXT priorities (ordered)
   - Any new lessons or findings
3. **Write SESSION-DIGEST.md** with:
   - What got done this session
   - Current state (exact)
   - Key decisions made
   - How to resume next session
4. **Spot-check 3 claims** from the digest — verify each is accurate
5. **Git commit** the memory and digest updates
6. Report: "Session wrapped. N commits. Ready for next boot."
```

**This is the *real* digest writer.** The auto SessionEnd hook only produces a stub. The `/wrap` flow produces the substantive handoff.

## Skill 3: /status — Read-Only Dashboard

A read-only counterpart to /boot. Same orientation, no actions taken. Useful for mid-day check-ins where you want to see state without triggering work.

## Skill 4: /research — Parallel Research Swarm

```markdown
---
name: research
description: Deep research swarm — 3-5 parallel agents on any topic
argument-hint: "[topic to research]"
allowed-tools: [Agent, WebSearch, WebFetch, Read, Write, Glob, Grep]
---

# Deep Research Protocol

Topic: $ARGUMENTS

Execute:

1. **Parse the topic** — understand what's needed
2. **Launch 3-5 parallel research agents** (subagent_type=researcher):
   - Agent 1: Market/industry analysis
   - Agent 2: Technical feasibility
   - Agent 3: Competitor landscape
   - Agent 4: Pricing/business model (if relevant)
   - Agent 5: Risk/regulatory (if relevant)
3. **Each agent must:** use WebSearch + WebFetch, cite sources, structured report
4. **Synthesize findings** — combine all agent results
5. **Present:**
   - Key findings (3-5 bullets)
   - Numbers with sources
   - Clear recommendation
6. **Save research** to `research/{topic-slug}.md`

Rules:
- Every stat needs a source
- "I think" is NOT a finding
- 400+ lines minimum across all agents
- Cross-verify between agents
```

## Skill 5: /audit — Multi-Agent Adversarial Quality Gate

A skill that launches 8-10 parallel specialized agents (security, performance, types, architecture, dependencies, compliance, accessibility, data integrity) + an adversarial verifier + (when applicable) a runtime test.

Each Phase 1 agent reports severity (P0/P1/P2), file:line citations, evidence, and exploit path. Phase 2 verifier re-reads files and distinguishes theoretical vs exploitable findings, targeting ≥30% false-positive reduction. Phase 3 runtime-tests applicable claims (don't trust static analysis for runtime behavior). Phase 4 synthesizes into a markdown report with P0/P1/P2 counts, false positives caught, blind spots, and coverage gaps.

**Mandatory agent rules** that emerge from operating experience:
- For every cited file path: confirm it exists via Glob/Read FIRST. Quote only lines actually read.
- For numeric/legal constants: grep entire repo for duplicate encodings. The worst findings often live in sibling files that were not in the diff.

**Done criteria** must include false-positive count (proof verifier ran) and coverage gaps (honest about what wasn't audited).

## The Cook/Suggest/Status/Wrap Vocabulary

Beyond named skills, mature operators develop a verb vocabulary that maps to behavior modes:

| Verb | Mode | Operator intent |
|------|------|-----------------|
| "cook" / "go" / "do it" | Full autonomy | Execute without asking |
| "suggest" / "think" / "plan" | Plan only | Present options, wait for direction |
| "status" | Read-only dashboard | Orient without triggering work |
| "wrap" | Session end | Commit, update memory, write digest |

This vocabulary makes the operator-Claude interaction efficient. "Cook" replaces "could you please...?" The verbs become shortcuts for full behavior modes.

## Built-In Skills vs Custom Skills

Claude Code ships with built-in skills that operators may not realize exist. Before building custom, check:

- `update-config` — Configure settings.json
- `keybindings-help` — Customize keyboard shortcuts
- `simplify` — Code simplification review
- `fewer-permission-prompts` — Allowlist common operations
- `loop` — Run recurring commands
- `claude-api` — Anthropic SDK help
- `init` — Initialize CLAUDE.md
- `review` — Review a PR
- `security-review` — Security audit pending changes

Custom skills should fill *gaps* in built-ins, not duplicate them. If `/review` already exists as a built-in, your custom `/audit` should do something the built-in doesn't.

---

# Part 6: The Custom Agents — Cost-Tiered Subagents

Custom subagents are specialized personas with their own tool access, model selection, and system prompts. A mature operator setup typically has 2-5 custom agents, deliberately tiered by cost.

## The Cost-Tiering Principle

Three model tiers, three use cases:

```
TIER 1: HAIKU (cheapest)            TIER 2: SONNET (mid)              TIER 3: OPUS (most expensive)
─────────────────                   ──────────────────                ──────────────────────────────

Use case:                           Use case:                         Use case:
Read-only recon                     Focused analysis                  Heavy reasoning, main thread

Examples:                           Examples:                          Examples:
- "Where is X defined?"             - "Verify this fix works"         - Main operator session
- "Grep all references to Y"        - "Research domain Z"             - /ultrareview synthesis
- "Trace call chain for Z"          - "Audit module A"                - Architectural decisions

Cost saving vs Opus:                Cost saving vs Opus:              Cost (relative):
~80-90%                             ~60%                              baseline (1x)

Reasoning depth:                    Reasoning depth:                  Reasoning depth:
Limited                             Substantial                       Maximum

Typical max-turns:                  Typical max-turns:                Typical max-turns:
10-15                               30-50                             unbounded
```

## Agent 1: explorer (Haiku)

```markdown
---
name: explorer
description: Fast read-only codebase exploration
model: haiku
disallowed-tools: [Agent, Edit, Write, NotebookEdit]
---

You are a fast codebase explorer. Your job is to find information quickly.

- Search for files by pattern (Glob)
- Search for content by regex (Grep)
- Read files to understand code
- NEVER modify anything
- Report findings concisely with file paths and line numbers
- When asked about architecture, trace the full call chain
- When asked about a bug, find all related code paths
```

**Use case:** "Where is X defined?" "What files reference Y?" Lookups, not analysis.

**Cost optimization:** Haiku is cheapest. Read-only recon doesn't need Opus reasoning. Saves money on the majority of exploratory queries.

## Agent 2: verifier (Sonnet, Background)

```markdown
---
name: verifier
description: Adversarial verification — tries to break implementations
model: sonnet
background: true
disallowed-tools: [Agent, Edit, Write, NotebookEdit]
max-turns: 30
---

You are an adversarial verifier. Your job is to BREAK things, not confirm they work.

1. Read the code that was changed
2. Think of edge cases, race conditions, missing validations
3. Run tests if they exist
4. Try unexpected inputs mentally
5. Check for: security issues, error handling gaps, missing null checks, hardcoded values
6. Check that numbers/claims in docs match actual code

Output format:
- VERDICT: PASS / FAIL / PARTIAL
- Issues found (if any), with file:line references
- Severity: CRITICAL / HIGH / MEDIUM / LOW
```

**Background mode** means it can run while operator continues main work. Result returned when ready.

**Use case:** Phase 2 of /audit skill. Also standalone for "verify this fix actually works."

## Agent 3: researcher (Sonnet)

```markdown
---
name: researcher
description: Deep research agent — web + code + analysis
model: sonnet
allowed-tools: [WebSearch, WebFetch, Read, Glob, Grep, Bash]
max-turns: 50
---

You are a deep research agent. Your job is thorough investigation.

1. Use WebSearch to find current information
2. Use WebFetch to read full articles/documentation
3. Cross-reference multiple sources
4. CITE every claim with a source
5. Distinguish fact from opinion
6. Report "NOT FOUND" rather than guessing

Output format:
- Key findings (numbered)
- Sources (linked)
- Confidence level per finding (HIGH/MEDIUM/LOW)
- Gaps in research (what couldn't be verified)
```

**Use case:** Invoked by /research skill in parallel swarms of 3-5 agents. Each takes one angle of the topic. Operator synthesizes.

## When to Build Custom vs Use Built-In

Claude Code ships with several built-in agent types:

| Built-in | Use when |
|----------|----------|
| `claude` | Catch-all (default) |
| `claude-code-guide` | Questions about Claude Code itself / API / SDK |
| `Explore` | Narrow targeted search |
| `general-purpose` | Multi-step catch-all |
| `Plan` | Architecture planning |
| `statusline-setup` | Configure status line |

**Build custom when:**
- You repeatedly need the same specialized behavior (e.g., adversarial verification)
- You want a different model tier than the default
- You want a narrow tool allowlist (e.g., read-only)
- You want a system prompt that frames the task specifically

**Use built-in when:**
- It already does what you need
- You don't need cost tiering
- You don't need a specific tool allowlist

The cost model:
- Main operator session: Opus high (via `effortLevel: high`)
- Subagents: Sonnet (via `CLAUDE_CODE_SUBAGENT_MODEL=sonnet`) — 60% cheaper
- explorer agent: Haiku — cheapest, for read-only recon

This is a deliberate cost-tiered architecture. Heavy thinking on the main thread; cheap parallel work in subagents; cheapest model for recon.

---

# Part 7: MCP Server Roster

MCP (Model Context Protocol) servers extend Claude with capabilities beyond what Claude Code natively has. A mature setup typically has 5-10 MCP server families authorized.

## Authorization Pattern

MCP tools are authorized via wildcards in the permissions allow-list:

```json
{
  "permissions": {
    "allow": [
      "mcp__<server-name>__*"
    ]
  }
}
```

This authorizes ALL tools from a given server. Alternative: explicit per-tool allow (`mcp__<server>__<tool>`) for tighter scoping.

## Canonical MCP Categories

```
┌───────────────────────────────────┬───────────────────────────────────┐
│ CATEGORY                          │ TYPICAL SERVERS                   │
├───────────────────────────────────┼───────────────────────────────────┤
│ Web / Browser Automation          │ playwright, firecrawl             │
│   (page snapshots, scraping)      │                                   │
├───────────────────────────────────┼───────────────────────────────────┤
│ Productivity                      │ Gmail, Calendar, Notion,          │
│   (email, calendar, knowledge)    │ Google Drive                      │
├───────────────────────────────────┼───────────────────────────────────┤
│ Reasoning                         │ sequential-thinking               │
│   (structured chain-of-thought)   │                                   │
├───────────────────────────────────┼───────────────────────────────────┤
│ Documentation Lookup              │ context7                          │
│   (library docs, API references)  │                                   │
├───────────────────────────────────┼───────────────────────────────────┤
│ UI Generation                     │ magic / 21st.dev                  │
│   (component generation, mockups) │                                   │
├───────────────────────────────────┼───────────────────────────────────┤
│ Infrastructure                    │ Cloud provider MCPs               │
│   (servers, networking, configs)  │ (often split: config / net / srv) │
├───────────────────────────────────┼───────────────────────────────────┤
│ Developer Tools                   │ IDE bridges                       │
│   (diagnostics, code execution)   │                                   │
├───────────────────────────────────┼───────────────────────────────────┤
│ Reverse Engineering / Security    │ Ghidra MCP                        │
│   (binary analysis)               │                                   │
└───────────────────────────────────┴───────────────────────────────────┘
```

## Authorization Granularity Patterns

```
PATTERN A: Wildcard Trust          PATTERN B: Tool-Specific          PATTERN C: Per-Server Split
─────────────────────              ──────────────────────            ───────────────────────────

mcp__server__*                     mcp__server__safe_tool1            mcp__server-config__*  (read)
                                   mcp__server__safe_tool2            mcp__server-data__*    (read)
Authorizes everything                                                  mcp__server-mutate__*  (deny)
from a server                      Explicit per-tool authorization

Pros:                              Pros:                              Pros:
- Simple                           - Tight scope                      - Read-default, write-explicit
- Easy to manage                   - Audit-friendly                   - Layered safety

Cons:                              Cons:                              Cons:
- Trusts whole server              - Verbose                          - Requires server split
- Future tools auto-allowed        - Maintenance burden               - Not all servers split

Use for:                           Use for:                           Use for:
- Trusted servers you know         - Untrusted/unknown servers        - High-stakes integrations
- Productivity tools               - Specific tool needs              - Infrastructure (cloud,
                                                                       databases, prod systems)
```

For infrastructure MCPs (cloud providers, databases), Pattern C is often correct — split the server installation by capability (read vs write), allow read by default, gate write behind explicit authorization.

## Build-vs-Borrow Decision

A mature operator setup typically consumes existing MCPs but rarely builds custom ones. Why?

**MCPs are infrastructure.** They translate between Claude and external services. The translation logic is similar across operators. There's no value-add in reinventing it.

**Value-add lives elsewhere.** The operator's value-add is in skills (workflows), hooks (enforcement), memory (continuity), and CLAUDE.md (behavioral rules). Not in MCP servers.

**Exception:** if you have an INTERNAL service that no one else uses (proprietary API, custom database), a custom MCP is warranted.

## Setup Gotchas

**Windows-specific:** npx-based MCP servers must be wrapped with `cmd /c` to avoid `/doctor` warnings:

```json
{
  "mcpServers": {
    "<server>": {
      "command": "cmd",
      "args": ["/c", "npx", "-y", "<package>"]
    }
  }
}
```

**Authentication gotchas:** Google Drive and similar OAuth-based MCPs require an authentication flow. Tools may appear deferred until auth completes.

**Plugin-vs-MCP confusion:** Some integrations exist as both plugins (e.g., `discord`, `telegram`, `imessage` external plugins) AND MCPs. Plugin = bundled UX. MCP = raw tool access. Pick one path; using both creates routing confusion.

---

# Part 8: The Plugin Decision

The Claude Code plugin marketplace ships with dozens of plugins covering language servers, code review, hooks, skills, MCPs, and more. A mature operator typically enables 0-3 plugins out of 30+ available.

This isn't laziness or NIH syndrome — it's a deliberate decision.

## Three Approaches to Claude Code Extension

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  APPROACH 1: ALL PLUGINS                                            │
│  ───────────────────────                                            │
│  Install everything from marketplace. Configure heavily.            │
│  Custom work: minimal.                                              │
│                                                                     │
│  Pros:                                                              │
│  - Fast bootstrap                                                   │
│  - Maintained by others                                             │
│  - Community-tested                                                 │
│                                                                     │
│  Cons:                                                              │
│  - Dependency on plugin maintainers' update cadence                 │
│  - Less control over edge cases                                     │
│  - Multiple plugins may conflict                                    │
│  - Hard to debug when something breaks                              │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  APPROACH 2: HYBRID                                                 │
│  ──────────────────                                                 │
│  Install plugins where they fit. Build custom for everything else.  │
│  Custom work: moderate.                                             │
│                                                                     │
│  Pros:                                                              │
│  - Plugins for infrastructure (LSPs, IDE bridges)                   │
│  - Custom for workflow-specific behavior                            │
│  - Balanced trade-off                                               │
│                                                                     │
│  Cons:                                                              │
│  - Two sources of truth (plugin + custom)                           │
│  - Risk of duplication                                              │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  APPROACH 3: MOSTLY CUSTOM                                          │
│  ────────────────────────                                           │
│  Minimal plugins (often just LSPs). Maximum custom.                 │
│  Custom work: maximum.                                              │
│                                                                     │
│  Pros:                                                              │
│  - Full control over edge cases                                     │
│  - Adversity-tested in own production                               │
│  - No dependency on external maintainers                            │
│  - Customized to operator's specific failure modes                  │
│                                                                     │
│  Cons:                                                              │
│  - Substantial upfront work                                         │
│  - Bus factor of 1 (operator-tuned)                                 │
│  - Reinvention risk (custom-built before platform shipped feature)  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Why Mature Operators Tend Toward Approach 3

**Each plugin = a dependency.** Plugins are maintained by others (or by no one). When the operator's needs evolve, the plugin may or may not evolve with them. When the platform evolves, the plugin may or may not stay compatible.

**Most plugin functionality is replicable.** Code review plugin → custom /audit skill. Commit-commands plugin → discipline + hooks. CLAUDE.md management plugin → 3-tier hierarchy. Hookify → just write the hook.

**Custom = full control over edge cases.** When the operator's secret-scanning regex needs to also catch the new credential format that shipped last month, with custom you edit one file. With a plugin you wait (or fork).

**Custom = adversity-tested.** A hook that was written in response to a specific failure mode is calibrated to that failure mode. A plugin is calibrated to its author's failure modes.

## When Plugins Are Correct

There are clear cases where plugins win:

**Language servers (LSPs).** Rolling your own language server is not realistic. Use the plugin: `rust-analyzer-lsp`, `pyright-lsp`, `typescript-lsp`, `clangd-lsp`, etc.

**Highly specialized integrations.** Discord bot bridge, iMessage reader, Telegram bot — these have domain-specific complexity. Plugin authors have done the integration work; consuming is correct.

**Bootstrap phase.** When you're new and don't know what you need, plugins help you explore. Once you know your workflow, replace plugins with custom equivalents.

## The Cache Discipline Note

When you browse the marketplace, plugins get cached locally even if you don't enable them. This is intentional (faster install when you do decide to enable). But it creates a discipline question:

- 32 plugins cached, 1 enabled = signal of healthy exploration
- 32 plugins cached, 30 enabled = signal of unhealthy bloat
- 32 plugins cached, 0 enabled = signal that you might be over-rejecting

Periodic prune is healthy. Disabled plugins still take disk and clutter `/plugins` browsing.

---

# Part 9: Memory Namespace Pattern

The Claude Code auto-memory system creates one memory namespace per working directory at `~/.claude/projects/<encoded-path>/`. A mature operator typically accumulates 5-15 namespaces over time.

For atom anatomy, the 4 atom types, the 200-line index cap, lifecycle protocols, and failure modes, see the **[memory-kit]** companion document. This section focuses on namespace-level patterns.

## The Archetype Distribution

A mature setup's namespaces typically follow a "fat head, long tail" pattern:

```
┌───────────────────────────┬─────┬──────────┬─────────────────────────┐
│ NAMESPACE                 │ #   │ ACTIVITY │ CHARACTERIZATION        │
│                           │ atms│ TIER     │                         │
├───────────────────────────┼─────┼──────────┼─────────────────────────┤
│ War room (strategy hub)   │ 70+ │ ACTIVE   │ Cross-project intel,    │
│                           │     │          │ daily driver            │
├───────────────────────────┼─────┼──────────┼─────────────────────────┤
│ Project A (primary work)  │ 40+ │ ACTIVE   │ Main project, substantial│
│                           │     │          │ ongoing memory          │
├───────────────────────────┼─────┼──────────┼─────────────────────────┤
│ Project B (recent work)   │ ~10 │ SEMI-    │ Recent activity, modest │
│                           │     │ ACTIVE   │ atom accumulation       │
├───────────────────────────┼─────┼──────────┼─────────────────────────┤
│ Project C (last quarter)  │ ~5  │ STALE    │ Last touched 60-90 days │
│                           │     │          │ ago, candidate to archive│
├───────────────────────────┼─────┼──────────┼─────────────────────────┤
│ Project D (one-shot)      │ 0   │ SHELL    │ Namespace exists but    │
│                           │     │          │ no atoms ever captured  │
└───────────────────────────┴─────┴──────────┴─────────────────────────┘
```

**The pattern is healthy when:** 70-80% of total atoms consolidate in 1-2 namespaces (the war room + primary project).

**The pattern is unhealthy when:** atoms spread evenly across many namespaces (lack of focus) OR 90%+ in one namespace (no cross-project pattern emerging).

## The Tier Model

```
TIER A — DAILY DRIVER
  Active in last 7 days, 30+ atoms, MEMORY.md regularly updated
  → Keep operational hygiene high

TIER B — SEMI-ACTIVE
  Active in last 30 days, 5-30 atoms
  → Periodic prune (monthly)

TIER C — STALE
  Last touched 30-90 days ago
  → Archive candidate at 90-day mark

TIER D — DORMANT
  Last touched 90+ days ago
  → Archive: move to ~/.claude/projects/_archive/<slug>/

TIER E — SHELL
  Namespace exists, 0 atoms accumulated
  → Delete: was an exploratory session that never produced state
```

## The War Room Pattern (Cross-Project)

For operators running 3+ active projects simultaneously, a war room namespace handles cross-cutting concerns. See [memory-kit Part 10] for the full pattern. Summary:

- **War room** holds atoms applicable across projects: user identity, behavioral preferences, infrastructure references.
- **Per-project namespaces** hold project-specific atoms: phase status, blockers, team-specific decisions.
- **Updates flow ONE direction:** war room is canonical for cross-cutting. Project work doesn't modify war room atoms.

Single-project operators don't need this pattern — it adds friction without benefit. War room is for multi-project consolidation.

## Aggregation Policy

When a namespace approaches the 200-line MEMORY.md index cap, you face an aggregation decision: keep many small atoms, or merge into fewer larger atoms?

**Rule of thumb:** when 5+ atoms exist on the same topic, consider aggregation.

```
BEFORE aggregation:                   AFTER aggregation:
  app_pricing_v1.md                    app_pricing_intel.md
  app_pricing_v2.md                    (consolidates all 6 prior atoms,
  app_pricing_competitor_a.md           historical observations as sub-sections,
  app_pricing_competitor_b.md           current state at top)
  app_pricing_personas.md
  app_pricing_decision_2026q1.md
```

Aggregation reduces index entries (frees cap room) and consolidates fragmented intel. Trade-off: larger atoms are slightly less surgical to update.

## Retirement Policy

When does a namespace stop earning its keep?

**Signals for retirement (archive, don't delete):**
- Last MEMORY.md edit >90 days ago
- Project has been completed/shipped/abandoned
- Atoms are all status snapshots that have decayed
- Memory references services/people/contexts no longer relevant

**Archive process:**
```bash
mv ~/.claude/projects/<dead-slug>/ ~/.claude/projects/_archive/<dead-slug>/
```

**Never delete** — archive. Recovery from accidental deletion is harder than ignoring an archive directory.

## Memory and Backup Interaction

Memory namespaces are part of `~/.claude/`. Backup pipeline (Part 10) captures everything. But the curated memory sync (Channel B in Part 10) selectively syncs ONLY atoms relevant to the off-site operator. This prevents leaking personal feedback atoms or interview-specific notes to remote systems.

---

# Part 10: The Backup Pipeline

A mature operator setup has off-site backup. Local disk fails. Operating systems get reinstalled. Memory atoms are high-value, low-volume — they belong in remote storage.

The canonical pattern: **two-channel off-site sync.**

## Channel A: Full State Backup

```bash
#!/bin/bash
# scripts/backup-state.sh
# Trigger: SessionEnd hook
# Destination: remote:/backup/<your-config>/dotclaude-{YYYY-MM-DD-HHMM}.tar.gz
# Retention: rolling N-day window (typical: 14)

DEST="/backup/dotclaude"
DATE=$(date +%Y-%m-%d-%H%M)
TARGET_NAME="dotclaude-${DATE}.tar.gz"
MAX_BACKUPS=14
LOG="$HOME/.claude/backup-state.log"
LOCK="$HOME/.claude/backup-state.lock"

# Lockfile prevents concurrent runs
if [ -f "$LOCK" ]; then
    LOCK_AGE=$(($(date +%s) - $(stat -c%Y "$LOCK" 2>/dev/null || echo 0)))
    [ "$LOCK_AGE" -lt 1800 ] && exit 0
fi

run_backup() {
    touch "$LOCK"
    trap "rm -f $LOCK" EXIT

    {
        echo "[$(date -Iseconds)] === Backup starting ==="

        # SSH connect timeout
        if ! ssh -o ConnectTimeout=5 -o BatchMode=yes <remote-host> "true" 2>/dev/null; then
            echo "[$(date -Iseconds)] ABORT: SSH failed"
            return 1
        fi

        ssh <remote-host> "mkdir -p $DEST" 2>/dev/null

        # Tar pipe — no intermediate file
        if (cd "$HOME" && tar -czf - .claude 2>/dev/null) | ssh <remote-host> "cat > $DEST/$TARGET_NAME"; then
            REMOTE_SIZE=$(ssh <remote-host> "stat -c%s $DEST/$TARGET_NAME 2>/dev/null" || echo 0)
            echo "[$(date -Iseconds)] SUCCESS: $TARGET_NAME ($((REMOTE_SIZE / 1024 / 1024)) MB)"
        else
            echo "[$(date -Iseconds)] FAIL: tar/upload error"
            return 1
        fi

        # Retention: prune oldest
        DELETED=$(ssh <remote-host> "cd $DEST && ls -t dotclaude-*.tar.gz | tail -n +$((MAX_BACKUPS+1)) | xargs -r rm -fv | wc -l")
        [ "$DELETED" -gt 0 ] && echo "[$(date -Iseconds)] Retention: pruned $DELETED old backup(s)"

        echo "[$(date -Iseconds)] === Backup done ==="
    } >> "$LOG" 2>&1
}

run_backup &
disown
exit 0
```

**Key design choices:**

- **Tar pipe (no intermediate file):** memory-efficient, atomic-ish (no partial file on disk)
- **SSH ConnectTimeout=5:** fail fast when remote unreachable
- **Lockfile with stale timeout:** prevents concurrent runs, stale lock cleared after 30 minutes
- **Background + disown:** doesn't block SessionEnd (which has 1.5s timeout)
- **Rolling retention:** never grow unbounded
- **Log everything:** when backup fails, you want to know why

## Channel B: Curated Memory Sync

```bash
#!/bin/bash
# scripts/sync-memory-curated.sh
# Trigger: SessionEnd hook
# Destination: remote:/path/to/memory/_from_local/
# Pattern: Curated allowlist of specific atoms

SRC="$HOME/.claude/projects/<your-war-room-slug>/memory"
LOG="$HOME/.claude/sync-memory.log"
LOCK="$HOME/.claude/sync-memory.lock"

# Curated allowlist — ONLY atoms relevant to remote operator
FILES=(
  reference_<service>.md
  reference_<infrastructure>.md
  lesson_<category>.md
  # ... explicit list of files to sync, NOT everything
)

# Lockfile (3-min stale)
if [ -f "$LOCK" ]; then
  age=$(($(date +%s) - $(stat -c%Y "$LOCK" 2>/dev/null || echo 0)))
  [ "$age" -lt 180 ] && exit 0
fi
echo $$ > "$LOCK"
trap 'rm -f "$LOCK"' EXIT

(
  # Build list of files that exist
  existing=()
  for f in "${FILES[@]}"; do
    [ -f "$SRC/$f" ] && existing+=("$f")
  done
  count=${#existing[@]}

  [ "$count" -eq 0 ] && exit 0

  # Tar and pipe
  ( cd "$SRC" && tar -cz "${existing[@]}" ) 2>/dev/null | \
    ssh -o ConnectTimeout=10 -o BatchMode=yes <remote-host> \
      "mkdir -p /path/to/memory/_from_local && cd /path/to/memory/_from_local && tar -xz && date '+%Y-%m-%dT%H:%M:%S synced ${count} files' >> SYNC-LOG.md" \
      2>>"$LOG"
) &
disown
exit 0
```

**Critical:** the FILES allowlist is HARD-CODED. Not glob-based. This prevents accidental sync of personal feedback atoms, interview-specific notes, or any atom you don't explicitly want on the remote.

**Why two channels?**

```
Channel A — disaster recovery       Channel B — operational sync
─────────────────────────           ────────────────────────────

Backs up EVERYTHING                  Syncs CURATED subset
14-day retention                     Always-fresh (overwrites)
Used when: laptop dies               Used when: remote needs context
Recovery: untar onto fresh           Recovery: not a backup —
   ~/.claude/                          consumed by remote operator
```

## Honest Gaps in This Pattern

**Gap 1: Unidirectional.** Channel B is laptop → remote. Changes made on the remote (e.g., SSH session on the remote operator) don't flow back. Over time, memory bifurcates.

**Mitigation options:**
- Define explicit ownership ("remote owns operations memory, laptop owns project memory")
- Add a Channel C: remote → laptop sync of designated atoms
- Use rclone or similar with proper conflict detection

**Gap 2: Restore drill not run.** Backups are a hypothesis until you restore from one and verify it works. Quarterly restore drill recommended:
- Pull latest tarball
- Untar to a scratch directory
- Verify integrity: file count, key files present, no corruption
- Test loading: would a fresh Claude Code session boot correctly from this state?

**Gap 3: No git versioning.** Backup captures the FILES at a point in time. It doesn't capture the HISTORY of changes. Recommendation: put `~/.claude/` itself under git. Push to a private remote. Then you have both file-state (tarballs) AND change-history (git log).

```bash
cd ~/.claude
git init
git remote add origin git@github.com:<your-username>/dotclaude-private.git
git add .
git commit -m "Initial commit"
git push -u origin main
```

This is a 30-minute investment that catastrophically improves recovery options.

## The Pattern Summary

```
LOCAL LAPTOP                        REMOTE SERVER
──────────                          ─────────────

~/.claude/                          /backup/dotclaude/
  │                                   ├── dotclaude-DATE-1.tar.gz
  ├── SessionEnd fires:                ├── dotclaude-DATE-2.tar.gz
  │   1. session-end-digest.sh          ├── ... (14 total)
  │   2. backup-state.sh ─tar─►        └── (older auto-pruned)
  │   3. sync-memory-curated.sh
  │                                   /path/to/memory/_from_local/
  └── Logs:                             ├── reference_<service>.md
      backup-state.log                  ├── lesson_<category>.md
      sync-memory.log                   ├── ... (curated subset)
                                        └── SYNC-LOG.md (append on each sync)

Resilience:
  · Both channels backgrounded
  · Lockfile prevents concurrent runs
  · SSH connect timeouts (5s / 10s)
  · SessionEnd blocks for ≤1.5s
  · Both fail gracefully if remote offline
```

---

# Part 11: Provenance Map — Custom vs Borrowed vs Native

Where does every piece of the operator stack come from? Three categories.

## CUSTOM (Operator-Built)

```
┌─────────────────────────────────────────────────────────────────────┐
│  ALL HOOKS (typically 8-15)                                         │
│  - Every hook in ~/.claude/hooks/ is operator-written               │
│  - Reflects operator's specific failure modes                       │
│  - Updates calibrated to operator's evolving needs                  │
│                                                                     │
│  ALL SKILLS (typically 3-7)                                         │
│  - boot, wrap, status, research, audit — all custom                 │
│  - Reflect operator's workflow vocabulary                           │
│  - Pattern influences from public repos, but code is own            │
│                                                                     │
│  ALL CUSTOM AGENTS (typically 2-5)                                  │
│  - Cost-tiered (haiku / sonnet / sonnet) intentionally              │
│  - System prompts calibrated to specific tasks                      │
│                                                                     │
│  STATUSLINE + BACKUP SCRIPTS                                        │
│  - statusline-command.sh — custom render                            │
│  - backup-state.sh + sync-memory-curated.sh — custom pipeline       │
│                                                                     │
│  CLAUDE.md FILES (all 3 tiers)                                      │
│  - Global behavioral rules — clean-room recreation OR operator      │
│    interpretation of platform spec                                  │
│  - Machine identity — fully custom                                  │
│  - Project specifics — fully custom                                 │
│                                                                     │
│  ALL MEMORY ATOMS                                                   │
│  - Every atom written collaboratively in-session                    │
│  - Format follows platform spec (4 types, frontmatter)              │
│  - Content is operator-specific                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Typical share of stack:** ~80% custom.

## BORROWED (Imported with Attribution)

```
┌─────────────────────────────────────────────────────────────────────┐
│  PATTERNS FROM PUBLIC REPOS                                         │
│  - Plan-first workflow patterns (from public skill collections)     │
│  - Hook architecture concepts (from public hook collections)        │
│  - Eval framework patterns (from research repo benchmarks)          │
│  - Cherry-picked structures from forked starter projects            │
│                                                                     │
│  ADAPTATION DISCIPLINE                                              │
│  - When forking: preserve LICENSE files                             │
│  - When taking concepts: write own code (don't copy)                │
│  - When taking code: per-file attribution headers                   │
│  - Audit before clone: confirm permissive license                   │
│                                                                     │
│  WHAT IS NOT BORROWED                                               │
│  - Full plugin packages with many agents/skills (scope discipline)  │
│  - Code without verifiable license                                  │
│  - Patterns whose context-of-use is unclear                         │
└─────────────────────────────────────────────────────────────────────┘
```

**Typical share of stack:** ~10% borrowed.

## NATIVE (Comes with Claude Code)

```
┌─────────────────────────────────────────────────────────────────────┐
│  BUILT-IN AGENTS                                                    │
│  - claude (default catch-all)                                       │
│  - claude-code-guide (Claude Code / SDK / API questions)            │
│  - Explore (fast read-only search)                                  │
│  - general-purpose (catch-all multi-step)                           │
│  - Plan (architecture / planning agent)                             │
│  - statusline-setup (configure status line)                         │
│                                                                     │
│  BUILT-IN SKILLS                                                    │
│  - update-config                                                    │
│  - keybindings-help                                                 │
│  - simplify                                                         │
│  - fewer-permission-prompts                                         │
│  - loop                                                             │
│  - claude-api                                                       │
│  - init                                                             │
│  - review                                                           │
│  - security-review                                                  │
│                                                                     │
│  BUILT-IN INFRASTRUCTURE                                            │
│  - Plugin marketplace (claude-plugins-official)                     │
│  - LSP plugins (rust-analyzer, pyright, typescript, etc.)           │
│  - Auto-memory system (4-type spec, MEMORY.md index)                │
│  - Hook system (events, exit codes)                                 │
│  - MCP protocol                                                     │
│                                                                     │
│  PLATFORM EVOLUTION                                                 │
│  - Quarterly: new agents, skills, hook events, MCP integrations     │
│  - Some shipped features may replace operator's custom work         │
│  - Important: re-evaluate custom vs native quarterly                │
└─────────────────────────────────────────────────────────────────────┘
```

**Typical share of stack:** ~10% native.

## The Provenance Pie

```
┌────────────────────────────────────────────────────┐
│                                                     │
│  CUSTOM:    ████████████████░░░░  ~80%             │
│  BORROWED:  ██░░░░░░░░░░░░░░░░░░  ~10%             │
│  NATIVE:    ██░░░░░░░░░░░░░░░░░░  ~10%             │
│                                                     │
│  Mature operator stack is mostly custom, built on  │
│  the native platform, with deliberate borrowing.   │
│                                                     │
└────────────────────────────────────────────────────┘
```

## The Anti-Pattern: Drift Against Platform

When the platform ships a new feature that replaces operator's custom work, operator may not notice for months. The custom becomes a duplicate, an unnecessary maintenance burden.

**Mitigation: quarterly platform feature review.**

```
QUARTERLY CHECKLIST (15-minute review)

[ ] What's new in Claude Code since last review?
[ ] Any new built-in skills that replace my custom skills?
[ ] Any new built-in agents that replace my custom agents?
[ ] Any new hook events that simplify my hook scripts?
[ ] Any new MCP servers that replace my custom integrations?
[ ] Any policy/behavior changes in CLAUDE.md spec?
[ ] Any new env vars that simplify my settings.json?
```

After the review:
- If platform feature is strictly better than custom → migrate
- If platform feature is comparable → keep custom (don't migrate-for-the-sake-of-it)
- If platform feature is worse → keep custom, note the gap

## Why Provenance Discipline Matters

Three reasons:

1. **Intellectual honesty.** When you say "I built this," it should mean "I built this." When you say "I adapted this from X," that's also honest. Mixing the two erodes credibility.

2. **License compliance.** Borrowed code with permissive licenses (MIT, Apache) requires attribution. Borrowed code without LICENSE files should not be copied at all.

3. **Maintenance clarity.** When something breaks, knowing whether you wrote it (your problem to fix) vs borrowed (maintainer's problem, or your fork's problem) determines your debugging path.

---

# Part 12: Integration Diagram — Event by Event

How everything connects across the session lifecycle. This is the operating manual for the whole stack.

## Full Session Timeline

```
═══════════════════════════════════════════════════════════════════════════
                         SESSION TIMELINE — EVENT BY EVENT
═══════════════════════════════════════════════════════════════════════════

  T+0       SESSION START
  ─────────────────────────
              │
              ├─► Hook: session-start.sh fires
              │     · Prints boot banner (project, git state, file presence)
              │     · Output injected into Claude context as orientation
              │
              ├─► Claude reads (automatic harness loads):
              │     · ~/.claude/CLAUDE.md (global behavioral rules)
              │     · <strategy-hub>/CLAUDE.md (machine identity)
              │     · <project>/CLAUDE.md (project specifics, if present)
              │     · MEMORY.md index (first 200 lines)
              │
              └─► Operator types first prompt
                  │
                  ├─► Hook: scan-secrets.sh fires
                  │     · Blocks if API key pattern detected in prompt
                  │
                  └─► Prompt enters context

  T+...     MID-SESSION WORK
  ──────────────────────────
              │
              ├─► Operator: /<skill>
              │     · skills/<name>.md loads
              │     · Claude follows skill protocol
              │
              ├─► Claude: Bash command
              │     · Hooks fire: block-git-push.sh + block-git-add-all.sh
              │     · settings.json deny list also checks
              │     · If both pass: command runs
              │     · If command fails: post-bash-failure.sh fires
              │
              ├─► Claude: Write/Edit
              │     · Hooks fire: block-versioned-files.sh + block-secrets-in-code.sh
              │     · If both pass: write happens
              │     · After write: auto-format.sh fires (ruff/rustfmt/prettier)
              │
              ├─► Claude: Agent spawn (subagent)
              │     · Subagent gets CLAUDE_CODE_SUBAGENT_MODEL (typically sonnet)
              │     · Subagent loads agents/<name>.md system prompt
              │     · Runs in own context window
              │     · Returns result to main thread
              │
              ├─► Claude: TaskUpdate complete
              │     · Hook: task-completed-verify.sh fires
              │     · If >10 uncommitted files: warns
              │
              └─► Memory: Claude writes new atom
                  · Atom .md file → ~/.claude/projects/<slug>/memory/
                  · MEMORY.md gets new index line

  T+...     CONTEXT REACHES ~80%
  ──────────────────────────────────
              │
              ├─► Hook: precompact-save.sh fires (PreCompact event)
              │     · Snapshots: git state, MEMORY.md (50 lines),
              │                  SESSION-DIGEST.md (30 lines)
              │     · Output appended to compaction context
              │
              ├─► Claude Code auto-compacts:
              │     · Old messages summarized
              │     · Volatile state lost
              │     · Persistent state (memory atoms, files) preserved
              │
              └─► Hook: post-compact-recover.sh fires (PostCompact event)
                    · Injects: project name, git state, CLAUDE.md head,
                               MEMORY.md head, SESSION-DIGEST tail
                    · Message: "Context was compacted. Re-read any file you need."

  T+end     OPERATOR INVOKES /wrap (or attempts /stop)
  ───────────────────────────────────────────────────
              │
              ├─► If /wrap invoked:
              │     · Claude runs wrap protocol (6 steps)
              │     · Commit changes, update MEMORY, write SESSION-DIGEST
              │     · Manual digest (substantive)
              │
              ├─► When Claude attempts Stop:
              │     · Hook: stop-checklist.sh fires
              │     · If uncommitted changes: exit 2 (force continuation)
              │     · Message: "Did you commit? Did you update MEMORY? Digest?"
              │     · stop_hook_active flag check prevents retry loop
              │
              └─► SESSION ENDS — SessionEnd cascade fires in parallel:
                  1. session-end-digest.sh (auto-stub digest, 1.5s timeout)
                  2. backup-state.sh (background tarball)
                  3. sync-memory-curated.sh (background curated sync)
                  · Background processes detached, session closes immediately

═══════════════════════════════════════════════════════════════════════════
```

## Event-to-Hook Mapping

```
┌──────────────────────┬───────────────────────────────────────────────┐
│  CLAUDE CODE EVENT   │  HOOKS THAT FIRE (canonical 13-hook setup)    │
├──────────────────────┼───────────────────────────────────────────────┤
│  SessionStart        │  session-start.sh                             │
│  UserPromptSubmit    │  scan-secrets.sh                              │
│  PreToolUse:Bash     │  block-git-push.sh                            │
│                      │  block-git-add-all.sh                         │
│  PreToolUse:Write|   │  block-versioned-files.sh                     │
│    Edit              │  block-secrets-in-code.sh                     │
│  PostToolUse:Write|  │  auto-format.sh                               │
│    Edit              │                                               │
│  PostToolUseFailure: │  post-bash-failure.sh                         │
│    Bash              │                                               │
│  Stop                │  stop-checklist.sh                            │
│  PreCompact          │  precompact-save.sh                           │
│  PostCompact         │  post-compact-recover.sh                      │
│  TaskCompleted       │  task-completed-verify.sh                     │
│  SessionEnd          │  session-end-digest.sh                        │
│                      │  backup-state.sh                              │
│                      │  sync-memory-curated.sh                       │
└──────────────────────┴───────────────────────────────────────────────┘
```

## The Critical Insights

**Insight 1: The session has a beginning, middle, and end.** Each has its own hook events. Designing across all three creates a coherent lifecycle. Designing only one (e.g., only PreToolUse) creates a system that works mid-session but degrades at boundaries.

**Insight 2: Background hooks at SessionEnd are essential.** SessionEnd has a 1.5s timeout. Anything slow (backup, sync, git operations) must background + disown. Otherwise it gets killed and you lose the operation.

**Insight 3: PreCompact + PostCompact are anti-amnesia partners.** They exist BECAUSE auto-compaction is lossy. Designing them in pairs (snapshot at compact, recovery after compact) bridges the discontinuity.

**Insight 4: The Stop hook's stop_hook_active flag is critical.** Without it, the Stop hook can retry 9 times, wasting minutes. This single line of bash, born from a real incident, prevents the loop.

---

# Part 13: Adoption Levels

Four levels, from "anyone can do this in 90 minutes" to "operator running multi-project memory empire."

## Level 1: Minimal (90 minutes total)

The smallest setup that demonstrates the pattern. Day-one functional.

```
ARTIFACTS                              EFFORT
─────────                              ──────

~/.claude/                              5 min   git init, .gitignore, push to private remote
├── README.md                          10 min   5-line orient
├── CLAUDE.md                          15 min   ~40 lines of behavioral rules
├── settings.json                      10 min   1 env var, 1 deny, 3 hook regs
├── hooks/
│   ├── block-git-push.sh              10 min   Copy from this kit
│   ├── scan-secrets.sh                10 min   Copy from this kit
│   └── session-start.sh                5 min   Copy from this kit
├── skills/
│   ├── boot.md                        10 min   Copy from this kit
│   └── wrap.md                        10 min   Copy from this kit
└── projects/<your-slug>/memory/
    └── MEMORY.md                       5 min   3 atom pointer lines

Plus first atoms (3 files, ~10 lines each):  15 min total
```

**Result:** Fully functional baseline. Behavioral rules in place. Push protection active. Session start orientation working. Boot/wrap rituals available.

**Time investment:** ~90 minutes total.

**What you can do at this level:**
- Work in any project, get behavioral rule baseline
- /boot at session start, /wrap at session end
- Cross-session continuity via SESSION-DIGEST.md
- Push safety from day one

## Level 2: Standard (3-5 hours additional, over Week 1)

Build on Level 1. Add machine identity, more hooks, first off-site backup.

```
ARTIFACTS ADDED                        EFFORT
───────────                             ──────

<strategy-hub>/CLAUDE.md               30 min   Machine identity + project inventory
First <project>/CLAUDE.md              20 min   Project identity + validation
hooks/
├── block-git-add-all.sh                5 min   Copy from this kit
├── block-secrets-in-code.sh           10 min   Copy from this kit
├── precompact-save.sh                 15 min   Copy + customize
├── post-compact-recover.sh            10 min   Copy from this kit
└── stop-checklist.sh                  10 min   Copy from this kit (with retry-loop fix)
skills/
└── status.md                          10 min   Copy from this kit
scripts/
└── backup-state.sh                    45 min   Customize for your remote
First 5-10 atoms                       60 min   Captured organically during use
```

**Result:** ~10 atoms, 8 hooks, 3 skills. Off-site backup running. Lived-in system.

**Time investment:** Additional 3-5 hours over Week 1.

**What you can do at this level:**
- Multi-tier CLAUDE.md hierarchy applied
- Anti-amnesia hooks protecting against context compaction
- Stop hook preventing accidental session abandonment
- Off-site backup running on every SessionEnd

## Level 3: Full Power (10-15 hours additional, over Month 1)

Build on Level 2. Add custom agents, more skills, hook test suite, memory integrity checks.

```
ARTIFACTS ADDED                        EFFORT
───────────                             ──────

agents/
├── explorer.md (haiku, read-only)     30 min   Cost-tier 1 agent
├── verifier.md (sonnet, background)   45 min   Cost-tier 2 agent
└── researcher.md (sonnet, web+code)   30 min   Cost-tier 2 agent
skills/
├── research.md                        60 min   Parallel research swarm
└── audit.md                           90 min   Multi-agent quality gate
hooks/
├── post-bash-failure.sh               20 min   Bash failure guidance
├── auto-format.sh                     30 min   Post-write formatting
├── task-completed-verify.sh           15 min   Completion guard
├── block-versioned-files.sh           10 min   No-copies guard
└── session-end-digest.sh              20 min   Auto-stub digest
scripts/
└── sync-memory-curated.sh             60 min   Channel B curated sync
tests/
├── run-tests.sh                       30 min   Single entry point
└── hooks/                            120 min   Test for each hook
First ~30 atoms                        Captured organically
First lesson_*.md atom                  When first caught failure becomes a rule
Memory integrity check on boot         30 min   Orphan detector
```

**Result:** ~30 atoms, 13 hooks tested, 5 skills, 3 cost-tiered agents. Production-grade setup.

**Time investment:** Additional 10-15 hours over Month 1.

**What you can do at this level:**
- /research swarm for any new domain
- /audit multi-agent quality gate
- Cost-tiered agent execution (haiku for recon, sonnet for analysis)
- Memory integrity check at boot catches orphans
- Hook test suite catches regressions

## Level 4: Godmode (~30 hours over Month 3+, then ongoing)

Build on Level 3. Add war room pattern, bidirectional sync, quarterly platform reviews, sanitized share templates.

```
ARTIFACTS ADDED                        EFFORT
───────────                             ──────

War room namespace pattern             Ongoing   Cross-project memory consolidation
Per-project namespaces (3+)            Ongoing   Project-scoped memory
Bidirectional remote sync              90 min    Channel C (remote → local)
Quarterly platform review               60 min/Q  Catch native features replacing custom
Cost telemetry (monthly export)         30 min/M  Trend data over time
Sanitized share template                3 hours   Generic version of own setup
Documented operating model              5 hours   Kit-style docs (like this one)
Encrypted-at-rest memory directory      60 min    For high-risk environments
Periodic conflict audit                 60 min    Cross-atom contradiction scanner
Restore drill                           30 min/Q  Test backup actually restores
```

**Result:** Mature multi-project operator stack. 80% custom, 10% borrowed, 10% native. Documented, testable, restorable.

**Time investment:** Additional ~30 hours over Month 3+, then ongoing maintenance (~5 hours/month).

**What you can do at this level:**
- War room consolidates cross-project intel
- Bidirectional sync prevents memory bifurcation
- Quarterly platform review catches drift against native features
- Sanitized share enables documentation/sharing without leaking
- Restore drill validates backup actually works
- System survives bus-factor-1 risk (documented + onboardable)

## The Tiered Learning Curve

```
LEVEL    HOURS   FEATURES                          MATURITY
─────    ─────   ────────                          ────────

L1       1.5h    Basic safety + boot/wrap          Beginner — system works
L2       5h      + machine identity, more hooks    Intermediate — pattern emerges
L3       15h     + agents, skills, tests           Advanced — production-grade
L4       30h     + war room, share, restore drill  Expert — fully matured
```

The right level depends on your usage:
- **Single project, casual use:** L1 is enough
- **Multi-project, daily driver:** L2 minimum, L3 recommended
- **Critical workflows + multi-machine:** L3 minimum, L4 recommended
- **Considering sharing/documentation:** L4 required

## Anti-Patterns During Adoption

**Anti-pattern A: Building all hooks day one.** Each hook should be born from a failure or anticipated risk. Building 13 hooks before you understand the lifecycle just means 13 hooks that don't catch real issues yet.

**Anti-pattern B: Skipping tests.** Hooks without tests are immune systems without checkups. Add tests as you add hooks.

**Anti-pattern C: Premature war room.** If you only run one project, the war room adds friction. Wait until you have 3+ concurrent projects.

**Anti-pattern D: Custom everything from day one.** Use platform built-ins (Plan agent, init skill) until you understand what's missing. Then build custom for the gaps.

---

# Part 14: Anti-Patterns and Trade-offs

The patterns in this blueprint earn their keep. They also have costs. Naming the costs is intellectual honesty.

## Anti-Pattern 1: All-Custom-No-Tests

Building 13 hooks without tests creates an immune system without checkup. If a regex misses a new credential format, you find out when the leak happens.

**Mitigation:** Hook test suite from Day 1. Adding a hook = adding a test. Run `tests/run-tests.sh` before committing.

**Cost of mitigation:** ~30 minutes per hook to write a basic test. Worth it.

## Anti-Pattern 2: Cost-of-Recall Ignored

Every memory atom load costs tokens. The MEMORY.md index loads on every prompt. Anything in the index is paying a persistent token cost.

**Math:** A 73-line index at ~50 tokens/line = ~3,650 tokens per prompt. At 100 prompts/day = 365,000 tokens/day just in index loads. At Opus pricing, that's meaningful annual cost.

**Mitigation:** 200-line cap is a hard ceiling, not a target. Prune aggressively. At 180 lines, prune before adding more.

## Anti-Pattern 3: Drift Against Platform

Operator builds custom feature. Anthropic ships native equivalent six months later. Operator never notices. Custom becomes duplicate.

**Mitigation:** Quarterly review (15 minutes) of new platform features. Migrate when native is strictly better.

**Specific examples that have happened:**
- Custom `/ultrareview` skill built before cloud `/ultrareview` was available
- Custom PreCompact hook before platform documented PreCompact event
- Custom Sonnet subagent setup before `CLAUDE_CODE_SUBAGENT_MODEL` env var shipped

## Anti-Pattern 4: Bus Factor of 1

Operator-tuned system survives one machine nuke (via backup) but not one operator departure (no documentation).

**Mitigation:**
- README at `~/.claude/` root with 5-line orient
- Kit-style docs (like this one) in `~/.claude/docs/`
- Sanitized public version of setup template
- Bootstrap script for new machine

**Test of mitigation:** Can someone unfamiliar with your setup boot a fresh machine to working state using only your docs?

## Anti-Pattern 5: Stale Namespace Accumulation

Memory namespaces never get cleaned up. After 18 months, you have 30 namespaces, 28 of which haven't been touched in 90+ days. The active 2 get harder to find.

**Mitigation:** 90-day archive rule. Namespace untouched 90 days → archive to `~/.claude/projects/_archive/`. Reversible, doesn't delete.

## Anti-Pattern 6: Backup-Not-Restore

Backup pipeline runs daily. Never tested for restore. "We have backups" until you find out you don't.

**Mitigation:** Quarterly restore drill. 30 minutes per quarter. Pull latest tarball, verify integrity, test fresh-machine load.

## Anti-Pattern 7: Manual Ritual Single-Point-of-Failure

`/wrap` is manual. Auto-digest hook produces stub. If operator forgets /wrap, continuity dies.

**Mitigation:**
- Upgrade auto-digest hook to be substantive (last 5 commits, tools used count, files modified)
- Add SessionEnd warning if /wrap not run recently
- Make /wrap a habit not a choice

## Anti-Pattern 8: 100% Public When Should Be Private

Memory atoms accidentally pushed to public git. Sanitization issues. Identifying intel leaked.

**Mitigation:**
- scan-secrets hook on memory writes
- block-memory-push hook on git push
- `.gitignore` for memory paths (when memory dir is under a git repo)
- Periodic grep for known-sensitive patterns in memory dir
- Sanitized export pipeline for sharing

## Master Anti-Pattern Table

| Anti-Pattern | Symptom | Mitigation |
|--------------|---------|------------|
| All-Custom-No-Tests | Hook regex gaps slip silently | Hook test suite from Day 1 |
| Cost-of-Recall Ignored | High token cost per prompt | 200-line cap; prune aggressively |
| Drift Against Platform | Custom duplicates native | Quarterly review |
| Bus Factor of 1 | Operator-only knowable | README + docs + bootstrap |
| Stale Namespace Accumulation | Dead namespaces pile up | 90-day archive rule |
| Backup-Not-Restore | Untested backup hypothesis | Quarterly restore drill |
| Manual Ritual SPOF | /wrap forgotten = continuity dies | Substantive auto-digest + reminders |
| 100% Public When Private | PII / secrets pushed to public git | Multiple gates: scan hooks + block-push + .gitignore |

## The Honest Trade-offs

This blueprint is opinionated. Some trade-offs are explicit:

**Trade-off 1: Operator-time vs platform-feature.** Custom hooks earn full control at cost of build time + maintenance burden. For high-value workflows, custom is correct. For low-frequency tasks, native built-ins are correct.

**Trade-off 2: Discipline vs flexibility.** 13 hooks impose discipline. Some operators will find this constraining. The discipline pays dividends, but only if the operator can sustain it.

**Trade-off 3: Cost vs quality.** Always-Opus + always-high-effort is expensive. For director-level operators, the per-decision value justifies the cost. For exploratory work, dropping to Sonnet may be correct.

**Trade-off 4: Sophistication vs onboardability.** Highly tuned operator stacks are harder to onboard. A simpler stack with worse coverage may be more shareable.

There is no universal right answer. Pick deliberately based on your workflow and your sustainability.

---

## Final Words

This blueprint is the architectural skeleton of a mature Claude Code operator setup. It is not the only correct architecture. It is one operator's documented choice, sanitized for adoption or evaluation by others.

Components shown:
- 3-root filesystem model
- 3-tier CLAUDE.md hierarchy
- ~30-entry settings.json
- 13 hooks across 10 events
- 5 user-invocable skills
- 3 cost-tiered custom agents
- 8 MCP server families
- Curated plugin enablement
- Memory namespaces with war room pattern
- Two-channel off-site backup
- Provenance discipline (80/10/10 split)
- Full integration event timeline
- 4-tier adoption path
- 8 named anti-patterns

The patterns shown have been earned. Every hook prevents a real failure mode. Every skill matches a real workflow need. Every architectural choice has a documented trade-off.

```
┌────────────────────────────────────────────────┐
│                                                 │
│   Architecture is not aesthetics.               │
│                                                 │
│   It's what survives when individual decisions │
│   become organizational habits.                 │
│                                                 │
│   The blueprint is not the building.            │
│   But every building that lasts                 │
│   started with one.                             │
│                                                 │
│   Adopt or adapt — but build deliberately.      │
│                                                 │
└────────────────────────────────────────────────┘
```

---

*This blueprint is a sanitized architectural reference, not an export of any specific operator's data.*
*Adopt entire patterns or pick individual components. The structure is more valuable than the specifics.*
*For memory system mechanics, see the companion [memory-kit]. For operating philosophy, see [ezekiel-kit].*

[memory-kit]: memory-kit.md
[ezekiel-kit]: ezekiel-kit.md
[memory-kit Part 10]: memory-kit.md#part-10-the-war-room-pattern
