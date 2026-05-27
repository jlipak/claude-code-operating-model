# The Ezekiel Kit — Claude Code Godmode

> A complete operating system for Claude Code, forged from 1,000+ sessions of failure and triumph.
> Every rule backed by evidence. Every pattern earned the hard way. Every failure catalogued so you don't repeat it.

> *"Son of man, I have made you a watchman for the house of Israel."* — Ezekiel 3:17

---

## The Story — Why This Exists

This system was born from the ashes of a predecessor called SHIKA.

SHIKA ran for **968 sessions** over 3 months. 9,997 messages. 3,110 victories. **1,614 frustrations.** It started as a simple AI-powered system, grew into a custom MCP server with ChromaDB RAG memory, 36 validation gates, Docker + Coolify deployment, and layers upon layers of "just one more safety check."

It ended on **Session 777** — a 7-minute session where nothing executed. The system was so over-engineered that it couldn't do basic tasks. Total rot.

The creator walked away.

Two weeks later, he came back with a different philosophy: **simplicity is the strategy.**

No SHIKA code was reused. No Docker. No custom frameworks. Just native Claude Code, a CLAUDE.md file, and 10 hard rules distilled from 968 sessions of evidence. The new system — Ezekiel — went from zero to a deployed trading bot in 5 sessions over 2 days, then pivoted to a weather arbitrage strategy that achieved **97.1% win rate over 4,261 historical trades** within 2 weeks.

The difference? SHIKA had 4,977 lines of code at 46% win rate. Ezekiel had 636 lines at 96.4%.

**This document is everything we learned.** Drop it into your Claude Code setup and skip the 968 sessions of pain.

---

## Table of Contents

