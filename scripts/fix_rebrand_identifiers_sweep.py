#!/usr/bin/env python3
"""Repo-wide repair of identifiers broken by the bulk Hermes->Berdaya Agent rebrand.

The bulk replace turned identifiers like ``HermesCLI`` / ``startHermes`` into
``Berdaya AgentCLI`` / ``startBerdaya Agent`` — an embedded space that is a
syntax error in Python/JS. Code identifiers must keep the original ``Hermes``
spelling; only prose/user-facing text says "Berdaya Agent".

Two repair rules:
  1. ``fooBerdaya Agent``  -> ``fooHermes``   (identifier char immediately before)
  2. ``Berdaya AgentBar``  -> ``HermesBar``   (identifier char immediately after)

Prose like "let Berdaya Agent do X" is untouched (space on both sides).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CODE_EXTS = {
    ".py", ".pyi", ".js", ".cjs", ".mjs", ".ts", ".tsx", ".jsx",
    ".rs", ".sh", ".ps1", ".psm1", ".yaml", ".yml", ".toml", ".json",
    ".html", ".css", ".sql", ".manifest", ".plist", ".service",
}

SKIP_DIRS = {
    ".git", "node_modules", ".venv", "venv", "__pycache__", "dist",
    "release", "build", ".icns_build", "site-packages",
}

# Files whose contents intentionally contain the broken spellings
# (repair-map sources), or that define the rebrand itself.
SKIP_FILES = {
    "scripts/fix_desktop_identifiers.py",
    "scripts/fix_rebrand_identifiers_sweep.py",
}

# Rule 1: identifier char directly before "Berdaya Agent".
RE_BEFORE = re.compile(r"(?<=[A-Za-z0-9_$])Berdaya Agent")
# Rule 2: "Berdaya Agent" directly followed by an identifier char.
RE_AFTER = re.compile(r"Berdaya Agent(?=[A-Za-z0-9_$])")


def fix_text(text: str) -> str:
    text = RE_BEFORE.sub("Hermes", text)
    text = RE_AFTER.sub("Hermes", text)
    return text


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    changed: list[tuple[Path, int]] = []

    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in CODE_EXTS:
            continue
        rel = path.relative_to(ROOT)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if str(rel).replace("\\", "/") in SKIP_FILES:
            continue

        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if "Berdaya Agent" not in text:
            continue

        fixed = fix_text(text)
        if fixed != text:
            n = len(RE_BEFORE.findall(text)) + len(RE_AFTER.findall(text))
            changed.append((rel, n))
            if not dry_run:
                path.write_text(fixed, encoding="utf-8", newline="")

    label = "Would fix" if dry_run else "Fixed"
    for rel, n in sorted(changed):
        print(f"{label} {rel} ({n} occurrence(s))")
    print(f"\n{label} {sum(n for _, n in changed)} occurrence(s) in {len(changed)} file(s).")


if __name__ == "__main__":
    main()
