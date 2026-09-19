#!/usr/bin/env python
"""Check markdown links in this repository. Standard library only.

For each file: every relative link must point at an existing file, every
#anchor must match a heading (GitHub slug rules) in the target file, and
reference-style links must have a definition. External URLs are listed,
never fetched. Exit 1 if any internal link is broken.

Usage: python scripts/check_links.py [file.md ...]
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_FILES = ["README.md", "blueprint.md", "ezekiel-kit.md", "memory-kit.md"]

FENCE = re.compile(r"^(```|~~~)")
INLINE_CODE = re.compile(r"`[^`\n]*`")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
DEFINITION = re.compile(r"^\s{0,3}\[([^\]]+)\]:\s*(\S+)")
INLINE_LINK = re.compile(r"!?\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
FULL_REF = re.compile(r"\[([^\]]+)\]\[([^\]]*)\]")
SHORTCUT_REF = re.compile(r"(?<!\])\[([^\[\]]+)\](?![\(\[:])")
EXTERNAL = re.compile(r"^(https?://|mailto:)", re.I)


def read_lines(path):
    with open(path, encoding="utf-8") as f:
        return f.read().splitlines()


def prose_lines(lines):
    """Yield (line_no, text) for lines outside fenced code blocks, with inline code removed."""
    in_fence = False
    for no, line in enumerate(lines, 1):
        if FENCE.match(line.strip()):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        yield no, INLINE_CODE.sub("", line)


def slugify(text):
    text = re.sub(r"[*_`]+", "", text)
    text = INLINE_LINK.sub(r"\1", text)
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    return text.replace(" ", "-")


def headings(path, cache={}):
    if path in cache:
        return cache[path]
    slugs = set()
    seen = {}
    for _, line in prose_lines(read_lines(path)):
        m = HEADING.match(line)
        if not m:
            continue
        slug = slugify(m.group(2))
        n = seen.get(slug, 0)
        seen[slug] = n + 1
        slugs.add(slug if n == 0 else f"{slug}-{n}")
    cache[path] = slugs
    return slugs


def check_file(path, externals, broken):
    lines = read_lines(path)
    prose = list(prose_lines(lines))
    definitions = {}
    for _, line in prose:
        m = DEFINITION.match(line)
        if m:
            definitions[m.group(1).lower()] = m.group(2)

    targets = []  # (line_no, target)
    for no, line in prose:
        if DEFINITION.match(line):
            continue
        for m in INLINE_LINK.finditer(line):
            targets.append((no, m.group(2)))
        stripped = INLINE_LINK.sub("", line)
        for m in FULL_REF.finditer(stripped):
            label = (m.group(2) or m.group(1)).lower()
            targets.append((no, definitions.get(label, f"[undefined reference: {label}]")))
        stripped = FULL_REF.sub("", stripped)
        for m in SHORTCUT_REF.finditer(stripped):
            label = m.group(1).lower()
            if label in definitions:
                targets.append((no, definitions[label]))
    for no, target in (t for t in [(0, v) for v in definitions.values()]):
        targets.append((no, target))

    count = 0
    for no, target in targets:
        count += 1
        if EXTERNAL.match(target):
            externals.add(target)
            continue
        if target.startswith("[undefined"):
            broken.append((path, no, target))
            continue
        file_part, _, anchor = target.partition("#")
        if file_part:
            dest = os.path.normpath(os.path.join(os.path.dirname(path), file_part))
            if not os.path.exists(dest):
                broken.append((path, no, f"{target} -> missing file {file_part}"))
                continue
        else:
            dest = path
        if anchor:
            if not dest.lower().endswith(".md") or os.path.isdir(dest):
                continue
            if anchor.lower() not in headings(dest):
                broken.append((path, no, f"{target} -> no heading for #{anchor}"))
    return count


def main(argv):
    files = argv or DEFAULT_FILES
    externals = set()
    broken = []
    for name in files:
        path = name if os.path.isabs(name) else os.path.join(ROOT, name)
        if not os.path.exists(path):
            print(f"MISSING FILE {name}")
            broken.append((name, 0, "file not found"))
            continue
        n = check_file(path, externals, broken)
        print(f"{os.path.relpath(path, ROOT)}: {n} links checked")
    print(f"\nExternal URLs ({len(externals)}, not fetched):")
    for url in sorted(externals):
        print(f"  {url}")
    if broken:
        print(f"\nBROKEN ({len(broken)}):")
        for path, no, what in broken:
            print(f"  {os.path.relpath(path, ROOT) if os.path.isabs(path) else path}:{no}: {what}")
        return 1
    print("\nOK: no broken internal links")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
