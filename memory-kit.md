# The Memory Kit — How Claude Code Remembers

> A complete memory system for Claude Code, forged from hundreds of sessions where the AI forgot everything that mattered.
> Every rule backed by evidence. Every pattern earned by repeating the same explanation for the 50th time.
> Drop this in your setup and stop teaching a goldfish.

> *"There is no remembrance of former things; neither shall there be any remembrance of things that are to come with those that shall come after."* — Ecclesiastes 1:11

---

## The Story — Why This Exists

A senior engineer opens a fresh Claude Code session for a project he's been working on for six months. He types: "let's continue where we left off."

Claude says: "I'd be happy to help — could you tell me a bit about the project?"

That moment — repeated thousands of times across millions of users — is what this document fixes.

The default Claude Code session is **stateless**. Every conversation begins from absolute zero. The model is brilliant, but it remembers nothing between sessions. Not your codebase. Not your preferences. Not the bug you fixed yesterday. Not the architecture decision you spent two hours explaining. Not even your name.

For a one-shot task ("rename this function"), statelessness is fine. For a multi-month project, it's a slow-motion catastrophe. You become a human Stack Overflow for your own AI partner, re-explaining the same context in every session, until you either burn out or accept mediocrity.

**Memory is the fix.** Not a vector database. Not a fine-tuned model. Just plain markdown files on disk, structured so that Claude reads them on boot and writes to them as you work. Boring tech, surgical results.

The system in this kit emerged from running Claude Code as a daily driver across multiple long-running projects in different domains. Different problems, same memory primitives. The patterns survived because they earned it: every failure mode catalogued here cost someone real time, real trust, or real money.

**This document is everything that survived.** Adopt it whole. Adopt it piecewise. Just don't ship without memory and wonder why your AI partner has the institutional memory of a goldfish.

---

## Table of Contents

