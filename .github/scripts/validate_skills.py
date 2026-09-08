#!/usr/bin/env python3
"""Validate SKILL.md frontmatter across dist/generic."""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "dist" / "generic"

# Deliberately not using a YAML library: the runner has no guaranteed PyYAML,
# and the frontmatter here only ever uses top-level scalar keys.
KEY = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$")

errors: list[str] = []
seen: dict[str, pathlib.Path] = {}
skills = sorted(SRC.glob("*/SKILL.md"))

if not skills:
    print(f"error: no SKILL.md found under {SRC.relative_to(ROOT)}", file=sys.stderr)
    sys.exit(1)

for path in skills:
    rel = path.relative_to(ROOT)
    directory = path.parent.name
    lines = path.read_text().splitlines()

    if not lines or lines[0].strip() != "---":
        errors.append(f"{rel}: no frontmatter block")
        continue

    try:
        end = next(i for i, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration:
        errors.append(f"{rel}: frontmatter block is not closed")
        continue

    keys: dict[str, str] = {}
    for line in lines[1:end]:
        if match := KEY.match(line):
            keys[match.group(1)] = match.group(2).strip()

    if "name" not in keys:
        errors.append(f"{rel}: frontmatter missing 'name'")
    elif keys["name"] != directory:
        errors.append(f"{rel}: frontmatter name '{keys['name']}' != directory '{directory}'")

    # A folded value ('>-') leaves the key empty on its own line, so only the
    # key's presence is meaningful here.
    if "description" not in keys:
        errors.append(f"{rel}: frontmatter missing 'description'")

    # build-plugin.sh flattens every skill into one directory, so a duplicate
    # name means one skill silently overwrites another.
    if directory in seen:
        errors.append(f"{rel}: duplicate skill name, also at {seen[directory]}")
    else:
        seen[directory] = rel

for error in errors:
    print(f"error: {error}", file=sys.stderr)

print(f"checked {len(skills)} skills: {len(errors)} error(s)")
sys.exit(1 if errors else 0)
