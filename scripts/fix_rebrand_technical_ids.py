#!/usr/bin/env python3
"""Fix technical identifiers broken by naive Hermes -> Berdaya Agent replacement."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SKIP_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    ".pytest_cache",
    "__pycache__",
    "dist",
    "build",
}

BINARY_SUFFIXES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".woff",
    ".woff2",
    ".ttf",
    ".pyc",
    ".pyo",
    ".so",
    ".dll",
    ".exe",
    ".zip",
    ".tar",
    ".gz",
    ".whl",
    ".pdf",
    ".mp3",
    ".mp4",
    ".sqlite",
    ".db",
}

# Order matters: longer / more specific replacements first.
REPLACEMENTS = [
    ("X-Berdaya-Session-Key", "X-Berdaya-Session-Key"),
    ("X-Berdaya-Session-Id", "X-Berdaya-Session-Id"),
    ("Berdaya-Agent/", "Berdaya-Agent/"),
    ("Berdaya Agent-tools-as-MCP", "Berdaya-tools-as-MCP"),
    ("Berdaya Agent-tools", "Berdaya-tools"),
    ("Berdaya Agent-managed", "Berdaya-managed"),
    ("Berdaya Agent-internal", "Berdaya-internal"),
    ("Berdaya Agent-specific", "Berdaya-specific"),
    ("Berdaya Agent-compatible", "Berdaya-compatible"),
    ("Berdaya Agent-created", "Berdaya-created"),
    ("Berdaya Agent-canonical", "Berdaya-canonical"),
    ("Berdaya Agent-wire-shape", "Berdaya-wire-shape"),
    ("Berdaya Agent-generated", "Berdaya-generated"),
    ("Berdaya Agent-side", "Berdaya-side"),
    ("Berdaya Agent-on-top", "Berdaya-on-top"),
    ("Berdaya Agent-Setup", "Berdaya-Setup"),
    ("Berdaya Agent-Update", "Berdaya-Update"),
    ("Berdaya Agent-${version}", "Berdaya-${version}"),
    ("Berdaya Agent-Katalog", "Berdaya-Agent-Katalog"),
    ("Berdaya Agent-Befehle", "Berdaya-Agent-Befehle"),
    ("Berdaya Agent-Gateway-Status", "Berdaya-Agent-Gateway-Status"),
    ("Berdaya Agent-Sitzung", "Berdaya-Agent-Sitzung"),
    ("Berdaya Agent-Team", "Berdaya-AI-Team"),
    ("Berdaya Agent-Plugins", "Berdaya-Agent-Plugins"),
    ("Berdaya Agent-Abzeichen", "Berdaya-Agent-Abzeichen"),
    ("Berdaya Agent-jelvények", "Berdaya-Agent-jelvények"),
    ("Berdaya Agent-bővítmények", "Berdaya-Agent-bővítmények"),
    ("Berdaya Agent-tool", "Berdaya-tool"),
    ("Berdaya Agent-Specific", "Berdaya-Specific"),
    ("Nous Research Berdaya Agent 3 / Hermes 4", "Nous Research Hermes 3 / Hermes 4"),
    ("Nous Berdaya Agent 3/4", "Nous Hermes 3/4"),
    ("Berdaya Agent 3/4", "Hermes 3/4"),
    ("Berdaya Agent 3", "Hermes 3"),
    ("Berdaya Agent Kanban", "Berdaya Kanban"),
    ("Open Berdaya Agent Kanban", "Open Berdaya Kanban"),
    ("Berdaya Agent Kanban documentation", "Berdaya Kanban documentation"),
    ("Hermes Kanban", "Berdaya Kanban"),
    ("Berdaya Agent-Monitor/", "Berdaya-Monitor/"),
    ("Berdaya Agent-Specific Setup", "Berdaya-Specific Setup"),
]


def should_process(path: Path) -> bool:
    if path.suffix.lower() in BINARY_SUFFIXES:
        return False
    for part in path.parts:
        if part in SKIP_DIRS:
            return False
    return True


def fix_text(text: str) -> str:
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    return text


def main() -> int:
    dry_run = "--dry-run" in sys.argv
    changed: list[Path] = []

    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or not should_process(path):
            continue
        if path.name in {"rebrand_hermes.py", "fix_rebrand_technical_ids.py"}:
            continue
        try:
            original = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        updated = fix_text(original)
        if updated == original:
            continue
        changed.append(path)
        if not dry_run:
            path.write_text(updated, encoding="utf-8", newline="\n")

    mode = "Would fix" if dry_run else "Fixed"
    print(f"{mode} {len(changed)} files")
    for path in changed[:40]:
        print(f"  {path.relative_to(ROOT)}")
    if len(changed) > 40:
        print(f"  ... and {len(changed) - 40} more")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
