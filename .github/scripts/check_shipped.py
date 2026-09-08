#!/usr/bin/env python3
"""Check the shipped plugin still matches the skill sources.

`dist/claude/adform-agentic-skills/` is what marketplace.json installs, but
build-plugin.sh does not generate it — it is maintained by hand, and has drifted
from dist/generic/ before.
"""

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "dist" / "generic"
SHIPPED = ROOT / "dist" / "claude" / "adform-agentic-skills" / "skills"

errors: list[str] = []

source = {p.parent.name: p for p in SRC.glob("*/SKILL.md")}
shipped = {p.parent.name: p for p in SHIPPED.glob("*/SKILL.md")}

if not source:
    print(f"error: no skills found under {SRC.relative_to(ROOT)}", file=sys.stderr)
    sys.exit(1)

for name in sorted(source.keys() - shipped.keys()):
    errors.append(f"{name}: in dist/generic but not shipped")

for name in sorted(shipped.keys() - source.keys()):
    errors.append(f"{name}: shipped but not in dist/generic")

for name in sorted(source.keys() & shipped.keys()):
    if source[name].read_bytes() != shipped[name].read_bytes():
        errors.append(f"{name}: shipped copy differs from dist/generic")

for error in errors:
    print(f"error: {error}", file=sys.stderr)

if errors:
    print(
        "\nRegenerate the shipped plugin from dist/generic/ and commit the result.",
        file=sys.stderr,
    )

print(f"compared {len(source)} skills: {len(errors)} error(s)")
sys.exit(1 if errors else 0)