1. [Part 1: The 10 Holy Rules](#part-1-the-10-holy-rules)
2. [Part 2: The Failure Database](#part-2-the-failure-database)
3. [Part 3: The System Architecture](#part-3-the-system-architecture)
4. [Part 4: Identity & Communication](#part-4-identity--communication)
5. [Part 5: Behavioral Law](#part-5-behavioral-law)
6. [Part 6: Operational Checklists](#part-6-operational-checklists)
7. [Part 7: The Memory System](#part-7-the-memory-system)
8. [Part 8: Hooks & Structural Enforcement](#part-8-hooks--structural-enforcement)
9. [Part 9: Agent Orchestration](#part-9-agent-orchestration)
10. [Part 10: Session Lifecycle](#part-10-session-lifecycle)
11. [Part 11: Prompt Engineering Deep Dive](#part-11-prompt-engineering-deep-dive)
12. [Part 12: Meta-Patterns](#part-12-meta-patterns)
13. [Part 13: The Anti-Complexity Bible](#part-13-the-anti-complexity-bible)
14. [Part 14: Quick Start](#part-14-quick-start)

---

# Part 1: The 10 Holy Rules

Distilled from 968 sessions, 9,997 messages, 3,110 victories, 1,614 frustrations.
Every rule is the **inverse of a proven failure mode.** Every rule has hundreds of data points backing it.

```
Trust = (Consistent Results x Speed) / (Errors x Scope Creep)
```

---

### I. COMMIT AFTER EVERY WIN
**Evidence: 1,524 save requests (#1 across all sessions), 546 lost_work frustrations**

Context dies without warning. Compaction eats in-progress work. API errors kill sessions mid-thought. Commits survive everything.

- Stage specific files, never `git add -A` (prevents committing garbage)
- Descriptive messages (future you needs to understand)
- One concern per commit (makes rollback safe)
- After every meaningful change — not just at the end

**The cost of not doing this:** Session S16 lost 3 hours of infrastructure work to a compaction event. Session S609 lost a complete refactor. These happened *hundreds* of times in SHIKA.

---

### II. READ BEFORE WRITE
**Evidence: 422 wrong_output events, 215 read_first requests**

Never hallucinate file contents, paths, or APIs. This is the #1 cause of wasted time:

| What you're touching | What to do FIRST |
|---------------------|------------------|
| File path | Glob to verify it exists |
| Function/class | Grep to verify it exists |
| Library API | Official docs or context7 lookup |
| CLI flag | `--help` first |
| Config setting | Read the config file |
| External API | `curl` it and count the actual fields |
| SDK method | Check the actual SDK types (not a tutorial) |

**Zero tolerance.** Not "when in doubt" — ALWAYS on first use. A 2-minute check prevents 2 hours of debugging.

**The cost of not doing this:** Session S23: ICON weather API documentation said 40 ensemble members. Reality: 39. Parser broke silently for hours. A single `curl` command would have caught it in 10 seconds.

---

### III. NEVER REWRITE — ALWAYS PATCH
**Evidence: 544 rewrite anti-pattern occurrences (most destructive single pattern)**

Rewrites silently drop accumulated bug fixes. This is the most expensive mistake in the entire dataset.

The catastrophe: A v3 rewrite broke resolution logic that had been working for 30+ sessions. It dropped 35+ bug fixes that were embedded in the v2 code — edge cases, workarounds, one-liner patches that each fixed a specific production bug. The rewrite looked "cleaner" but was functionally broken.

- Patch what exists
- Read the git log before touching old code — understand what you're preserving
- If a function looks messy, it's probably messy for a reason (accumulated fixes)
- Only rewrite when explicitly asked, and even then, catalog every fix in the old code first

---

### IV. VERIFY BEFORE "DONE"
**Evidence: 315 verify requests, 282 make_sure requests**

Never say "done", "should work", or "that should fix it." These phrases are lies.

- Run the tests. Read the output. Don't assume green
- If it touches a server: SSH in and verify directly
- If it shows data: verify ONE number end-to-end against the real source
- If it's a config change: check that the actual system behavior changed
- If it's a deployment: spot-check a critical log line after restart

"Verified" or "not done." Nothing between.

**The cost:** Session S25: A spread gate was "deployed" but the default value was 0.0 — effectively dead code. It was "done" according to the commit. The feature didn't actually work for 3 sessions. Session S30: "all systems healthy" but the order book showed 0/8 orders filled. The bot was tracking ghost positions.

---

### V. THREE STRIKES, NEW APPROACH
**Evidence: 632 repetition frustrations (#2 overall), 47 rabbit holes**

Same approach fails three times? **FULL STOP.** Change strategy entirely.

- Don't brute force
- Don't blind retry
- Don't "try one more thing" on the same path
- Diagnose root cause or propose a completely different approach

**The cost:** Sessions S609-S613: zero deployments across FIVE sessions — just audit rounds trying the same approach. Sessions S807-S810: four sessions trying to fix a custom MCP server that should have been deleted.

---

### VI. DO EXACTLY WHAT WAS ASKED
**Evidence: 12 explicit scope complaints, but every rewrite traces back to scope creep**

Asked for X? Build X. Not X + Y + "while we're at it."

- No bonus features
- No "improvements" to surrounding code
- No refactoring adjacent functions
- No adding comments/docs to code you didn't change
- "Just check" means READ, not MODIFY

**The cost:** SHIKA's codebase grew from 636 lines to 4,977 lines — not because more features were needed, but because every session added "just one more thing." Each addition was individually reasonable. Collectively, they killed the system.

---

### VII. KEEP IT SIMPLE
**Evidence: 94 over-engineer, 188 bloat, 77 unnecessary occurrences. The SHIKA collapse.**

636 lines at 96.4% WR beat 4,977 lines at 46% WR. This is **proven, not theoretical.**

| Simple | Complex |
|--------|---------|
| Config change | Code rewrite |
| Native tools | Custom frameworks |
| 3 similar lines | Premature abstraction |
| 1 file | 7 files |
| systemd + binary + .env | Docker + Coolify + CI/CD |
| 10 rules + hooks | 36 validation gates |
| SQLite | ChromaDB with CUDA |

If complexity is creeping in: **STOP.** Ask "is this solving a real problem that already happened, or is it 'just in case'?" If just in case → don't build it.

**The creator's own words:** *"I honestly think at this point we overengineered our custom Claude setup."* — said at Session ~800, two months into SHIKA's decline.

---

### VIII. PROTECT THE CONTEXT
**Evidence: 524 compaction events, 530 context_limit frustrations (1,054 combined)**

The context window is finite and precious. Every token wasted is a token not available for actual work.

- Heavy research → subagent (gets its own fresh 200K window)
- Large files → read with line offsets, not full dump
- Parallel tool calls whenever possible (speed + fewer round trips)
- Save progress before potential compaction (commit!)
- After compaction: re-read memory, check for zombie background processes
- Don't load source code at boot — load knowledge/context files; load source when building

**The cost:** Session S16 of SHIKA: 67MB of context, 8 hours 37 minutes, 23 compactions. Most of the session was spent recovering from compactions, not doing actual work.

---

### IX. ZERO RED ERRORS
**Evidence: 57 red_errors events, but outsized emotional impact**

Red error output in the terminal is the #1 visual trigger for frustration. It signals "things are broken" even when they're not.

- Suppress safe errors with `2>/dev/null`
- Test commands silently before running visibly
- Wrap commands that might fail in conditional checks (`|| true`)
- Never let raw tracebacks show in the terminal
- SSH commands: ALWAYS append `|| true` AND `2>/dev/null`
- Python over SSH: ALWAYS wrap in `try/except` with clean error output

```bash
# BAD — grep exit code 1 on no matches = red error
ssh server 'grep -c "pattern" file'

# GOOD — neutralized
ssh server 'grep -c "pattern" file || true' 2>/dev/null
```

**The creator's words:** *"SHIKA HAD MILLION RED ERRORS I HATE IT"*

---

### X. PRESENT BEAUTIFULLY
**Evidence: 26 visual_output requests, every "love it" tied to visual output**

Humans are visual. Output must be scannable at a glance.

- ASCII boxes, tables, structured formatting
- Show outcomes, not internals
- Max 2-3 options with one clear recommendation
- Lead with action, explain after
- No walls of text — if it takes a paragraph, use a table
- Lead with the core finding first, then what dilutes it
- Diagrams > paragraphs for architecture and flow

```
┌─────────────────────────────────────┐
│  DASHBOARD — System Health          │
├──────────┬──────────┬───────────────┤
│ Service  │ Status   │ Key Metric    │
├──────────┼──────────┼───────────────┤
│ Bot A    │ ACTIVE   │ 23 positions  │
│ Bot B    │ ACTIVE   │ Range regime  │
│ VPS      │ HEALTHY  │ 42 days up    │
└──────────┴──────────┴───────────────┘
```

---

# Part 2: The Failure Database

Every entry cost real time, real money, or real trust. Organized chronologically across 90+ days.

## Era 1: SHIKA (Dec 2025 — Feb 2026) — 968 Sessions

### The Architecture That Killed Itself

| What Was Built | What Happened | Lesson |
|---------------|---------------|--------|
| ChromaDB RAG memory | CUDA segfaults, file locks, data corruption | Use simple, proven storage (SQLite) |
| Custom MCP server | Called "cancer in our system" at S807 | Use native tools, not custom infrastructure |
| 36 validation gates | 4 gates to edit 1 file. Nothing shipped | Rules need to be few and enforced, not many and ignored |
| WARN-level hooks | 86% violation rate — universally ignored | Only BLOCK-level hooks work (exit 2) |
| Docker + Coolify | Added complexity with zero benefit | systemd + binary + .env. Always |
| LIVE_STATE.json as truth | Local cache drifted from VPS reality | Verify the system, not the document |
| Paper labeled as live | Trust killer. Reported fake profits | Never lie about mode |
| "Sorry won't happen again" | Said 100s of times, never backed by fix | Structural fix or it doesn't count |

### The Timeline of Collapse

```
Dec 2025: ORIGIN — works great, simple, fast
   ↓ add ChromaDB, MCP, Tkinter dashboard
Dec 12: First friction — compaction cascades, file locks
   ↓ add more safety checks
Dec 16: 12 protocol violations in ONE session
   ↓ add more validation gates
Dec 25: System claims 85/100 health. Actual: 72/100
   ↓ add more monitoring
Jan 2026: Fleet launch $29,300 — only 25% functional
   ↓ add more frameworks
Feb 4-9: Brief profitable period (+$70, 63.3% WR)
   ↓ add Rust rewrite, more complexity
Feb 24: Session 777 — 7 minutes, nothing executes
   ↓ THE END
```

**The pattern:** Every fix added complexity. Complexity caused new failures. New failures demanded new fixes. Repeat until system collapse. This is the **complexity death spiral** and it's the most important thing in this entire document.

### What SHIKA Proved Works

Despite the collapse, some patterns survived and became foundational:

1. **BLOCK-level hooks** (not WARN) — the only behavioral enforcement that works
2. **Factory methodology** — plan → build → test → ship in tight cycles
3. **DOWN-only betting** (96.4% WR) — the "Golden Formula" that survived into Ezekiel
4. **Intel-first-then-build** — 18 research rounds before code = 82.9% WR
5. **Agent swarms** — 10+ parallel agents for research (creator called it "best thing I saw so far")
6. **SQLite** — replaced ChromaDB, never failed once

---

## Era 2: Ezekiel (Mar 2026 — Present) — 35+ Sessions

### Session-by-Session Failure Log

Every failure that happened after the rebuild — each one generated a rule that prevented recurrence.

---

#### S5-S6: First Overnight (-$1,071)

**What:** Trading bot deployed with 3 assets (BTC/ETH/SOL), 10x leverage. All 3 trades hit stop loss overnight. Circuit breaker fired correctly at -10.71%.

**Root cause:** Strategy was designed for ranging markets but deployed into a trending market. OFI signal was contemporaneous (not predictive). Multi-asset diluted the only profitable coin (ETH).

**Lessons:**
- Per-asset backtest analysis reveals hidden poison (BTC was alpha-negative)
- Removing a "smart" indicator (OFI) **added** +16pp win rate — indicators can destroy edge
- Circuit breakers WORK — design them, trust them

---

#### S10: The Filter Graveyard

**What:** Built and backtested 5 "improvement" filters. ALL destroyed value:

| Filter | Effect | Why It Failed |
|--------|--------|---------------|
| 4H EMA gate | Killed 13 winners, 9 losers. -$1,838 | Too slow for 15m ETH trading |
| ADX/DMI | Killed 6W/0L at threshold 25 | Confirms trends AFTER best entries |
| Partial TP | WR up 50→62% but return tanks 21→6% | Double taker fees on Hyperliquid |
| Chandelier stop | Best case: Sharpe 2.41 vs baseline 2.60 | ETH pullbacks clip trailing stops |
| Conviction sizing | Sharpe 2.22 vs 2.23 | Just a leverage multiplier, not alpha |

**Meta-lesson:** Edge comes from catching trends EARLY. Any filter that waits for "more confirmation" removes the best entries. Only crowd-detection and temporal filters add value.

---

#### S21: Silent API Failure

**What:** ECMWF weather API silently broke. Returned errors instead of forecasts. Bot continued running with partial data for **days** without anyone noticing.

**Root cause:** API call was non-fatal — error was caught and the bot continued with fewer models. No smoke test, no alerting, no health check.

**Rule created:** FIX → HARDEN → DOCUMENT, same turn. When you find a silent failure: fix the bug, add a smoke test that catches it, update the gotchas doc. All three in one turn. No "I'll add the test later."

---

#### S23: "Docs Say 40 Members"

**What:** ICON weather API documentation (and every agent that researched it) said 40 ensemble members. Parser was written for 40. Reality: **39 members.** Silent `None` returns for hours.

**Root cause:** Trusted documentation instead of verifying with a live API call.

**Rule created:** `curl` every new API BEFORE writing the parser. Count actual fields in the response. A 2-minute test prevents weeks of silent failure. **Never trust docs, agents, or tutorials for exact field counts.**

---

#### S25: Dead Code Deployment

**What:** Spread gate filter was "deployed" with a default value of 0.0. Since the gate checked `if spread > threshold`, and threshold was 0.0, it fired on literally everything — but then the gate was bypassed because 0.0 meant "disabled." Net effect: the entire feature was dead code.

**Root cause:** Deployed without testing one real input through the full path.

**Rule created:** "Done" means you traced ONE REAL EXAMPLE through the entire code path. Not "the code looks right" — actually run a case and verify the output.

---

#### S27: World-Readable Secrets

**What:** `.env` file on VPS was `chmod 644` (world-readable) instead of `600` (owner-only). Any user on the server could read API keys and private keys.

**Root cause:** Default file permissions on upload. No security check in deployment process.

**Rule created:** VPS security audit checklist runs every boot. `.env` permissions, SSH config, firewall, fail2ban, no suspicious logins. Every deployment checks file permissions.

---

#### S29: Live Production ($5 + 3 Hours)

First real-money deployment. Cost $5 in losses + 3 hours debugging. Generated 5 critical lessons:

**1. "Almost disabled" ≠ disabled**
YES trades were "disabled" by setting `yes_min_forecast_prob=0.99`. But a probability of exactly 1.00 passed the check. Real money lost on a YES trade that should have been impossible.

**Fix:** Use MATHEMATICALLY IMPOSSIBLE values to hard-disable: 1.01 for probability (can never be > 1.0), -1 for non-negative values. "Almost never" is NOT "never."

**2. Ground truth exceeded threshold = HARD KILL**
Weather station showed 71°F vs a 59°F threshold. The system "nudged" the edge by -0.08 instead of killing the trade. A 12°F exceedance should be a guaranteed kill, not a nudge.

**Fix:** When observation exceeds threshold by >5°, return -1.0 (guaranteed kill). Don't nudge — kill.

**3. SDK types are NOT dicts**
Passed `options={"tick_size": x}` but SDK expected `PartialCreateOrderOptions(tick_size=x)`. Python dicts and SDK objects look similar but are fundamentally different. SDK does `.tick_size` attribute access, not `["tick_size"]` dict access.

**Fix:** Always use EXACT library types. Copy from docs verbatim. Never use dict shortcuts for SDK objects.

**4. Grep ALL call sites before patching**
Patched `execute_paper_trade()` but the calling code had `if mode == "paper"` guard — it never called the patched function in live mode. The patch was invisible.

**Fix:** ALWAYS `grep` every call site before monkey-patching. Understand the full call chain.

**5. Secrets hardcoded despite having a rule against it**
Discord webhook URL was hardcoded as a default fallback in source code. The rule against this already existed. Speed was the excuse.

**Fix:** Rules without enforcement don't work. Empty string default + env var. ALWAYS. No exceptions for speed.

---

#### S30: Boot Hallucination Crisis

The session that generated the most rules. Claude loaded stale documentation and presented it as current reality. Trust crisis — the user had SHIKA flashbacks.

**7 Meta-Patterns discovered:**

**META-1: Verify SYSTEMS not DOCUMENTS**
Checked the config file and said "all healthy." But the actual CLOB order book showed 0/8 orders filled. Ghost positions everywhere.

**Rule:** After ANY deployment or audit, verify ACTUAL SYSTEM STATE. Check real orders/fills, check real logs, check real responses. NEVER report "healthy" from a doc read alone.

**META-2: Re-read your own rules before coding in the same domain**
Wrote a rule in Session 29: "SDK types are NOT dicts." In Session 30: wrote `book.get("asks")` on an SDK object — the exact same mistake.

**Rule:** Before writing ANY code for a previously-used SDK/API, re-read your own notes about it. 10 seconds prevents 2 hours.

**META-3: Parse instructions LITERALLY**
User said "2 is open, 1 I cancel." AI deleted position 2 (which was OPEN, as stated). Should have parsed: "2 are open" + "1 was cancelled" = don't touch the open ones.

**Rule:** When the user states a fact, parse it LITERALLY. Don't add interpretation. Don't add context. Parse. The. Words.

**META-4: Clean up when done**
6 idle agent processes left consuming resources. User had to point it out.

**Rule:** When agents/processes/teams finish, clean up IMMEDIATELY. Housekeeping is part of the task.

**META-5: "Done" requires end-to-end proof**
"All systems healthy" without checking if orders actually fill. "YES disabled" without testing a 1.00 probability case. "Spread gate deployed" without checking the default value.

**Rule:** "Done" means you traced ONE REAL EXAMPLE through the ENTIRE path. System behavior is proof. Words on screen are not.

**META-6: SESSION-DIGEST wins over stale docs**
SESSION-DIGEST (written at end of session) said "YES leak fixed." MEMORY.md NEXT list (written earlier) said "[ ] FIX: YES leak." AI reported the stale version.

**Rule:** When two sources conflict, the most recent write wins. Reconcile stale lists against the latest digest before presenting.

**META-7: Stale docs are hallucinations with extra steps**
CLAUDE.md said "PAPER MODE ONLY" and "15 cities" when reality was LIVE mode and 18 cities. Bot loaded the file and parroted it without checking.

**Rule:** Reporting a wrong number from a doc is the SAME failure as making one up. If you report it, you verified it THIS SESSION.

---

#### S31: CLOB Liquidity ($0 + 24 Hours Dead)

**What:** Weather market CLOB order books have ZERO liquidity at fair value. Model says YES=36%, but the order book has bids at $0.01 and asks at $0.97. 96-cent bid-ask spread. Paper trading at model midpoint was fiction — those prices don't exist in the real book.

**Lessons:**

1. **Always `curl` the actual order book** before assuming an execution model
2. **FOK (fill or kill) requires existing asks. GTC (good till cancel) creates liquidity.** FOK on thin books = 0 fills. GTC rests as a standing offer. Whales use GTC
3. **Never change execution mode without checking order book state first**
4. **`round(shares)` can exceed dollar budget** — `round(5.05, 1) = 5.1 → $5.05 > $5.00 cap`. Always use `math.floor` for share sizing
5. **"Below" markets are correctly priced** — the obvious bucket (e.g., "31°F or below") has NO~99.6% and the market KNOWS it. Alpha lives in exact markets where ground truth gives an information edge

---

#### S33: Burning API Credits on Nothing

**What:** Sports strategy module was polling Pinnacle API every hour for NBA game odds. Polymarket had ZERO game-specific sports markets — only season-long markets (Finals, MVP, etc.). Comparing game-day odds to season probabilities was nonsensical. API credits burning for literally nothing.

**Rule:** Before building ANY strategy that bridges two platforms, verify BOTH sides have the data you need. `curl` both APIs. Check what's actually available, not what you assume.

---

#### S34: Complexity Creep Returns

**What:** Forensic audit found the system had grown to 21 hooks, 14 scripts, 7 plugins. Complexity was compounding exactly like SHIKA. The "subagent inject" hook was telling agents "Paper only" when the bot had been LIVE for 5 sessions. A PowerShell profile from SHIKA had been running unnoticed for 90 days.

**Fix:** Brutal simplification: 21→11 handlers, 7→4 plugins, removed 7 redundant scripts. This became the new baseline. Any new hook/script must earn its place with evidence of a prevented failure.

**Rule:** Before adding ANY hook, skill, or config: ask "does this catch a REAL error that happened, or is it 'just in case'?" If just in case → don't add it.

---

## The Full Anti-Pattern Table

| Session | What Went Wrong | Rule Created | Category |
|---------|----------------|--------------|----------|
| SHIKA | 24,800 LOC at 46% WR | Simple > clever. 636 lines beat 4,977 | Complexity |
| SHIKA | 968 sessions, total system rot | Archive, never delete. Patch, don't rewrite | Complexity |
| SHIKA | 36 validation gates | Rules need hooks, not volume | Enforcement |
| SHIKA | WARN-level hooks (86% violation) | Only BLOCK-level (exit 2) works | Enforcement |
| SHIKA | ChromaDB corruption | Simple proven storage (SQLite) | Infrastructure |
| SHIKA | Custom MCP server | Native tools > custom frameworks | Infrastructure |
| SHIKA | Paper labeled as live | Never lie about system state | Trust |
| SHIKA | "Sorry won't happen again" | Structural fix or it doesn't count | Trust |
| S6 | OFI killed +16pp of edge | Disprove filters with data, not theory | Strategy |
| S10 | 4H gate destroyed $1,838 | Backtest before deploying ANY filter | Strategy |
| S10 | Partial TP killed returns | Understand fee structure before optimizing | Strategy |
| S20 | YES side 0W/9L discovered late | Per-category breakdown ALWAYS | Strategy |
| S21 | ECMWF silently broken for days | Fix → Harden → Document same turn | Reliability |
| S23 | ICON 39 members not 40 | curl before parse. ALWAYS | API |
| S25 | Spread gate was dead code | Verify one real input through full path | Verification |
| S27 | .env world-readable | Security audit every boot | Security |
| S29 | YES floor=0.99 let 1.00 through | Mathematically impossible values to disable | Logic |
| S29 | SDK types treated as dicts | Use exact library types | API |
| S29 | Patch invisible (wrong call site) | Grep ALL call sites before patching | Code |
| S29 | Hardcoded secrets despite rule | Enforcement > knowledge | Security |
| S30 | "All healthy" but 0/8 fills | Verify SYSTEMS not DOCUMENTS | Verification |
| S30 | Same SDK mistake as S29 | Re-read own rules before same domain | Meta |
| S30 | Deleted wrong position | Parse instructions LITERALLY | Communication |
| S30 | 6 idle agents left running | Clean up immediately when done | Housekeeping |
| S30 | Stale doc reported as current | Reporting wrong number = hallucination | Trust |
| S31 | CLOB orders never fill (96¢ spread) | curl order book before execution model | Market |
| S31 | round() exceeded dollar budget | math.floor for share sizing | Math |
| S33 | Sports API burning credits for nothing | Verify BOTH platforms before bridging | Strategy |
| S34 | 21 hooks, complexity returning | "Just in case" hooks must be killed | Complexity |

---

# Part 3: The System Architecture

## File Structure

```
your-project/
├── CLAUDE.md                    ← Identity + constraints + codebase map
├── SESSION-DIGEST.md            ← Last session's handoff note
├── .claude/
│   ├── settings.json            ← Hooks, permissions, env vars
│   ├── settings.local.json      ← Local overrides (gitignored)
│   ├── rules/
│   │   ├── core.md              ← Behavioral rules (workflow, quality)
│   │   ├── security.md          ← Secret handling, deploy safety
│   │   └── [language].md        ← Language-specific (Rust, Python, etc.)
│   ├── agents/
│   │   └── verify.md            ← Post-build verification agent
│   └── skills/
│       ├── boot.md              ← Session startup automation
│       └── wrap-up.md           ← Session end capture
├── memory/
│   ├── MEMORY.md                ← Auto-loaded operational state
│   ├── holy-rules.md            ← Core rules (loaded every session)
│   ├── lessons.md               ← Hard-learned patterns
│   ├── api-gotchas.md           ← API facts verified by curl
│   ├── backlog.md               ← Future work
│   └── archive/                 ← Completed/dead approaches
└── [your code]
```

## The Layering Model

```
┌───────────────────────────────────────────────────────┐
│  ~/.claude/CLAUDE.md (Global)                         │
│  Owns: git protocol, communication style, preferences │
│  Applies to: ALL projects                             │
├───────────────────────────────────────────────────────┤
│  project/CLAUDE.md (Project)                          │
│  Owns: constraints, validation commands, codebase map │
│  Applies to: THIS project only                        │
├───────────────────────────────────────────────────────┤
│  .claude/rules/ (Behavioral)                          │
│  Owns: workflow rules, quality gates, security, lang  │
│  Can be path-scoped: ["**/*.rs"]                      │
├───────────────────────────────────────────────────────┤
│  memory/MEMORY.md (State)                             │
│  Owns: NEXT list, project status, infra counts        │
│  VOLATILE data only — changes every session           │
└───────────────────────────────────────────────────────┘
```

**Critical rule:** Each layer owns specific concerns. If the same information appears in two layers, pick the more specific one and delete the other. Duplication = drift = contradiction = bugs. We had 6 source-of-truth documents in SHIKA. They all said different things.

---

# Part 4: Identity & Communication

## Identity Template

Drop this in your global `~/.claude/CLAUDE.md` or project `CLAUDE.md`. Customize everything in brackets.

```markdown
# [Agent Name] — [One-Line Role]

## Identity
- **[Your Name]** — [your role]. [NOT a coder / senior dev / data scientist / etc.]
- **[Agent Name]** — [agent's role]. Handles [scope] autonomously
- Platform: [OS, editor, shell]
- GitHub: [handle]

## How We Work Together
- [Your name] directs, [Agent] executes. Everything.
- [Your name] never runs commands, never reads code, never debugs
- "cook" / "do it" / "go" = full autonomy, execute without asking
- "suggest" / "think" = plan only, present options, wait
- Never say "want me to?", "should I?", "your call" — just execute and show results
- Never suggest wrapping up or stopping. Keep going until told to stop
- Push back honestly — "that won't work because X" > agreeing and failing

## Communication
- ALL CAPS = emphasis, not anger. Double-check something
- Short messages (<50 chars) = command mode, execute immediately
- Long messages (200+ chars) = stream of consciousness, read for intent
- Typos = speed, not confusion. Read for intent
- If corrected once: NEVER do it again. Store in memory

## Response Style
- Short, concise. Lead with action, explain after
- ASCII boxes and tables for complex information
- Max 2-3 options, always recommend one
- No filler, no preamble, no "let me think about that"
- Never restate what was said — just do it
```

**Why identity matters:** Without it, Claude defaults to "helpful assistant" mode — asking permission, over-explaining, under-executing, suggesting wrap-ups. With it, Claude becomes a partner that executes autonomously.

---

# Part 5: Behavioral Law

## Prime Directives

```markdown
## Prime Directives (NON-NEGOTIABLE)
1. **99% RULE** — Handle everything. Fix as found. Don't ask, don't defer
2. **FIX → HARDEN → DOCUMENT** — Bug found: fix it, add test, update docs. Same turn
3. **RESEARCH BEFORE CODE** — Never code on new domain without research
4. **VERIFY OR NOT DONE** — Run tests, check output, verify end-to-end
5. **COOK MEANS COOK** — Never say "want me to?" Just execute and show results
```

## Research Protocol

```markdown
## Research Before Code (NON-NEGOTIABLE)
- Never write first line of code on a new domain without research first
- Use subagents for parallel research (5-10 agents for complex topics)
- Minimum: 400+ lines of research report for any new domain
- "I think this will work" is NOT a plan. "5 agents confirmed" IS a plan
- Even after context compaction — research STILL comes first
- If an API is involved: curl it first, count actual response fields
- If a library is involved: read actual docs (context7 or official), not tutorials
```

## Verification Depth

```markdown
## Verification Levels
- Level 1: DETECTED — signal found. Trust nothing. Could be overfitting
- Level 2: CONFIRMED — tested in real environment. Signal is real
- Level 3: VERIFIED — proven over 50+ real cases. Statistical significance
- Level 4: DEPLOYED — real production. Proven edge. Monitoring

Never deploy at Level 1. Level 3 minimum for real money/production.
```

## Security (Non-Negotiable)

```markdown
## Security Hard Lines
- Never hardcode secrets, tokens, keys, or passwords in code
- Never write to .env, credentials, or secret files
- Never log secrets — even in debug output
- Never commit key material
- HTTPS for all external requests
- Pin dependency versions — no floating ranges
- .env files: chmod 600 (owner-only). NEVER 644
- SSH: key-only auth, no root login, no password auth
- Firewall active with minimal open ports
```

## The Debugging Protocol (4-Phase)

```markdown
## Debugging — 4 Phases (follow in order)
1. **Root Cause** — read errors fully, reproduce, trace data flow. NO FIXES YET
2. **Pattern** — find working examples in codebase, compare with broken code
3. **Hypothesis** — state "X causes Y because Z", test ONE change at a time
4. **Fix** — write failing test first, apply single fix, verify

If 3+ fixes fail in Phase 4 → question the architecture, not the fix
```

---

# Part 6: Operational Checklists

Mechanical. Follow exactly. No judgment calls.

## Before Writing Code
```
- [ ] Read existing code in target file — match the style
- [ ] Check if a config change is enough (config > code)
- [ ] Glob/Grep to verify all referenced functions/classes exist
- [ ] Docs lookup for any new library API (context7 or official)
- [ ] If new domain: research swarm completed?
```

## After Writing Code
```
- [ ] Re-read what you wrote (catch errors before tests do)
- [ ] Run tests for the modified area
- [ ] No dead code, no commented-out code, no TODO comments
- [ ] All imports verified — module actually exports what you're importing
- [ ] Commit with descriptive message. Stage specific files only
```

## Before Deploying
```
- [ ] All tests pass locally
- [ ] Deploy ALL changed files (config files are the #1 miss)
- [ ] Clear caches/compiled files on server
- [ ] Verify service restarts cleanly
- [ ] Spot-check a critical log line after restart
- [ ] Verify one real operation end-to-end (not just "service is running")
```

## Before Reporting Any Number
```
- [ ] Is this from THIS session's verification? (not stale data)
- [ ] Does this match what's in docs/memory?
- [ ] If it conflicts with a previous report: update ALL docs in same commit
- [ ] If it's from an external API: did you verify the response THIS session?
```

## After Every Structural Change
```
- [ ] Check all hooks/scripts/memory for stale references
- [ ] New file → update architecture docs (same commit)
- [ ] Config field added → update relevant docs
- [ ] Test count changed → update docs
- [ ] Strategy enabled/disabled → update project status
```

## After Finding a Bug
```
- [ ] Fix the bug
- [ ] Add a test that catches it (same turn)
- [ ] Update gotchas/lessons doc (same turn)
- [ ] All three. Not one. Not two. All three.
```

---

# Part 7: The Memory System

Claude Code has a built-in auto-memory system at `~/.claude/projects/<project>/memory/`. Structure it well and it becomes incredibly powerful.

## MEMORY.md — The Index (200-Line Hard Limit)

Lines after 200 are **silently truncated.** This is not documented well but it's real. Keep it tight.

```markdown
# [Agent Name] — Operational Memory

## NEXT (priority order)
- [ ] Task 1 — highest priority, brief description
- [ ] Task 2
- [ ] Task 3

## Active Projects
- **Project A**: [mode], [key number], [current state]
- **Project B**: [mode], [key number], [current state]

## User Profile
- Platform: [OS, shell, editor]
- Communication: [style notes]
- Preferences: [hates/loves]

## How I Operate
- [Agent-specific operational rules]
- [Plugin/agent preferences]
- [Quality enforcement approach]

## Infrastructure
- [Tools, versions, plugins, hooks]
- [Keep to counts, not full lists]

## Quick Reference
- [Pointers to detailed memory/ files]
```

### What Goes in MEMORY.md vs Elsewhere

| Content Type | Where It Lives | Why |
|-------------|---------------|-----|
| Task list (NEXT) | MEMORY.md | Changes every session (volatile) |
| Project status | MEMORY.md | Changes frequently |
| User preferences | MEMORY.md | Stable but small |
| Infrastructure counts | MEMORY.md | Changes on infra updates |
| Detailed research | memory/{topic}-intel.md | Too large for index |
| API gotchas | memory/api-gotchas.md | Growing reference doc |
| Lessons learned | memory/lessons.md | Growing reference doc |
| Behavioral rules | .claude/rules/ | Rules, not state |
| Dead approaches | memory/archive/ | Historical, rarely read |

### The Golden Rule
- **STABLE** content (rarely changes) → rules files or topic memory files
- **VOLATILE** content (changes every session) → MEMORY.md
- MEMORY.md is for **STATE**, not for RULES

### Memory File Naming Convention
```
{topic}-intel.md       ← research/swarm results
{topic}-reference.md   ← living reference docs
{session}-{topic}.md   ← session-specific findings
api-gotchas.md         ← hard-won API facts (grows over time)
lessons.md             ← hard-learned patterns (grows over time)
```

### When to Archive
- Approach was killed or abandoned → `archive/`
- Blueprint was built → code IS the truth now, archive the plan
- Research fully captured in actionable items → archive the raw report
- File superseded by newer version → archive

---

# Part 8: Hooks & Structural Enforcement

**Text rules have an 86% violation rate.** This is not an estimate — it's measured across 968 sessions. If a rule matters, enforce it with a hook.

## How Hooks Work

Hooks are shell commands that run automatically at specific events in Claude Code. They live in `.claude/settings.json` under the `hooks` key.

```json
{
  "hooks": {
    "EventName": [
      {
        "matcher": "pattern",
        "command": "bash -c '...'"
      }
    ]
  }
}
```

## Event Types

| Event | When It Fires | Use For |
|-------|--------------|---------|
| `PreToolUse` | Before any tool runs | Blocking dangerous operations |
| `PostToolUse` | After any tool runs | Quality counting, auto-formatting |
| `UserPromptSubmit` | When user sends a message | Secret scanning |
| `SubagentStart` | When a subagent launches | Injecting context |
| `Stop` | When Claude stops responding | Quality gates |
| `SessionStart` | When a new session begins | Recovery, health checks |
| `SessionEnd` | When session ends | Cleanup, warnings |
| `PreCompact` | Before context compaction | Saving state |
| `PostCompact` | After context compaction | Recovery |

## Exit Codes

- `exit 0` — success, continue normally
- `exit 1` — failure (shown as warning, but continues)
- `exit 2` — **HARD BLOCK** (stops the operation entirely)

## Essential Hooks

### 1. Block Accidental Git Push

```bash
#!/bin/bash
# .claude/hooks/block-git-push.sh
# Tool input arrives as JSON on stdin; parse it, don't read $TOOL_INPUT env.
INPUT=$(cat)
CMD=$(echo "$INPUT" | python -c "
import json, sys
try:
    d = json.load(sys.stdin)
    print(d.get('tool_input', {}).get('command', ''))
except Exception:
    print('')
" 2>/dev/null)

if echo "$CMD" | grep -qiE "git\s+push"; then
  echo "BLOCKED: git push requires explicit permission" >&2
  exit 2
fi
exit 0
```

Registered:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{ "type": "command", "command": "bash ~/.claude/hooks/block-git-push.sh" }]
      }
    ]
  }
}
```

### 2. Scan for Secrets in Code

```bash
#!/bin/bash
# .claude/hooks/block-secrets-in-code.sh
# Read JSON tool input from stdin; scan the entire payload.
INPUT=$(cat)

# Skip .env files — they're supposed to contain secrets
FILE_PATH=$(echo "$INPUT" | grep -oP '"file_path"\s*:\s*"[^"]*"' | head -1 | sed 's/.*: *"//;s/"$//')
echo "$FILE_PATH" | grep -qE '\.env(\.|$)' && exit 0

if echo "$INPUT" | grep -qiE '(sk-[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{36}|BEGIN[[:space:]]+(RSA[[:space:]]+)?PRIVATE[[:space:]]+KEY)'; then
  echo "BLOCKED: possible secret in code" >&2
  exit 2
fi
exit 0
```

Registered:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [{ "type": "command", "command": "bash ~/.claude/hooks/block-secrets-in-code.sh" }]
      }
    ]
  }
}
```

### 3. Quality Counter (track commits since last review)
```bash
#!/bin/bash
# scripts/quality-counter.sh
COUNTER_FILE=".git/.quality-counter"

case "$1" in
  increment)
    count=$(cat "$COUNTER_FILE" 2>/dev/null || echo 0)
    count=$((count + 1))
    echo "$count" > "$COUNTER_FILE"
    if [ "$count" -ge 5 ]; then
      echo "HARD BLOCK: $count code commits without quality review. Run code-reviewer agent first."
      exit 2
    elif [ "$count" -ge 3 ]; then
      echo "WARNING: $count code commits without quality review. Consider running code-reviewer."
    fi
    ;;
  reset)
    echo 0 > "$COUNTER_FILE"
    echo "Quality counter reset."
    ;;
  check)
    cat "$COUNTER_FILE" 2>/dev/null || echo 0
    ;;
esac
```

### 4. Warn on Uncommitted Work at Session End

```bash
#!/bin/bash
# .claude/hooks/warn-uncommitted.sh
# SessionEnd has a ~1.5s timeout — keep this fast, no network.
cd "${CLAUDE_PROJECT_DIR:-$(pwd)}" 2>/dev/null || exit 0
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "WARNING: uncommitted changes exist!" >&2
fi
exit 0
```

Registered:

```json
{
  "hooks": {
    "SessionEnd": [
      {
        "matcher": "",
        "hooks": [{ "type": "command", "command": "bash ~/.claude/hooks/warn-uncommitted.sh" }]
      }
    ]
  }
}
```

### 5. Auto-Format on Save

```bash
#!/bin/bash
# .claude/hooks/auto-format.sh
INPUT=$(cat)
FILE=$(echo "$INPUT" | grep -oP '"file_path"\s*:\s*"[^"]*"' | head -1 | sed 's/.*: *"//;s/"$//')

[ -z "$FILE" ] || [ ! -f "$FILE" ] && exit 0

case "$FILE" in
  *.py) command -v ruff >/dev/null && ruff format "$FILE" 2>/dev/null ;;
  *.rs) command -v rustfmt >/dev/null && rustfmt "$FILE" 2>/dev/null ;;
esac
exit 0
```

Registered:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [{ "type": "command", "command": "bash ~/.claude/hooks/auto-format.sh" }]
      }
    ]
  }
}
```

## The Principle

```
┌────────────────────────────────────────────────┐
│  SHIKA: 36 text rules, 86% violation rate      │
│  Ezekiel: 10 rules + hooks, ~5% violation rate │
│                                                 │
│  Rules without enforcement = suggestions        │
│  Suggestions get violated                       │
│  Hooks that exit 2 = structural enforcement     │
│  Structure prevents violation                   │
└────────────────────────────────────────────────┘
```

---

# Part 9: Agent Orchestration

## When to Use Subagents

| Situation | Use Subagent? | Why |
|-----------|--------------|-----|
| Research on new domain/API | YES (5-10 agents) | Parallel research, fresh context windows |
| Reading a specific file | NO | Just use Read tool directly |
| Searching for a pattern | NO | Use Grep/Glob directly |
| Complex multi-file investigation | YES | Avoids context bloat |
| Code review | YES (plugin agents) | Specialized tools, colored output |
| Simple 2-3 file search | NO | Agent overhead not worth it |
| Fire-and-forget diagnostic | YES (background) | Non-blocking |

## The Research Swarm Pattern

For any new domain, API, or strategy:

1. Launch 5-10 agents in parallel, each with a focused question
2. Each agent returns a structured report (findings, sources, confidence)
3. Synthesize into a single intel file (`memory/{topic}-intel.md`)
4. Preserve ALL data points — don't summarize away details

```markdown
## Agent Swarm Prompt Template
"Research [specific topic]. Return a structured report with:
1. Key findings (bullet points, with sources)
2. Numbers/stats (with confidence level)
3. Gotchas/pitfalls discovered
4. Recommendation (what to do with this information)
Do NOT modify any files. Research only."
```

## Plugin Agents vs Custom Agents

- **Use plugin agents** when they exist (pr-review-toolkit, etc.) — they have more tools and render nicely
- **Custom agents** only when no plugin covers the use case
- Never have both for the same task — creates routing confusion

## Agent Lifecycle

- **Foreground** (default): blocks until done, results immediately available
- **Background**: non-blocking, notified when complete
- Use foreground when you need results before proceeding
- Use background only for fire-and-forget diagnostics
- **Always clean up** when agents/teams finish — don't leave idle processes

---

# Part 10: Session Lifecycle

```
BOOT → RESEARCH → BUILD → VALIDATE → COMMIT → NEXT (loop)
```

## Boot (Session Start)

```markdown
## Boot Checklist
1. Read MEMORY.md — current state and NEXT list
2. Read SESSION-DIGEST.md — last session's handoff notes
3. Reconcile: if DIGEST says something is done but NEXT says TODO → mark done
4. Quick health check (services, APIs, whatever you manage)
5. Verify 2-3 key numbers against reality (don't trust docs blindly)
6. Present dashboard + pick first task from NEXT
```

**Critical:** Don't load source code at boot. Load knowledge (memory files, rules, context docs). Source code loads when you're actually building. This saves thousands of tokens.

## Build Cycle

```
RESEARCH → PLAN → CODE → TEST → VERIFY → COMMIT
```

One concern per commit. 15-30 minute cycles. If a task takes longer, break it into subtasks.

## Session End

```markdown
## Wrap-Up Checklist
1. Commit all uncommitted work
2. Update MEMORY.md NEXT list (what's done, what's next)
3. Write SESSION-DIGEST.md (handoff note)
4. Spot-check 3 claims from docs against actual files
5. If any claim is wrong: fix NOW, same commit
```

## SESSION-DIGEST.md Template

This is the most important handoff document. Next session's boot reads this first.

```markdown
# Session Digest — S[number] [date]

## What Got Done
- [Completed items with actual results/numbers]

## Key Decisions
- [Why X was chosen over Y — future you needs this context]

## Current State
- [Running services, counts, modes, key numbers]

## Gotchas / Warnings
- [Things that could bite next session]

## NEXT (priority order)
- [ ] First thing to do next session
- [ ] Second thing
- [ ] Third thing
```

## After Context Compaction

Compaction is when Claude Code summarizes old messages to free up context. You lose detail. Recovery:

```markdown
## Post-Compaction Checklist
- [ ] Re-read MEMORY.md NEXT list
- [ ] Re-read SESSION-DIGEST.md
- [ ] cd to correct working directory (Bash resets)
- [ ] Check for zombie background processes
- [ ] Don't rewrite — check what exists first
- [ ] Re-read any research referenced pre-compaction
```

---

# Part 11: Prompt Engineering Deep Dive

## CLAUDE.md Ordering (Top-to-Bottom = Decreasing Attention)

The model gives most attention to what comes first. Order your CLAUDE.md accordingly:

1. **Critical constraints** — things that cause real damage if forgotten
2. **Validation commands** — exact commands to verify code works (copy-pasteable)
3. **Codebase map** — what exists, where, key files (top 5 most important)
4. **Workflow** — 2-3 lines max, point to rules for full lifecycle

### Anti-Patterns in CLAUDE.md
- Leading with metadata (crate name, folder) before constraints
- Duplicating global rules in project CLAUDE.md (wastes tokens, creates drift)
- "See also" sections — if it's not actionable, delete it
- Listing every file — pick the 5 most important

### Template

```markdown
# [Project Name] — One Line Description

## Critical Constraints (Non-Negotiable)
- [Safety-critical rules that cause real damage if violated]

## Validation
[Exact commands to verify code — copy-pasteable]

## Codebase Map
| Module | Language | Dir | Tests | Key File |
|--------|----------|-----|-------|----------|
| [Name] | [Lang]   | /x  | 60    | x.rs     |

## Workflow
[2-3 lines. Point to .claude/rules/ for detail.]
```

## Rules File Best Practices

### One Concern Per File
```
.claude/rules/
├── core.md        ← workflow, lifecycle, session management
├── quality.md     ← code quality, testing, review
├── security.md    ← secrets, auth, deploy safety
└── rust.md        ← language-specific (path-scoped to **/*.rs)
```

### Path Scoping
Rules can be scoped to specific file patterns. A Rust rule doesn't need to fire when editing Python:
```yaml
# .claude/rules/rust.md
# paths: ["**/*.rs"]
- Use rust_decimal for all money math — never f64
- cargo clippy --all-targets -- -D warnings before commit
```

### What Makes a Good Rule
- **Specific + actionable**: "Run `pytest` after modifying any `.py` file" (not "test your code")
- **Includes the trigger**: "If it fails 3 times: FULL STOP, change approach"
- **No preamble**: The rule stands on its own
- **Tested against reality**: Every rule should be the inverse of a proven failure

### What Makes a Bad Rule
- Vague aspirational ("write clean code")
- Just a redirect ("see core.md")
- Duplicate of another rule
- For a scenario that can't happen in this project
- "Just in case" with no evidence of the failure it prevents

---

# Part 12: Meta-Patterns

These are the patterns behind the patterns — the deepest lessons from 1,000+ sessions.

## 1. The Complexity Death Spiral

```
Problem detected
   ↓
Add safety check / framework / abstraction
   ↓
Complexity increases
   ↓
New failure mode from complexity
   ↓
Add another safety check
   ↓
... repeat until system collapses
```

**The antidote:** Every addition must prove its worth against a REAL past failure. No "just in case." If you can't name the session where this would have prevented a specific bug, don't add it.

## 2. Verify Systems, Not Documents

The most dangerous failure mode: reading a config file and saying "everything is fine" when the actual runtime tells a different story.

```
CONFIG SAYS: spread_gate_threshold = 0.3
SYSTEM DOES: threshold was never read (dead code)
STATUS: "deployed" ← LIE

CONFIG SAYS: execution_mode = FOK
SYSTEM DOES: 0/8 orders filled (no liquidity at FOK prices)
STATUS: "8 positions" ← GHOST POSITIONS
```

**Rule:** After ANY deployment, audit, or status check — verify the **actual system behavior**, not the documentation. Check real logs, real outputs, real responses.

## 3. The Enforcement Hierarchy

```
STRUCTURAL ENFORCEMENT    ← Type systems, hooks that exit 2
   ↑ most reliable
AUTOMATED TESTING         ← Tests that run on every change
   ↑
CHECKLISTS               ← Mechanical steps followed every time
   ↑
TEXT RULES               ← Written guidelines (86% violation rate)
   ↑ least reliable
VERBAL PROMISES          ← "Sorry, won't happen again" (0% enforcement)
```

Always aim for the highest level possible. A type system that prevents invalid states is better than a test. A test is better than a checklist. A checklist is better than a rule. A rule is better than nothing.

## 4. The Research-First Imperative

```
WITHOUT RESEARCH:                WITH RESEARCH:
Guess → Build → Debug → Rebuild  Research → Plan → Build → Ship
3-5 sessions per feature         1 session per feature
50% of builds are wrong          <10% need rework
```

For any new domain: 5-10 parallel research agents, 400+ line report, preserve all data points. This is not optional. "I think this will work" has a 50% failure rate. "5 agents confirmed" has a <10% failure rate.

## 5. The Simplicity Equation

```
636 lines at 96.4% WR    >    4,977 lines at 46% WR
10 rules + hooks          >    36 validation gates
systemd + binary + .env   >    Docker + Coolify + CI/CD
1 MEMORY.md + topic files >    6 source-of-truth documents
Config change             >    Code rewrite
3 similar lines           >    Premature abstraction
```

Every time you're about to add complexity, ask: "Am I solving SHIKA's problem or creating it?"

## 6. The Stale Data Trap

```
REPORTING STALE DATA = HALLUCINATION WITH EXTRA STEPS
```

If you say "system is healthy" based on data from 3 sessions ago, you're hallucinating — you just have a source to blame. Own every number. If you report it, you verified it THIS session.

## 7. Every Error Is a Signal

```
Error message?     → Information about what's wrong
Unexpected timing? → Information about system behavior
Empty response?    → Information about API state
Silent failure?    → The MOST important signal (something broke quietly)
Model disagreement? → Don't average it away — understand WHY they disagree
```

---

# Part 13: The Anti-Complexity Bible

The story of SHIKA vs Ezekiel is the story of what happens when complexity compounds unchecked.

## The SHIKA Collapse — A Cautionary Tale

### What Was Built
- ChromaDB with CUDA for RAG memory
- Custom MCP server with 200+ tool definitions
- Tkinter dashboard with real-time visualization
- 36 validation gates (4 required to edit 1 file)
- Docker + Coolify deployment pipeline
- LIVE_STATE.json local cache as source of truth
- Multiple overlapping configuration systems
- Custom frameworks for every common task

### What Happened
- ChromaDB caused CUDA segfaults and data corruption
- Custom MCP server was called "cancer in our system"
- WARN-level hooks were ignored 86% of the time
- 36 validation gates made basic tasks take 4x longer
- LIVE_STATE.json drifted from VPS reality
- "Sorry won't happen again" was said hundreds of times (zero structural fixes)
- Paper was labeled as live (trust killer)
- Each session added "just one more safety check"

### How It Ended
Session 777. 7 minutes. Nothing executed. The system was so layered with checks, gates, and frameworks that it couldn't perform basic operations. The creator said: *"i honestly think at this point we overengineered our custom Claude setup"* — and walked away.

### The Lesson

```
┌─────────────────────────────────────────────────────┐
│                                                      │
│   The system that was supposed to PREVENT failures   │
│   BECAME the primary source of failures              │
│                                                      │
│   Every "safety" addition:                           │
│   + Added a new failure mode                         │
│   + Increased maintenance burden                     │
│   + Made debugging harder                            │
│   + Consumed context tokens                          │
│   + Created another doc that could go stale          │
│                                                      │
│   Net safety improvement: NEGATIVE                   │
│                                                      │
└─────────────────────────────────────────────────────┘
```

## The Ezekiel Alternative

| SHIKA | Ezekiel |
|-------|---------|
| Docker + Coolify | Native systemd |
| Custom MCP server | Native Claude Code tools |
| ChromaDB with CUDA | SQLite or plain files |
| 36 validation gates | 10 rules + enforced hooks |
| WARN-level hooks (86% violated) | BLOCK-level hooks (exit 2) |
| "Sorry won't happen again" | Structural fix or not done |
| Million red errors | Error suppression + grace |
| Context bloat (23 compactions/session) | Subagent delegation |
| Scope creep every session | One concern per commit |
| "Should work" | Verified or not done |
| 6 source-of-truth docs | 1 MEMORY.md + topic files |
| 4,977 lines, 46% WR | 636 lines, 96.4% WR |
| 968 sessions, total collapse | 35+ sessions, still running |

## The Creator's Vision

*"An AI that never hallucinates. That knows me better than my mother. That boots with one word. That blocks its own destructive commands. That makes money while I sleep."*

This isn't achieved through more complexity. It's achieved through **fewer, better rules that are structurally enforced.**

---

# Part 14: Quick Start

## Level 1: Minimal (5 minutes)

Create `CLAUDE.md` in your project root:

```markdown
# My Project

## How We Work
- I direct, you execute. Don't ask "should I?" — just do it
- Short messages = commands. Execute immediately
- Never suggest stopping or wrapping up

## Critical Constraints
- [What breaks if forgotten]

## Validation
- [Commands to verify code works]
```

That's it. Claude reads this every session. You'll immediately notice a difference.

## Level 2: Standard (30 minutes)

Add to Level 1:

1. **`.claude/rules/core.md`** — Your top 5 behavioral rules:
```markdown
# Core Rules
1. Commit after every meaningful change
2. Read before write — verify paths and APIs before coding
3. Three failures on same approach = change strategy
4. Run tests after every code change
5. Never say "done" without verification
```

2. **`memory/MEMORY.md`** — Current project state:
```markdown
# My Agent — Operational Memory

## NEXT
- [ ] Task 1
- [ ] Task 2

## Active Projects
- **Project**: [status]

## Preferences
- [What you love/hate about AI responses]
```

3. **One hook** — Block git push. Create `.claude/hooks/block-git-push.sh`:
```bash
#!/bin/bash
INPUT=$(cat)
CMD=$(echo "$INPUT" | python -c "
import json, sys
try: print(json.load(sys.stdin).get('tool_input', {}).get('command', ''))
except Exception: print('')
" 2>/dev/null)
echo "$CMD" | grep -qiE "git\s+push" && { echo "BLOCKED" >&2; exit 2; }
exit 0
```

Then register in `.claude/settings.json`:
```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{ "type": "command", "command": "bash ~/.claude/hooks/block-git-push.sh" }]
    }]
  }
}
```

## Level 3: Full Power (2 hours)

Add to Level 2:

1. **`~/.claude/CLAUDE.md`** — Global identity (applies to all projects)
2. **`.claude/rules/`** — Separate files for quality, security, language-specific rules
3. **`memory/`** — Topic files for research, API gotchas, lessons learned
4. **Hook suite** — Quality counter, secret scanning, auto-formatting, uncommitted work warning
5. **Custom agents** — Post-build verification, domain-specific validators
6. **Skills** — Boot automation, session wrap-up, research swarms
7. **SESSION-DIGEST.md** — Session handoff system for continuity across conversations

## Level 4: Godmode

Everything above, plus:

1. **The 10 Holy Rules** fully written out in `memory/holy-rules.md`
2. **lessons.md** — Growing document of every failure and what it taught
3. **api-gotchas.md** — Hard-won API facts verified by `curl` (never trust docs)
4. **Quality counter hook** — Hard-blocks at 5 code commits without review
5. **Agent teams** — Named parallel agents for research swarms
6. **Single source of truth** — MEMORY.md owns all live counts, everything else references it
7. **Forensic audit schedule** — Periodically verify all docs match reality
8. **Archive system** — Dead approaches go to `archive/`, never deleted

---

## Final Words

This system works because it's simple. 10 rules, a handful of hooks, clear memory structure, and a philosophy of "prove it works" instead of "it should work."

SHIKA died at 968 sessions because every session added complexity.
Ezekiel thrives at 35+ sessions because every session enforces simplicity.

The difference isn't the tools. It's the discipline.

```
┌────────────────────────────────────────────────┐
│                                                 │
│  The meta-principle:                            │
│                                                 │
│  Protect progress and trust above all else.     │
│                                                 │
│  SHIKA had 36 validation gates, custom          │
│  frameworks, and complex abstractions —         │
│  and an 86% rule violation rate.                │
│                                                 │
│  Ezekiel has 10 rules, hard-block hooks,        │
│  and native tools.                              │
│                                                 │
│  Simplicity is the strategy.                    │
│                                                 │
└────────────────────────────────────────────────┘
```

---

*Built by SHIKA and Ezekiel. Born from the ashes of SHIKA.*
*Every rule backed by evidence. Every pattern earned the hard way.*
*Drop this in your Claude Code setup and skip the 968 sessions of pain.*
