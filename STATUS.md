# STATUS — claude-code-operating-model

Updated: 2026-09-19
State: public-readiness pass done locally on `main`, two commits (`ef8df5b` docs, the hygiene commit that adds this file), nothing pushed. README 61 lines. `python scripts/check_links.py` green (54 links, 0 broken). No pseudonym, machine name or private path left in the tree.
Next: the owner pushes, sets description and topics, flips the repository to public. After that the repo only changes when an issue or a correction PR arrives.

## For the owner

- Push (from the hub folder): `git -C projects/claude-code-operating-model push origin main`
- Description: `gh repo edit jlipak/claude-code-operating-model --description "Three documents on running Claude Code daily across several projects, and what the author would change today."`
- Topics: `gh repo edit jlipak/claude-code-operating-model --add-topic claude-code --add-topic ai-engineering --add-topic operating-model --add-topic documentation --add-topic agent-workflows`
- Make public: GitHub, repository Settings, Danger Zone, "Change visibility", Public. Or `gh repo edit jlipak/claude-code-operating-model --visibility public --accept-visibility-change-consequences`.

## Validation (this session)

```
$ python scripts/check_links.py
README.md: 1 links checked
blueprint.md: 24 links checked
ezekiel-kit.md: 15 links checked
memory-kit.md: 14 links checked

External URLs (1, not fetched):
  https://github.com/jlipak

OK: no broken internal links
```

Negative test on a scratch file with a bad anchor and a missing file: both reported, exit code 1.

## Audit of the four documents (step 1 of the task)

Stale claims, fixed:
- README (old): kit line counts off by ~100 each, "actively maintained", "Maintained by <pseudonym>". Rewritten.
- `ezekiel-kit.md` Part 8 and `memory-kit.md` Part 13: the generic hook registration showed a flat `{"matcher", "command"}` object; real settings.json nests `hooks: [{type, command}]`, as every registered example in the same documents already did. Corrected in three places (incl. memory-kit Hook 2 registration).
- `blueprint.md` Part 3 maturity box said Level 2 = 5 hooks, Level 3 = 10, Level 4 = 13+, while Part 13 lists 8 at Level 2 and adds four at Level 3 (12) and no hooks at Level 4; `block-versioned-files.sh` was in no level at all. Now: 3 / 8 / 13 / 13, Level 3 gains `block-versioned-files.sh`, "13 hooks tested".
- `blueprint.md` Final Words "13 hooks across 9 events": the registry in Part 3 wires 10 events. Corrected.
- `blueprint.md` references `[memory-kit]`, `[ezekiel-kit]`, `[memory-kit Part 10]` had no link definitions and rendered as literal text. Definitions added at the end of the file.
- `LICENSE` copyright line carried the pseudonym and the old GitHub handle. Now the author's name and `jlipak`.

Private paths and machine names: none found (`C:\Users`, `~/Desktop`, hostnames all absent). The blueprint's "this machine's Desktop tree" in Tier 1B is generic and stays.

Persons and clients:
- The owner's pseudonym appeared 33 times in `ezekiel-kit.md` as the name of the collapsed predecessor system, plus in README, NOTICE and LICENSE. The system is now called v1 throughout; one quoted line keeps the edit visible as `[v1]`. README, NOTICE and LICENSE name the author.
- `blueprint.md` Part 9 used atom names from one of the author's real products (`lex_pricing_*`). Generalized to `app_pricing_*`.
- Platform and API names in the failure database (Hyperliquid, Polymarket, Pinnacle, ECMWF, ICON, Discord) are services, not people or clients. Left.

Contradictions between the kits, fixed:
- `ezekiel-kit.md` Part 7 presents a MEMORY.md template with nested headings and a NEXT list under the heading "The Index (200-line hard limit)"; `memory-kit.md` Part 5 says the auto-memory index is one line per atom, no nested headings, and a separate project MEMORY.md holds state. A note in ezekiel Part 7 now says which file is which and links memory-kit Part 5.
- `ezekiel-kit.md` anti-pattern table said v1 had "24,800 LOC"; the same document says 4,977 lines seven times. Aligned to 4,977.
- `memory-kit.md` Part 12 counted `lesson_*` atoms although its own taxonomy has four types (user, feedback, project, reference); the blueprint also uses `lesson_*.md`. Memory-kit now says lessons are `feedback` atoms and that the blueprint names them `lesson_*`.

Left as written (could not be verified from here, or deliberate period detail; the kit headers cover it):
- `ezekiel-kit.md`: "968 sessions" versus "it ended on Session 777". Both numbers are the author's; not reconciled.
- Measured rates (86% text-rule violation, ~5% for Ezekiel, 96.4% / 97.1% win rates) and money figures: the author's own numbers, left.
- `blueprint.md`: statusline example names "Claude Opus 4.7"; the built-in skill list says `review` (today `code-review`); agent names `Explore`, `Plan`. Period detail.
- Research swarm sizes differ (blueprint 3-5 agents, ezekiel 5-10). The README states what is used now (one agent, two or three for a comparison).
- `memory-kit.md` Hook 4 uses an undefined `PROJECT_SLUG`; Hook 3 uses GNU `date -d`. Code samples, not exercised in this pass.

## Notes

- Commits end with the Fable co-author line. Nothing pushed; the push waits for the owner's word.
- `.gitignore` already excludes `SESSION-DIGEST.md` and secrets; unchanged.
- The remote already points at `github.com/jlipak/claude-code-operating-model.git`.