1. [Part 1: The Amnesia Problem](#part-1-the-amnesia-problem)
2. [Part 2: The Architecture](#part-2-the-architecture)
3. [Part 3: Atom Anatomy](#part-3-atom-anatomy)
4. [Part 4: The Four Atom Types](#part-4-the-four-atom-types)
5. [Part 5: The Index — MEMORY.md](#part-5-the-index--memorymd)
6. [Part 6: Lifecycle of a Memory Atom](#part-6-lifecycle-of-a-memory-atom)
7. [Part 7: Data Flow — What Loads When](#part-7-data-flow--what-loads-when)
8. [Part 8: What NOT to Save](#part-8-what-not-to-save)
9. [Part 9: Stale Protection](#part-9-stale-protection)
10. [Part 10: The War Room Pattern](#part-10-the-war-room-pattern)
11. [Part 11: Session Lifecycle Integration](#part-11-session-lifecycle-integration)
12. [Part 12: Memory Failure Modes](#part-12-memory-failure-modes)
13. [Part 13: Hooks for Memory Discipline](#part-13-hooks-for-memory-discipline)
14. [Part 14: Quick Start](#part-14-quick-start)

---

# Part 1: The Amnesia Problem

Before you can fix something, you have to feel it.

## What "Stateless" Actually Means

```
SESSION 1                          SESSION 2
─────────                          ─────────

You: "I'm working on a Rust        You: "let's continue"
      service. We use rust_decimal
      for money math. Never f64.   Claude: "Sure! What's the project?
      The build command is              What language are you using?"
      `cargo test --workspace`."

Claude: "Got it. What should
         we tackle first?"          You: <30 minutes re-explaining>

[2 hours of useful work]            Claude: "Got it. What should
                                              we tackle first?"
SESSION ENDS
                                    [2 hours of useful work]

                                    SESSION ENDS

                                    SESSION 3
                                    ─────────

                                    [Same thing. Forever.]
```

This pattern compounds. Across a 6-month project with 100+ sessions, you spend a measurable percentage of your total time re-establishing context that should have been persisted on day one.

## The Three Failure Modes You've Felt Without Naming

**Failure 1: Re-explanation tax.**
You explain your stack, your conventions, your role, your preferences. Every. Single. Session. The cost isn't just minutes — it's the cognitive flatness of starting cold each time.

**Failure 2: Lost decisions.**
You make a careful architectural choice in Session 12 ("we chose Postgres over MongoDB because of X"). In Session 34, the same question comes up. Claude has no memory of the prior decision. You either rebuild the analysis or accept whatever Claude suggests now — possibly contradicting your past self.

**Failure 3: Repeated mistakes.**
You correct Claude in Session 7 ("don't run `git add -A`, use specific files"). Session 18: `git add -A`. Session 23: `git add -A`. The correction never sticks because it lives in a conversation that no longer exists.

## What Memory Fixes

```
WITHOUT MEMORY                      WITH MEMORY
──────────────                      ───────────

Stateless every session             Knows you on session 2
Re-explain stack each time          Stack documented once
Lost architectural decisions        Decisions persist + linked
Same mistakes repeat                Corrections become rules
Goldfish partner                    Colleague who remembers
2 hrs of useful work / session      4 hrs of useful work / session
Project knowledge in your head      Project knowledge on disk
You leave → project dies            You leave → handoff is trivial
```

The math is brutal: **a well-tuned memory system roughly doubles productive output per session** and makes handoff to another operator (or to future-you, six months later) feasible instead of catastrophic.

---

# Part 2: The Architecture

The memory system has four layers. Three are persistent (survive across sessions). One is volatile (lives only inside the current conversation).

## The Big Picture

```
═══════════════════════════════════════════════════════════════════════════
                    VOLATILE LAYER (RAM, dies with session)
═══════════════════════════════════════════════════════════════════════════

   ┌─────────────────────────────────────────────────────────────────┐
   │   Active conversation context (~200K tokens working memory)     │
   │   Auto-compacts at ~80% capacity → PreCompact hook fires        │
   │   Lost when session ends — unless persisted by wrap ritual      │
   └─────────────────────────────────────────────────────────────────┘
                              ▲                ▲
                              │                │
                    READ ON   │                │   WRITE ON
                    BOOT      │                │   WRAP / Hook
                              ▼                ▼

═══════════════════════════════════════════════════════════════════════════
                  PERSISTENCE LAYER (disk, survives sessions)
═══════════════════════════════════════════════════════════════════════════

   ┌─── TIER 1: STATIC RULES (loaded EVERY prompt) ─────────────────┐
   │                                                                 │
   │   ~/.claude/CLAUDE.md                                           │
   │     └─► User-global rules across ALL projects/machines          │
   │         · Behavioral guarantees (verification, comments, tone)  │
   │         · Identity preferences                                  │
   │                                                                 │
   │   <project>/CLAUDE.md                                           │
   │     └─► Project-level identity and critical constraints         │
   │         · Validation commands · codebase map · workflow         │
   │                                                                 │
   └─────────────────────────────────────────────────────────────────┘
                              │
   ┌─── TIER 2: AUTO-MEMORY ATOMS (cross-session, on-demand) ───────┐
   │                                                                 │
   │   ~/.claude/projects/<project-slug>/memory/                     │
   │                                                                 │
   │   ┌─ MEMORY.md ────────────────── (always-loaded index, ≤200) ┐ │
   │   │  - [User role] (user_role.md) — Senior backend engineer   │ │
   │   │  - [Quality preference] (feedback_tests.md) — No mocks    │ │
   │   │  - [Sprint deadline] (project_sprint.md) — Ship by 03-15  │ │
   │   │  - [Dashboard URL] (reference_grafana.md) — Latency board │ │
   │   │  ... (one line per atom, hard-capped at 200 lines)        │ │
   │   └────────────────────────────────────────────────────────────┘ │
   │                          │                                       │
   │                          ▼ links to                              │
   │   ┌─ ATOM FILES (one fact = one file) ────────────────────────┐ │
   │   │  user_role.md                                              │ │
   │   │  feedback_tests.md                                         │ │
   │   │  project_sprint.md                                         │ │
   │   │  reference_grafana.md                                      │ │
   │   │  ... (tens to hundreds of atoms, each ~10-30 lines)        │ │
   │   └────────────────────────────────────────────────────────────┘ │
   │                                                                 │
   └─────────────────────────────────────────────────────────────────┘
                              │
   ┌─── TIER 3: SESSION HANDOFF (per-project) ──────────────────────┐
   │                                                                 │
   │   <project>/SESSION-DIGEST.md                                   │
   │     └─► Last session's outcome, decisions, next steps           │
   │         Written at wrap, read at next boot                      │
   │                                                                 │
   │   <project>/MEMORY.md           (project-specific NEXT list)    │
   │     └─► Active phase, blockers, decisions, calibration data     │
   │                                                                 │
   └─────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════
```

## Why Each Layer Exists

**Tier 1 — Static Rules.** These are *behavioral contracts*. Things that should be true in every session, every project. "Always verify before claiming done." "Never push without explicit approval." They're loaded on every prompt because they have to be authoritative — you can't have a rule that applies sometimes.

**Tier 2 — Auto-Memory Atoms.** These are *episodic facts*. Things you learned, decided, or were told. They're loaded selectively — the index is always visible, the full atom content loads only when relevant. This is the heart of the system.

**Tier 3 — Session Handoff.** These are *continuity primitives*. They let Session N+1 begin where Session N ended without forcing you to re-orient.

**Volatile Layer.** This is where actual work happens. It's lossy by design — the context window has limits. The persistence layer exists specifically so that loss of volatile state doesn't lose ground truth.

## Critical Design Choice: Plain Files

```
┌────────────────────────────────────────────────────┐
│  WHY NOT A DATABASE?                                │
│                                                     │
│  · Git-trackable (history of every memory change)   │
│  · Greppable (find any fact in milliseconds)        │
│  · Human-readable (you can audit, fix, prune)       │
│  · Editor-native (open in your IDE, no SDK)         │
│  · Zero infrastructure (no daemon, no migrations)   │
│  · Portable (rsync the folder, you're moved)        │
│  · Resilient (corrupt one file ≠ lose everything)   │
└────────────────────────────────────────────────────┘
```

Vector databases offer semantic recall — finding "similar" memories without exact match. That's a real capability plain markdown does not have. The trade-off is operational: vector DBs add a daemon, a dependency, a migration path, and an opacity layer. For project memory at the scale of a single operator (or small team), the trade-off favors plain markdown. For larger scale or semantic-recall-critical use cases, a vector DB may be the right choice. Pick deliberately.

---

# Part 3: Atom Anatomy

An atom is one file. One file is one fact. That's the whole rule.

## The Template

```markdown
---
name: short-kebab-case-slug
description: One-line summary that survives in the index standalone.
metadata:
  type: user | feedback | project | reference
  originSessionId: <optional traceback identifier>
---

<body — the actual content, structured by type — see Part 4>

Related: [[other-atom-slug]] [[another-atom-slug]]
```

## Field-by-Field

**`name:`** — The unique slug. Used as the identifier in cross-atom links (`[[name]]`). Kebab-case, short, descriptive. Must be globally unique within the memory directory.

```
GOOD                          BAD
────                          ───
user-prefers-rust             info1
feedback-no-mocks             important-thing
project-q3-launch             status
reference-grafana-latency     dashboard
```

**`description:`** — A one-line elevator pitch. **This is the single most important field in the entire system.** The description is what appears in the index. The description is what Claude reads when deciding whether to open the atom. A vague description means the atom is invisible.

```
GOOD                                              BAD
────                                              ───
"User is senior Go engineer, new to React.        "User info"
 Frame frontend explanations in Go analogues."

"Integration tests must hit real DB, not mocks.   "Testing"
 Reason: prior mock/prod divergence incident."

"Sprint deadline 2026-03-15 for v2 launch.        "Deadline"
 No non-critical merges after 03-12."
```

**`metadata.type:`** — One of four values. Determines how the atom is structured and used. (Full breakdown in Part 4.)

**`metadata.originSessionId:`** — Optional. A traceback identifier so you can find the conversation that created this atom if you need original context.

## The Body

The body's structure depends on the atom type:

- **`user`** — Free-form. Whatever helps Claude tailor behavior to you specifically.
- **`feedback`** — Lead with the rule, then `**Why:**` line, then `**How to apply:**` line.
- **`project`** — Lead with the fact/decision, then `**Why:**` line, then `**How to apply:**` line.
- **`reference`** — Free-form. Pointer plus brief notes on what's there.

## Wiki-Style Links

Use `[[atom-slug]]` to link atoms together. This creates a knowledge graph:

```markdown
The integration test policy ([[feedback-no-mocks]]) is enforced by
the CI workflow at [[reference-ci-config]], which runs against the
sandbox database described in [[project-sandbox-db]].
```

**Links to non-existent atoms are not errors.** They're *intent markers* — a `[[some-future-atom]]` link is a signal that "this should be written eventually." When you do write it, the link becomes live automatically. No graph DB needed.

## Real Atom Example (Generic)

```markdown
---
name: feedback-no-mocks-in-integration-tests
description: "Integration tests must use real database, not mocks.
              Reason: prior incident where mocks passed but prod migration broke."
metadata:
  type: feedback
  originSessionId: a1b2c3d4-...
---

Integration tests in tests/integration/ must run against a real
Postgres instance, not mocks.

**Why:** A previous incident — a database migration passed all
mocked integration tests but failed in production because the mocks
didn't model trigger behavior. The team lost 6 hours rolling back
and re-shipping. The lesson stuck: if it talks to the database in
production, it talks to a database in test.

**How to apply:** When writing or reviewing tests in tests/integration/,
verify they use the testcontainers fixture, not the MockDB helper.
The MockDB helper is fine for unit tests in tests/unit/.

Related: [[reference-testcontainers-fixture]] [[project-migration-protocol]]
```

That atom — once it exists — never has to be re-explained. Every future session reads it from the index, opens it if relevant, and applies the rule automatically.

---

# Part 4: The Four Atom Types

The system distinguishes four types. Each type answers a different question.

## Type 1: `user`

**Question answered:** Who is the user?

**Content:** Role, expertise, goals, preferences, identity, communication style.

**Body structure:** Free-form. Whatever helps Claude tailor behavior.

**What NOT to put here:** Things already covered in CLAUDE.md. Don't duplicate.

```markdown
---
name: user-role-and-context
description: User is a data scientist focused on observability/logging,
             new to the company's TypeScript frontend codebase.
metadata:
  type: user
---

The user is a data scientist (Python + SQL background, 8 years).
Currently embedded with platform team to investigate logging gaps.

Has not worked with TypeScript or React before. When explaining
frontend concepts, lean on Python/Jupyter analogies where they
exist. Avoid framework jargon without unpacking it the first time.

Prefers concrete examples over abstract architecture diagrams.
```

**When to write:** First time you learn anything substantive about who the user is, what they do, what they know, or how they want to interact.

**When to read:** When the user's profile should shape your response — explaining things, recommending approaches, judging what level of detail to give.

## Type 2: `feedback`

**Question answered:** How should I work with this user?

**Content:** Corrections ("don't do X") and validations ("yes, that approach is right"). Operational lessons.

**Body structure:**
- Lead with the rule.
- `**Why:**` line — the reason. Often a past incident or strong stated preference. Knowing *why* lets you handle edge cases.
- `**How to apply:**` line — when and where this kicks in.

**Critical:** Save from both correction AND confirmation. Corrections are easy to notice. Confirmations are quieter — you have to watch for "yes, exactly" or non-pushback on an unusual choice. Both shape behavior; both should be saved.

```markdown
---
name: feedback-terse-responses
description: User wants terse responses without trailing summaries.
             Reads diffs directly.
metadata:
  type: feedback
---

End responses with the result. Do not append "Summary of changes:"
or "What I did:" sections after the work is reported.

**Why:** The user reads the diff and the test output directly. A
trailing summary just duplicates information they've already seen
and adds visual noise. They said: "I can read the diff."

**How to apply:** After completing a task, state what's done in one
sentence. Don't bullet-list the changes. Don't recap. Move on.
```

**When to write:** Any time the user corrects you, or any time they confirm an unusual approach. The signal isn't "did they say something nice" — it's "did they reveal a preference that I would not have inferred from the code or context."

**When to read:** Continuously. Feedback atoms shape your behavior in real time.

## Type 3: `project`

**Question answered:** What is currently happening in this work?

**Content:** State, status, deadlines, decisions, ongoing initiatives, people, motivations behind the work.

**Body structure:**
- Lead with the fact or decision.
- `**Why:**` line — the motivation (constraint, deadline, stakeholder ask).
- `**How to apply:**` line — how this should shape suggestions.

**Critical:** Project atoms decay fast. Always use absolute dates ("2026-03-15"), not relative ones ("next Thursday"). Update or remove when status changes — don't accumulate stale snapshots.

```markdown
---
name: project-q3-feature-freeze
description: Merge freeze begins 2026-03-12. Mobile team cuts release branch
             from main on 2026-03-15.
metadata:
  type: project
---

A merge freeze on non-critical changes begins 2026-03-12.

**Why:** The mobile team is cutting a release branch from main on
2026-03-15 and needs main to be stable for 3 days prior. Critical
fixes still go in; everything else waits until after the cut.

**How to apply:** When the user proposes any non-critical PR work
scheduled to merge after 2026-03-12, flag the freeze. Suggest
either landing before the deadline or queuing for after the cut.
```

**When to write:** When you learn anything about who is doing what, why, or by when, that isn't already obvious from the code or git history.

**When to read:** When the user's request might intersect with current project state, deadlines, or constraints.

## Type 4: `reference`

**Question answered:** Where does this information live outside the codebase?

**Content:** Pointers to external systems — dashboards, ticket trackers, Slack channels, documentation sites, vaults, runbooks.

**Body structure:** Free-form. URL or path, plus brief notes on what's there and when to consult.

```markdown
---
name: reference-incident-runbook
description: Runbook for production incidents lives at runbooks.internal/api-pager.
             Oncall checks this first.
metadata:
  type: reference
---

The runbook for API pager incidents is at:
  https://runbooks.internal/api-pager

Sections:
- "Initial triage" — first 5 minutes
- "Common failures" — top 10 with playbooks
- "Escalation" — when to wake the team lead

If the user mentions an API pager, alert, or page, suggest checking
this runbook before diving into code. The runbook is more current
than anything in the repo.
```

**When to write:** When the user references an external system that isn't in the codebase but is part of how the work gets done.

**When to read:** When the user asks about something that probably has a system-of-record outside the code.

## Summary Table

```
┌──────────┬───────────────────────────────┬──────────────────────────┐
│  TYPE    │  ANSWERS                      │  DECAY RATE              │
├──────────┼───────────────────────────────┼──────────────────────────┤
│ user     │  Who is the user?             │  Slow (months to years)  │
│ feedback │  How should I work with them? │  Slow (corrections stick)│
│ project  │  What's happening now?        │  FAST (weeks)            │
│ reference│  Where does external info live│  Medium (months)         │
└──────────┴───────────────────────────────┴──────────────────────────┘
```

The decay rate matters: project atoms need active pruning. User and feedback atoms compound in value over time. Reference atoms are touched-up when systems migrate.

---

# Part 5: The Index — MEMORY.md

`MEMORY.md` is not a memory atom. It's an *index of atoms.* Treat the distinction as sacred.

## The 200-Line Hard Limit

```
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│   MEMORY.md is loaded INTO CONTEXT on every prompt.          │
│                                                              │
│   Lines beyond 200 are SILENTLY TRUNCATED.                   │
│                                                              │
│   No error. No warning. They just don't get loaded.          │
│                                                              │
│   If you have 250 entries, the last 50 don't exist as far    │
│   as Claude is concerned.                                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

This is the single most-violated rule in the entire system because nothing warns you about it. Stay under 200 lines. If you're approaching 180, prune.

## The Format

Each entry is one line:

```markdown
- [Short Title](filename.md) — One-line hook that says why this matters.
```

That's it. No frontmatter on `MEMORY.md`. No nested headings (they break parsing). Just lines.

## Anatomy of a Good Entry

```
- [Sprint deadline 03-15](project_q3_freeze.md) — Merge freeze 03-12 for mobile release cut
  ▲                       ▲                      ▲
  │                       │                      │
  Title                   Filename               Hook
  (scannable)             (must exist)           (decision-making info)
```

- **Title** — what the atom is about, in 3-6 words. Scannable.
- **Filename** — the actual atom file in the same directory. If this is wrong, the link is dead.
- **Hook** — the *reason* this atom matters. Not just a topic label — a piece of information that helps Claude decide whether to open it.

## Good vs Bad Hooks

```
BAD HOOKS                                  GOOD HOOKS
─────────                                  ──────────

"User stuff"                               "Senior Go dev, new to React frontend"

"Testing preferences"                      "Integration tests must hit real DB"

"Project status"                           "Phase 4 complete, demo Q2 2026"

"Some thoughts"                            "Don't suggest pivots while work unfinished"

"API info"                                 "Dashboard at grafana.io/api-latency — oncall"
```

The bad hooks force Claude to open the atom just to know what it's about. The good hooks let Claude decide from the index alone whether the atom is relevant.

## What Goes in the Index vs the Atoms

| Content | Where | Why |
|---------|-------|-----|
| Pointer + one-line hook | MEMORY.md | Always loaded, must stay small |
| Full rule + Why + How | atom file | Loaded only when relevant |
| Examples and detail | atom file | Same reason |
| Cross-references | atom file (via `[[links]]`) | Graph lives in atoms |
| Timestamp / origin | atom frontmatter | Not for the index |

## Organize Semantically, Not Chronologically

```
GOOD (semantic grouping by topic):              BAD (chronological):

- [User role](user_role.md) — ...               - [Tue 03-04](session_03_04.md) — ...
- [Feedback: tests](feedback_tests.md) — ...    - [Wed 03-05](session_03_05.md) — ...
- [Feedback: commits](feedback_commits.md) — .. - [Thu 03-06](session_03_06.md) — ...
- [Project: sprint](project_sprint.md) — ...    - [Fri 03-07](session_03_07.md) — ...
- [Project: freeze](project_freeze.md) — ...
- [Reference: docs](reference_docs.md) — ...
- [Reference: pager](reference_pager.md) — ...
```

Chronological organization decays fast. Semantic organization compounds in value. Cluster related atoms; let topics group naturally via filename prefixes (`user_*`, `feedback_*`, `project_*`, `reference_*`).

---

# Part 6: Lifecycle of a Memory Atom

Every atom moves through four phases.

```
   ┌──────────────────────────────────────────────────────────────┐
   │                                                              │
   │   1. CREATE                                                  │
   │   ────────                                                   │
   │      Trigger: learn a fact worth persisting                  │
   │             ▼                                                │
   │      Write: ~/.claude/projects/<slug>/memory/new_atom.md     │
   │             ▼                                                │
   │      Index: append one line to MEMORY.md                     │
   │                                                              │
   │   2. READ                                                    │
   │   ──────                                                     │
   │      Trigger: next session boot, OR topic surfaces in chat   │
   │             ▼                                                │
   │      MEMORY.md index loads automatically (always)            │
   │             ▼                                                │
   │      Relevant atom loaded on-demand via Read tool            │
   │             ▼                                                │
   │      Content informs response                                │
   │                                                              │
   │   3. UPDATE                                                  │
   │   ────────                                                   │
   │      Trigger: fact changed, or atom needs refinement         │
   │             ▼                                                │
   │      Edit the SAME file (do NOT create new file)             │
   │             ▼                                                │
   │      Optionally update the description in MEMORY.md          │
   │                                                              │
   │   4. REMOVE                                                  │
   │   ────────                                                   │
   │      Trigger: fact no longer true, or atom outdated          │
   │             ▼                                                │
   │      Delete the .md file                                     │
   │             ▼                                                │
   │      Remove the matching line from MEMORY.md                 │
   │                                                              │
   └──────────────────────────────────────────────────────────────┘
```

## Create — When to Write

Trigger an atom write when:

- You learn something about the user (role, preference, expertise) → `user`
- The user corrects you OR validates an unusual choice → `feedback`
- The user reveals project context not derivable from code (deadline, decision, motivation) → `project`
- The user mentions an external system → `reference`

**Two-step protocol — both steps required:**
1. Write the atom file with full frontmatter and body.
2. Append a line to `MEMORY.md` with the pointer and hook.

**Skipping step 2 is the most common protocol violation.** An atom that isn't indexed is an atom that doesn't exist — it sits orphaned on disk, never loaded, never consulted, contributing nothing.

## Read — When Atoms Load

```
┌──────────────────────────────────┬─────────────────────────────────┐
│  EVENT                           │  WHAT LOADS                     │
├──────────────────────────────────┼─────────────────────────────────┤
│  Every prompt                    │  MEMORY.md index (first 200)    │
│                                  │  All CLAUDE.md files            │
├──────────────────────────────────┼─────────────────────────────────┤
│  Topic surfaces in conversation  │  Relevant atom(s) via Read tool │
├──────────────────────────────────┼─────────────────────────────────┤
│  User asks to recall something   │  Atoms matched to keywords      │
├──────────────────────────────────┼─────────────────────────────────┤
│  Cross-reference in another atom │  Linked atom may be loaded      │
└──────────────────────────────────┴─────────────────────────────────┘
```

Selective loading is the whole reason for the index pattern. If every atom loaded on every prompt, the system would collapse under its own weight at ~30 atoms.

## Update — Edit, Don't Duplicate

When a fact changes, edit the existing atom. Do not write a new atom with similar content. Duplicates create drift; drift creates contradiction; contradiction creates bugs.

**Check before writing:** Is there already an atom on this topic? If yes — update it. If no — write a new one.

**Search patterns to check for duplicates:**
- Filename: grep for similar slugs
- Description: grep MEMORY.md for similar one-liners
- Content: grep atom files for the relevant keyword

## Remove — Delete File AND Index Entry

When an atom is no longer true (the project finished, the preference changed, the reference moved), remove it cleanly:

1. Delete the `.md` file.
2. Remove the matching line from `MEMORY.md`.

**Leaving the file without the index entry:** the file becomes an orphan. Disk waste, audit confusion.

**Leaving the index entry without the file:** the link is broken. Claude tries to load a file that doesn't exist, generates noise.

Both halves of the removal are required.

---

# Part 7: Data Flow — What Loads When

Mechanics of the loading system, event by event.

```
═══════════════════════════════════════════════════════════════════════
  EVENT                          │  WHAT GETS LOADED INTO CONTEXT
═══════════════════════════════════════════════════════════════════════
  EVERY PROMPT                   │  ~/.claude/CLAUDE.md  (global)
                                 │  <project>/CLAUDE.md  (project)
                                 │  MEMORY.md  (index, capped 200 lines)
───────────────────────────────────────────────────────────────────────
  EXPLICIT BOOT COMMAND          │  All of "every prompt", PLUS:
                                 │  <project>/SESSION-DIGEST.md
                                 │  <project>/MEMORY.md  (if exists)
                                 │  <project>/PLAN.md    (if exists)
                                 │  Selected atom files (situational)
───────────────────────────────────────────────────────────────────────
  CUSTOM SKILL INVOCATION        │  ~/.claude/skills/<name>.md
                                 │  + any files the skill references
───────────────────────────────────────────────────────────────────────
  SUBAGENT SPAWN                 │  Subagent gets fresh context
                                 │  + agent definition file
                                 │  + the prompt you pass it
                                 │  (NOT your conversation history)
───────────────────────────────────────────────────────────────────────
  FILE EDIT (Write/Edit tools)   │  Matching .claude/rules/*.md files
                                 │  Secret-scanning hook fires
───────────────────────────────────────────────────────────────────────
  BASH COMMAND                   │  Configured PreToolUse hooks fire
                                 │  (block-git-push, block-rm-rf, etc.)
───────────────────────────────────────────────────────────────────────
  CONTEXT AT ~80% CAPACITY       │  PreCompact hook fires (save state)
                                 │  Auto-compact replaces old messages
                                 │  Memory atoms preserve continuity
───────────────────────────────────────────────────────────────────────
  SESSION END                    │  SessionEnd hook fires
                                 │  Wrap ritual writes digest
═══════════════════════════════════════════════════════════════════════
```

## The Critical Insight: Index Is Always Loaded

`MEMORY.md` is loaded on **every prompt.** That's why the 200-line cap matters so much. Anything in the index is paying a token cost on every single message.

Atoms themselves are loaded only when needed. The index tells Claude *what exists*. The atom contents are fetched only when Claude (or a hook, or a skill) determines the atom is relevant to the current prompt.

This is the same pattern as a database index: small, always-resident, points to the heavyweight content that lives elsewhere.

## Boot vs Mid-Session vs End

```
BOOT (session start)              END (session wrap)
─────────────────                 ──────────────────

Read:                             Execute:
  1. Global CLAUDE.md             1. Synthesize what changed
  2. Project CLAUDE.md            2. Write SESSION-DIGEST.md
  3. MEMORY.md index              3. Update MEMORY.md (new atoms)
  4. Project MEMORY.md            4. Commit if asked
  5. SESSION-DIGEST.md            5. Print checklist
  6. PLAN.md (if exists)
                                  Result:
Then: orient + first action       State persisted, next session
                                  can resume exactly here
                                                                    
MID-SESSION
───────────
                                                                    
On every prompt:                                                    
  · All CLAUDE.md re-read (cached)                                  
  · MEMORY.md index visible                                         
  · Atoms loaded ON-DEMAND when relevant                            
                                                                    
On learning a new fact:                                             
  · Write new atom file                                             
  · Append line to MEMORY.md                                        
                                                                    
On correction:                                                      
  · Update existing atom (NOT new file)                             
  · Or remove if outdated                                           
                                                                    
On context fill (~80%):                                             
  · PreCompact hook flushes state to disk                           
  · Auto-compact summarizes old messages                            
  · Memory atoms preserve continuity                                
```

---

# Part 8: What NOT to Save

The exclusion list is as important as the inclusion list. Over-saving kills signal.

## Hard No-Save List

```
┌────────────────────────────────────────────────────────────────────┐
│                                                                    │
│  DO NOT SAVE:                                                      │
│                                                                    │
│  1. Code patterns, conventions, architecture, file paths           │
│     → Derivable from reading current project state                 │
│                                                                    │
│  2. Git history, recent changes, who-changed-what                  │
│     → `git log` and `git blame` are authoritative                  │
│                                                                    │
│  3. Debugging solutions, fix recipes                               │
│     → The fix is in the code; context is in the commit message     │
│                                                                    │
│  4. Anything already in a CLAUDE.md file                           │
│     → Duplication causes drift                                     │
│                                                                    │
│  5. Ephemeral task details (in-progress state)                     │
│     → Goes in TaskCreate or PLAN.md, not memory                    │
│                                                                    │
│  6. Activity summaries, PR rosters, recent activity                │
│     → Ask: what was SURPRISING? That's the part worth keeping.     │
│                                                                    │
│  7. Secrets, credentials, API keys, tokens                         │
│     → Never. Not even "just temporarily."                          │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

## Why Over-Saving Kills the System

The index has a 200-line cap. Every entry is competing for one of those slots. If you fill the index with "PR #1234 merged on Tuesday" entries, you push out the entries that actually shape behavior.

The mental model: memory is for **non-obvious facts that affect future decisions.** Not for *records of what happened.* Records belong in git, in PRs, in your ticket tracker, in your notes app. Memory is decision-shaping context.

## The "Surprising or Non-Obvious" Test

When you're about to save something, ask:

```
- Is this surprising? (Something a fresh observer wouldn't infer)
- Is this non-obvious? (Not derivable from code/docs/git)
- Will this shape future decisions? (Not just a record)
- Is this stable enough to be worth saving? (Not pure ephemera)
```

If all four are yes → save it.
If any is no → it's noise.

## Hard Case: User Asks You to Save Something Excluded

Sometimes the user will explicitly request a save that falls into the exclusion list. ("Save the PR list." "Remember what we did today.")

The right move is *not* to silently comply or silently refuse — it's to **negotiate**:

> "I can save that — but what was *surprising* or *non-obvious* about it?
> A list of PRs is better tracked in your repo than my memory. If there's
> a specific finding from those PRs that shapes future work, I'll save
> that instead."

Often the user, when prompted, will surface the actual insight (which is worth saving) and let go of the raw roster (which isn't).

---

# Part 9: Stale Protection

Memory atoms are **point-in-time observations**, not live state. This is the single most important nuance in the entire system.

## The Age-Stamp Pattern

When an atom is loaded, the system can annotate it with its age:

```
> "This memory is 32 days old. Memories are point-in-time observations,
>  not live state — claims about code behavior or file:line citations
>  may be outdated. Verify against current code before asserting as fact."
```

Every atom carries this caveat. It's not a flaw — it's a feature. The atom captures what was true when it was written. What's true *now* requires verification.

## The Verify-Before-Recommend Rule

```
┌────────────────────────────────────────────────────────────────────┐
│                                                                    │
│   A memory atom is a CLAIM that something existed when written.    │
│                                                                    │
│   It is NOT a guarantee that it exists NOW.                        │
│                                                                    │
│   Before recommending action based on a memory:                    │
│                                                                    │
│   · If the atom names a FILE PATH      → check file exists         │
│   · If the atom names a FUNCTION       → grep for it               │
│   · If the atom names a FLAG/CONFIG    → read current config       │
│   · If the atom names a SERVICE/URL    → ping it                   │
│   · If the atom names a STATUS         → check current state       │
│                                                                    │
│   "The memory says X exists" is NOT the same as "X exists now."    │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

## When to Trust vs When to Verify

```
TRUST WITHOUT VERIFYING               VERIFY BEFORE ACTING
─────────────────────────             ───────────────────

User identity/role atoms              File path atoms
  (slow-decaying)                       (paths get renamed)

Feedback rules                        Function name atoms
  (preferences are stable)              (refactoring renames)

Reference URLs (well-known)           Project status atoms
  (large systems are stable)            (decay weekly)

Behavioral patterns                   Deadline atoms
  (corrections are durable)             (dates pass)
```

## The Stale Snapshot Failure

The single most common failure mode of any memory system:

```
1. Memory atom written:    "Service X is deployed to staging."
2. Three weeks pass:        Service X is moved to production.
                            Staging is decommissioned.
3. User asks:               "What's the status of service X?"
4. Claude reads atom:       "Service X is deployed to staging."
5. Claude reports:          "Service X is in staging."  ← LIE
```

The atom didn't lie when it was written. It became a lie through the passage of time.

**Fix:** when a project atom is loaded and is more than ~14 days old, treat it as *suggestive but unverified.* Either check the actual state, or qualify the response ("memory says X as of three weeks ago — let me verify").

---

# Part 10: The War Room Pattern

A pattern for cross-project memory when you run multiple projects.

## The Problem

You have memory in Project A. You have memory in Project B. Some facts are *project-specific* (Phase 4 of Project A shipped). Some facts are *cross-cutting* (the user is a senior Go engineer, that's true everywhere).

Without a pattern, cross-cutting facts get duplicated into every project's memory. Then they drift. Then they contradict.

## The Pattern

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│   WAR ROOM (single source of truth for shared facts)         │
│   ~/.claude/projects/<central-slug>/memory/                  │
│     ├── MEMORY.md             ◄── canonical index            │
│     ├── user_role.md                                         │
│     ├── user_handle.md                                       │
│     ├── feedback_terse_responses.md                          │
│     ├── feedback_no_emojis.md                                │
│     └── reference_infra.md                                   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
                       │
                       │ Read-only consultation
                       │ when working in any project
                       ▼
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│   PROJECT A — Own working directory                          │
│   ~/.claude/projects/<project-a-slug>/memory/                │
│     ├── MEMORY.md  (project A's own index)                   │
│     ├── project_phase_4_complete.md                          │
│     ├── project_decision_postgres.md                         │
│     └── project_team_names.md                                │
│                                                              │
│   PROJECT B — Own working directory                          │
│   ~/.claude/projects/<project-b-slug>/memory/                │
│     ├── MEMORY.md  (project B's own index)                   │
│     ├── project_sprint_status.md                             │
│     └── project_blocker_x.md                                 │
│                                                              │
└──────────────────────────────────────────────────────────────┘

Why this design:
· Cross-cutting facts live in ONE place (the war room)
· Project-specific facts stay in the project
· Updates flow one direction: war room is canonical
· Each project session loads its own memory first
· When cross-cutting info is needed, war room is consulted
```

## The Designated War Room

In Claude Code, each working directory has its own memory namespace. To set up a war room:

1. Pick one directory as your strategy hub (often a top-level `.claude/` or similar).
2. Write cross-cutting atoms there (user identity, global feedback, infrastructure).
3. Project working directories have their own memory for project-specific atoms.
4. When working in a project, consult war room atoms by reading from the war room path explicitly when needed.

## Rules

- **War room is read-only from projects.** Project sessions never write to war room atoms; they only read.
- **Updates flow one way.** When a cross-cutting fact changes, update the war room atom directly.
- **Project atoms stay project-scoped.** Don't promote project-specific facts to the war room.
- **No silent duplication.** If a fact would apply across projects, write it once in the war room, not in each project.

## When You Don't Need This Pattern

Single project? Skip the war room. The pattern adds friction without benefit. The war room is for operators running 3+ active projects where cross-cutting facts genuinely matter.

---

# Part 11: Session Lifecycle Integration

Memory is most powerful when it's wired into session start and end rituals.

## Boot Ritual

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│   BOOT — what happens at session start                       │
│                                                              │
│   1. Read MEMORY.md index (always loaded by harness)         │
│   2. Read SESSION-DIGEST.md (last session's handoff)         │
│   3. Read project MEMORY.md NEXT list (if exists)            │
│   4. Reconcile: if DIGEST says "X done" but NEXT says        │
│      "[ ] X" → mark X complete                               │
│   5. Quick health check on anything user manages              │
│      (services, deploys, integrations)                       │
│   6. Verify 2-3 key numbers/states against reality —         │
│      DON'T trust docs alone                                  │
│   7. Present orientation: "Status: X done. Next: Y. Heads-   │
│      up about Z."                                            │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Critical:** Don't load source code at boot. Load *knowledge* (memory files, rules, context docs). Source code loads on-demand when you're actually building. Loading source at boot wastes thousands of tokens before any work begins.

## Wrap Ritual

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│   WRAP — what happens at session end                         │
│                                                              │
│   1. Commit all uncommitted work (if user authorized)        │
│   2. Update project MEMORY.md NEXT list                      │
│      (mark done, add new, remove abandoned)                  │
│   3. Write SESSION-DIGEST.md handoff:                        │
│      · What got done                                         │
│      · Key decisions made                                    │
│      · Current state (numbers, modes, configs)               │
│      · Gotchas / warnings                                    │
│      · NEXT items in priority order                          │
│   4. Update any auto-memory atoms that changed               │
│   5. Spot-check 3 claims from docs against actual files;     │
│      fix any wrong claim in same commit                      │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## SESSION-DIGEST.md Template

```markdown
# Session Digest — [date]

## What Got Done
- [Completed items with actual results/numbers]
- [Each item one line, scannable]

## Key Decisions
- [Decision: chose X over Y]
  **Why:** [The reasoning future-you needs]

## Current State
- [Running services / counts / modes / key numbers]
- [Anything that affects how next session boots]

## Gotchas / Warnings
- [Things that could bite next session if forgotten]

## NEXT (priority order)
- [ ] First thing to do next session
- [ ] Second thing
- [ ] Third thing
```

The digest is the **single most important continuity primitive.** It's what lets Session N+1 begin where Session N ended without forcing you to re-explain everything.

## After Context Compaction

When the context window hits ~80% capacity, Claude Code auto-summarizes old messages to free space. You lose detail. Recovery:

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│   POST-COMPACT recovery                                      │
│                                                              │
│   1. Re-read MEMORY.md index                                 │
│   2. Re-read SESSION-DIGEST.md                               │
│   3. Re-read any project MEMORY.md                           │
│   4. Re-set working directory (Bash resets cwd)              │
│   5. Check for zombie background processes                   │
│   6. Don't rewrite — verify what exists first                │
│   7. Re-read any research referenced pre-compact             │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

The memory atoms exist *precisely so* that compaction is recoverable. Without them, compaction is catastrophic loss. With them, compaction is just "summarize the volatile parts; the persistent parts are on disk."

---

# Part 12: Memory Failure Modes

Every failure mode here has cost someone real time. Each one generates a rule that prevents recurrence.

## Failure 1: The Stale Snapshot

**Pattern:** Atom written, fact changes in the world, atom not updated. Future session loads atom, reports stale fact as current.

**Cost:** Trust killer. Once Claude reports one stale fact as current, every subsequent claim is suspect.

**Prevention:** Age-stamps on load. Verify-before-recommend rule. Project atoms older than ~14 days treated as suggestive, not authoritative.

## Failure 2: The Duplicate Atom

**Pattern:** Same fact written into two atoms. Both atoms drift independently over time. Eventually they contradict.

**Cost:** Claude reads both, has to pick one, may pick wrong. Debugging is hard because both atoms look authoritative.

**Prevention:** Before writing a new atom, grep for similar content. Update existing if found. Use the description field to make duplicates obvious in the index.

## Failure 3: The Orphan File

**Pattern:** Atom file exists but no index entry in MEMORY.md.

**Cost:** Atom is invisible. Disk waste. Confusion during audit.

**Prevention:** Two-step protocol — file + index entry. Periodically reconcile: list files in memory directory, compare to MEMORY.md entries.

## Failure 4: The Orphan Index Entry

**Pattern:** Line in MEMORY.md but the linked file doesn't exist.

**Cost:** Broken link. Claude tries to load file, gets error noise.

**Prevention:** When deleting an atom file, immediately delete the index entry. Same commit.

## Failure 5: The Hallucinated Recall

**Pattern:** Claude "remembers" something that was never written to an atom — just makes it up from training intuition.

**Cost:** Worse than no memory. Confidently wrong > obviously absent.

**Prevention:** Train the discipline: "If you don't see it in MEMORY.md or an atom, you don't know it from memory. Verify or ask."

## Failure 6: The Index Bloat

**Pattern:** MEMORY.md grows past 200 lines. Entries beyond 200 are silently truncated. Whole topics become invisible.

**Cost:** Worst-of-both-worlds — the atoms exist, but Claude doesn't know they exist. The system *seems* to be working but is silently incomplete.

**Prevention:** Prune aggressively. Combine related entries. Archive completed-project atoms. Hard rule: when you hit 180 lines, prune before adding more.

## Failure 7: The PII / Secret Leak

**Pattern:** An atom captures something sensitive — a credential, an internal-only person's name, a confidential business detail. The memory directory gets backed up, shared, or pushed to a remote.

**Cost:** Real-world security incident. Trust violation. Possibly legal exposure.

**Prevention:**
- Hooks that scan atom writes for secret patterns (API keys, private keys, credential patterns).
- Hard rule: memory directories never go to public Git.
- Periodic audit: grep memory directory for known-sensitive patterns.
- If sharing memory artifacts, sanitize first or use a clean-room export.

## Failure 8: The Just-in-Case Bloat

**Pattern:** Operator saves everything that *might* be useful "just in case." Memory fills with low-signal entries. The few high-signal entries get lost in the noise.

**Cost:** Index bloat. Decision fatigue when reading. Reduced effective recall.

**Prevention:** Apply the "surprising or non-obvious" test before every save. If you can't articulate why it's worth saving, it isn't.

## Failure 9: The Reverse-Engineering Risk

**Pattern:** Atoms accumulate detailed history of strategic decisions, personnel, competitive intel, customer-specific notes. Anyone with read access to the memory directory can reverse-engineer the operator's full operating context.

**Cost:** If memory is shared or compromised, the leak is far worse than any single document. The aggregate paints a complete picture.

**Prevention:** Treat the memory directory as classified data. Never share raw. If you want to share patterns, share a sanitized template (this document is an example). Encrypt at rest if local laptop is high-risk.

## Failure 10: The Conflicting Atoms

**Pattern:** Two atoms make contradictory claims. Both pass age-stamp checks. Claude has to pick — or worse, conflates them.

**Cost:** Confusion. Wrong recommendations. The user has to debug why the AI keeps flip-flopping.

**Prevention:**
- When updating an atom that contradicts another, update both.
- Cross-link atoms with `[[name]]` references so conflicts are visible.
- Periodic audit: scan atoms for conflicting claims on same topic.

## The Master Anti-Pattern Table

| Failure | Symptom | Prevention |
|---------|---------|------------|
| Stale Snapshot | Reports old fact as current | Age-stamps + verify-before-recommend |
| Duplicate Atom | Same fact in two files | Grep before write, update instead |
| Orphan File | Atom exists, not indexed | Two-step protocol, periodic audit |
| Orphan Index | Link exists, file doesn't | Same-commit delete |
| Hallucinated Recall | Confident fact never written | "If not in atoms, don't claim memory" |
| Index Bloat | >200 lines, silent truncation | Hard prune at 180 lines |
| PII / Secret Leak | Sensitive data on disk | Scan hooks, never public Git |
| Just-in-Case Bloat | Index full of low-signal | "Surprising/non-obvious" test |
| Reverse-Engineering Risk | Aggregate leaks strategy | Sanitize before sharing |
| Conflicting Atoms | Two atoms contradict | Cross-link, periodic conflict audit |

## Measurement: How Do You Know This Works?

A memory system without measurement is just a hope. These are the metrics worth tracking:

**Health metrics (run monthly):**
- Atom count by type (user / feedback / project / reference)
- Atoms touched in last 30 / 60 / 90 days (decay tracking)
- Index line count (alert if >180)
- Orphan count (atoms not indexed; index entries without files)
- Average atom age in days

**Quality metrics (run quarterly):**
- False-recall incidents per quarter (Claude cited an atom incorrectly)
- Stale-snapshot incidents (atom was outdated, caused wrong recommendation)
- Lessons-added-this-quarter (failure modes captured as `lesson_*` atoms)
- Atoms-removed (active pruning is a sign of discipline, not loss)

**Outcome metrics (run yearly):**
- Time-to-orient on new session (minutes from boot to first useful action)
- Re-explanation rate (how often you have to re-explain things memory should have captured)
- Handoff feasibility (could another operator pick up your work using only your memory?)

These metrics don't need automation to start — periodic manual review with a notebook is enough. The point is: measure, don't assume. A system you can't audit is a system you can't trust.

---

# Part 13: Hooks for Memory Discipline

Text rules get violated. Hooks don't. If memory hygiene matters, enforce it with shell-level interception.

## How Hooks Work

Hooks are shell commands registered in `.claude/settings.json` under the `hooks` key. They run at specific events (PreToolUse, PostToolUse, SessionStart, etc.) and can either pass (`exit 0`), warn (`exit 1`), or hard-block (`exit 2`).

```json
{
  "hooks": {
    "EventName": [
      {
        "matcher": "ToolName",
        "command": "bash -c '...'"
      }
    ]
  }
}
```

## Event Types Relevant to Memory

| Event | Use For Memory Discipline |
|-------|--------------------------|
| `PreToolUse` | Block sensitive content writes to memory |
| `PostToolUse` | Auto-format memory files |
| `SessionStart` | Boot ritual, integrity check |
| `SessionEnd` | Wrap ritual, digest write |
| `PreCompact` | Flush volatile state to disk before compact |
| `PostCompact` | Recovery — re-load memory |

## Hook 1: Block Secret Patterns in Memory Writes

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "command": "bash -c 'PATH_ARG=$(echo \"$TOOL_INPUT\" | grep -oP \"file_path\\\":\\s*\\\"\\K[^\\\"]+\"); echo \"$PATH_ARG\" | grep -qE \"/memory/.*\\.md$\" || exit 0; echo \"$TOOL_INPUT\" | grep -qiE \"(sk-[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{36}|PRIVATE.KEY|BEGIN RSA|-----BEGIN)\" && echo \"BLOCKED: possible secret in memory write\" && exit 2 || exit 0'"
      }
    ]
  }
}
```

This hook fires on every Write or Edit. If the target is a memory file AND the content matches secret patterns, it hard-blocks the write.

## Hook 2: PreCompact State Flush

```bash
#!/bin/bash
# .claude/hooks/precompact-save.sh
# Fires before Claude Code auto-compacts context.
# Ensures volatile state is persisted to memory before summarization.

set -e

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Append a compact marker to session digest
cat >> "$PROJECT_DIR/SESSION-DIGEST.md" <<EOF

## Compact at $TIMESTAMP
- Context was auto-compacted during session.
- Post-compact: re-read MEMORY.md and any active atoms.
EOF

exit 0
```

Registered:

```json
{
  "hooks": {
    "PreCompact": [
      {
        "matcher": "",
        "command": "bash $CLAUDE_PROJECT_DIR/.claude/hooks/precompact-save.sh"
      }
    ]
  }
}
```

## Hook 3: SessionEnd Digest Reminder

```bash
#!/bin/bash
# .claude/hooks/session-end-digest.sh
# Warns if SESSION-DIGEST.md wasn't updated this session.

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
DIGEST="$PROJECT_DIR/SESSION-DIGEST.md"
SESSION_START=$(date -d '4 hours ago' +%s)

if [ -f "$DIGEST" ]; then
  DIGEST_MTIME=$(stat -c %Y "$DIGEST" 2>/dev/null || stat -f %m "$DIGEST")
  if [ "$DIGEST_MTIME" -lt "$SESSION_START" ]; then
    echo "WARNING: SESSION-DIGEST.md not updated this session. Consider running wrap ritual."
  fi
fi

exit 0
```

## Hook 4: Memory Integrity Check on Boot

```bash
#!/bin/bash
# .claude/hooks/session-start-integrity.sh
# Checks for orphan files and orphan index entries on session start.

MEMORY_DIR="$HOME/.claude/projects/${PROJECT_SLUG}/memory"
INDEX="$MEMORY_DIR/MEMORY.md"

if [ ! -f "$INDEX" ]; then
  exit 0
fi

# Files referenced in index that don't exist
MISSING=$(grep -oP '\(\K[^)]+\.md' "$INDEX" | while read f; do
  [ -f "$MEMORY_DIR/$f" ] || echo "$f"
done)

if [ -n "$MISSING" ]; then
  echo "WARNING: MEMORY.md references missing files:"
  echo "$MISSING"
fi

# Files in memory dir that aren't in the index
ORPHANS=$(find "$MEMORY_DIR" -name "*.md" -not -name "MEMORY.md" -printf "%f\n" | while read f; do
  grep -q "($f)" "$INDEX" || echo "$f"
done)

if [ -n "$ORPHANS" ]; then
  echo "WARNING: Memory files not indexed in MEMORY.md:"
  echo "$ORPHANS"
fi

exit 0
```

## Hook 5: Block Memory Push to Public Remote

```bash
#!/bin/bash
# .claude/hooks/block-memory-push.sh
# Prevents accidentally pushing memory directory to a public remote.

INPUT="$TOOL_INPUT"

# If the command is a git push
echo "$INPUT" | grep -qiE "git\s+push" || exit 0

# Check if any pending commit touches the memory directory
cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || exit 0

git diff --cached --name-only 2>/dev/null | grep -qE "memory/.*\.md$" && {
  echo "BLOCKED: Push includes memory files. Memory directories should not be pushed."
  echo "If intentional, set MEMORY_PUSH_OK=1 and retry."
  [ -z "$MEMORY_PUSH_OK" ] && exit 2
}

exit 0
```

## The Enforcement Hierarchy

```
STRUCTURAL ENFORCEMENT    ← Hooks that exit 2 — physically impossible to violate
   ↑ most reliable
AUTOMATED CHECKS          ← Hooks that exit 1 — warn, but allow
   ↑
CHECKLISTS                ← Boot/wrap rituals followed every time
   ↑
TEXT RULES                ← Written guidelines (high violation rate)
   ↑ least reliable
VERBAL PROMISES           ← "I'll remember to..." (~0% enforcement)
```

For anything that genuinely matters (secret leaks, push safety, integrity), use the highest level possible. A `exit 2` hook is worth ten paragraphs of well-meaning rules.

---

# Part 14: Quick Start

Four levels, from "anyone can do this in 5 minutes" to "operator running a multi-project memory empire."

## Level 1: Minimal (5 minutes)

Just create one file. That's it.

Create `~/.claude/projects/<your-project-slug>/memory/MEMORY.md`:

```markdown
- [User role](user_role.md) — Senior backend engineer, 8 yrs Go, new to React
- [No mocks](feedback_no_mocks.md) — Integration tests must hit real DB
- [Sprint deadline](project_sprint.md) — v2 launch 2026-03-15
```

Then write the three referenced atoms in the same directory. Each file is ~10 lines.

That's a working memory system. Claude reads MEMORY.md every prompt. When you mention testing, the no-mocks rule applies. When you mention the sprint, the deadline comes up. Day-one productivity.

## Level 2: Standard (30 minutes)

Add to Level 1:

**1. The four-type discipline.** Write your first atom in each type. User, feedback, project, reference. Get the rhythm.

**2. Frontmatter on every atom:**

```markdown
---
name: descriptive-slug
description: One-line hook that survives in the index
metadata:
  type: user | feedback | project | reference
---

Body content here.
```

**3. SESSION-DIGEST.md** at project root:

```markdown
# Session Digest

## What Got Done
- ...

## Current State
- ...

## NEXT
- [ ] ...
```

**4. Boot and wrap rituals.** Start every session by reading MEMORY.md + SESSION-DIGEST. End every session by updating both.

## Level 3: Full Power (2 hours)

Add to Level 2:

**1. Hook suite** in `.claude/settings.json`:
- `block-git-push` — explicit approval required for push
- `scan-secrets` — block any write containing secret patterns
- `precompact-save` — flush state before compaction
- `session-end-digest` — warn if digest stale at end of session

**2. Memory integrity check** on boot — catches orphans and missing files.

**3. Cross-link discipline** — every atom links to related atoms via `[[slug]]`. Knowledge graph emerges.

**4. Periodic prune** — once a week, walk the index, remove stale project atoms, combine related atoms, ensure under 180 lines.

**5. Atom naming convention** — `<type>_<topic>.md` so filenames cluster naturally (`user_*`, `feedback_*`, `project_*`, `reference_*`).

**6. Custom skills** that interact with memory:
- `/boot` — orient, read digest, present status
- `/wrap` — commit, update digest, prune memory
- `/status` — quick dashboard from memory state

## Level 4: Godmode (one-time setup, ongoing discipline)

Everything above, plus:

**1. War Room pattern** — central directory for cross-cutting atoms, per-project directories for project-specific.

**2. Atom-write hooks** — secret scanning on every write to memory files.

**3. Sanitized share template** — a clean export pipeline so you can share *the pattern* without leaking *the data*.

**4. Encrypted-at-rest** memory directory if your laptop is high-risk.

**5. Periodic conflict audit** — script that scans atoms for contradicting claims and surfaces them for review.

**6. Memory metrics** — periodic count of atoms by type, atoms touched in last 30 days, atoms older than 90 days. Use to drive pruning.

**7. Backup strategy** — memory is high-value, low-volume. Daily sync to a secure remote (your own server, encrypted bucket). Versioned so you can recover from accidental deletion.

**8. Operating model documented** — a doc like this one, written for *your* setup, so handoff or onboarding is one URL.

---

## Final Words

This system works because it's simple.

Plain markdown files. One fact per file. An index that points at them. Hooks that enforce discipline. Rituals that integrate with session lifecycle.

No vector database. No fine-tuned model. No black box.

The discipline is the strategy. The mechanics are the proof.

```
┌────────────────────────────────────────────────┐
│                                                 │
│   The meta-principle:                           │
│                                                 │
│   Memory is versioned, auditable, reproducible. │
│                                                 │
│   Versioned: every change is explicit.          │
│   Auditable: everything is plain text.          │
│   Reproducible: same memory + same prompt =     │
│                 same execution.                 │
│                                                 │
│   Operating model is not a slogan.              │
│   The mechanics live in the files you can       │
│   open in any editor right now.                 │
│                                                 │
└────────────────────────────────────────────────┘
```

A goldfish forgets everything in fifteen seconds. A colleague remembers what mattered, forgets what didn't, and can hand off cleanly to the next person.

Choose which one you're building.

---

*Adapted from production use across multiple long-running projects in different domains.*
*Every pattern earned the hard way. Every failure mode catalogued so the next operator doesn't have to discover it firsthand.*
*Drop this in your Claude Code setup and stop teaching a goldfish.*
