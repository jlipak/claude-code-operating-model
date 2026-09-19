# Changelog

## 2026-09-19 — Public-readiness pass

- README rewritten: what the three documents are, who they are for, how to adopt them, and what the author would change today (the v1 to v3 lesson).
- Each kit opens with a two-line header: written when, for which Claude Code version, status.
- `ezekiel-kit.md`: the predecessor system is now called v1 (it carried the author's pseudonym); the lines-of-code figure in the anti-pattern table aligned with the rest of the text (4,977); the generic hook JSON corrected to the settings.json shape; a note reconciles the MEMORY.md template with memory-kit Part 5.
- `blueprint.md`: hook counts per adoption level reconciled (Part 3 box; Part 13 Level 3 gains `block-versioned-files.sh`; 13 hooks across 10 events); the `[memory-kit]` and `[ezekiel-kit]` references now resolve; project-specific atom names in Part 9 generalized.
- `memory-kit.md`: two hook registrations corrected to the nested settings.json shape; lesson atoms mapped to the `feedback` type.
- `LICENSE` and `NOTICE.md` name the author and the current GitHub handle.
- Added `CHANGELOG.md`, `CONTRIBUTING.md`, `.editorconfig`, `CODEOWNERS` and `scripts/check_links.py`.

## 2026-05-27 — Original release

- `ezekiel-kit.md`, `memory-kit.md`, `blueprint.md`, `README.md`, `NOTICE.md`, MIT `LICENSE`.
- Same day: hook input pattern fixed (tool input read from stdin JSON), unverified claims softened.
