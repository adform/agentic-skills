#!/usr/bin/env python3
"""Validate the marketplace and plugin manifests."""

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
errors: list[str] = []


def load(path: pathlib.Path):
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        errors.append(f"{path.relative_to(ROOT)}: missing")
    except json.JSONDecodeError as exc:
        errors.append(f"{path.relative_to(ROOT)}: invalid JSON — {exc}")
    return None


marketplace = load(ROOT / ".claude-plugin" / "marketplace.json")

if marketplace is not None:
    for field in ("name", "owner", "plugins"):
        if field not in marketplace:
            errors.append(f"marketplace.json: missing '{field}'")

    for entry in marketplace.get("plugins", []):
        name = entry.get("name", "<unnamed>")
        for field in ("name", "source", "description", "version"):
            if not entry.get(field):
                errors.append(f"marketplace.json: plugin '{name}' missing '{field}'")

        source = entry.get("source")
        # A source that escapes the repo would let an install pull from
        # anywhere, so resolve it and confirm it stays inside and exists.
        if isinstance(source, str):
            resolved = (ROOT / source).resolve()
            if not resolved.is_relative_to(ROOT):
                errors.append(f"marketplace.json: plugin '{name}' source escapes the repo: {source}")
            elif not resolved.is_dir():
                errors.append(f"marketplace.json: plugin '{name}' source does not exist: {source}")
            else:
                manifest = load(resolved / ".claude-plugin" / "plugin.json")
                if manifest is not None and manifest.get("name") != entry.get("name"):
                    errors.append(
                        f"marketplace.json: plugin '{name}' name disagrees with its "
                        f"plugin.json ('{manifest.get('name')}')"
                    )

for error in errors:
    print(f"error: {error}", file=sys.stderr)

print(f"checked manifests: {len(errors)} error(s)")
sys.exit(1 if errors else 0)
