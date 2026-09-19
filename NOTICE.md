# Attribution Notice

This repository contains original documentation written by Josip Lipak (GitHub `jlipak`). The code patterns and shell scripts shown within the documents are also original work, written from scratch.

However, several design choices were informed by concepts from the public Claude Code ecosystem. Attribution to those concept sources:

## Concept Inspirations

### `obra/superpowers` (MIT)

- Source: https://github.com/obra/superpowers
- Influenced: plan-first workflow skill patterns referenced in `blueprint.md` Part 5
- How: read as concept reference, not installed as plugin. The `/research` skill pattern was inspired by superpowers' plan-first discipline.

### `disler/claude-code-hooks-mastery` (no LICENSE — concept reference only)

- Source: https://github.com/disler/claude-code-hooks-mastery
- Influenced: hook architecture and exit-code semantics in `blueprint.md` Part 4 and `memory-kit.md` Part 13
- How: read concepts only (exit 2 hard-block enforcement, 13-event lifecycle coverage). No code copied. All hook implementations in this repo are original.

### `Orchestra-Research/AI-Research-SKILLs` (verified MIT-equivalent)

- Source: https://github.com/Orchestra-Research/AI-research-SKILLs
- Influenced: eval framework patterns (per-criterion P/R/F1 metrics)
- How: pattern extraction for evaluation methodology. Original code in any derivative work.

### `jordanrendric/claude-video-vision` (MIT)

- Source: https://github.com/jordanrendric/claude-video-vision
- Influenced: video pipeline patterns referenced in operator workflow examples
- How: read as reference. Did not adopt the codebase directly for this documentation set.

## Discipline

The author practices license auditing before consuming any third-party Claude Code ecosystem repo:

- If LICENSE is missing → read concepts only, write own code
- If LICENSE is permissive (MIT/Apache) → may fork with attribution
- If LICENSE is restrictive → do not consume

This documentation set itself is MIT licensed (see `LICENSE`). Adopt patterns freely. Attribution appreciated but not required for the patterns themselves; only required if you fork the documentation text verbatim.

## What Is NOT Borrowed

- The specific 14-part structure of `memory-kit.md`, `blueprint.md`, `ezekiel-kit.md` — original
- The 10 Holy Rules in `ezekiel-kit.md` — original, distilled from operator's own session data
- The 4 atom types taxonomy presentation — follows Anthropic's published auto-memory spec but with original framing
- The cost-tiered agent pattern — original deliberate design choice
- The two-channel backup pipeline pattern — original
- The 8 anti-patterns in `blueprint.md` Part 14 — original observation

If you find a pattern in this repo that resembles work from another public source not credited here, please open an issue and attribution will be corrected.

---

*Maintained by Josip Lipak.*
