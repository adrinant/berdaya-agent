#!/usr/bin/env python3
"""One-shot rebrand: Berdaya Agent -> Berdaya Agent (protects model names and upstream URLs)."""

from __future__ import annotations

import re
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
    ".next",
    ".turbo",
    "coverage",
    ".mypy_cache",
    ".ruff_cache",
}

SKIP_FILES = {
    "uv.lock",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
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
    ".eot",
    ".pyc",
    ".pyo",
    ".so",
    ".dll",
    ".exe",
    ".zip",
    ".tar",
    ".gz",
    ".bz2",
    ".xz",
    ".whl",
    ".pdf",
    ".mp3",
    ".mp4",
    ".wav",
    ".bin",
    ".dat",
    ".sqlite",
    ".db",
}

# Protect Nous model IDs, model-family prose, and upstream repo URLs.
PROTECT_PATTERNS = [
    re.compile(r"Berdaya Agent-\d[\w.-]*"),
    re.compile(r"Hermes-4\.\d[\w.-]*"),
    re.compile(r"\bHermes\s+4\b"),
    re.compile(r"NousResearch/[Hh]ermes-[Aa]gent"),
    re.compile(r"github\.com/NousResearch/[Hh]ermes-[Aa]gent"),
]


def should_process(path: Path) -> bool:
    if path.name in SKIP_FILES:
        return False
    if path.suffix.lower() in BINARY_SUFFIXES:
        return False
    for part in path.parts:
        if part in SKIP_DIRS:
            return False
    return True


def rebrand_text(text: str) -> str:
    placeholders: dict[str, str] = {}

    def protect(match: re.Match[str]) -> str:
        key = f"__REBRAND_PROTECT_{len(placeholders)}__"
        placeholders[key] = match.group(0)
        return key

    for pattern in PROTECT_PATTERNS:
        text = pattern.sub(protect, text)

    text = text.replace("Berdaya Agent", "Berdaya Agent")
    text = text.replace("Berdaya Agent", "Berdaya Agent")

    for key, original in placeholders.items():
        text = text.replace(key, original)

    return text


def main() -> int:
    dry_run = "--dry-run" in sys.argv
    changed_files: list[Path] = []

    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or not should_process(path):
            continue
        try:
            original = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue

        updated = rebrand_text(original)
        if updated == original:
            continue

        changed_files.append(path)
        if not dry_run:
            path.write_text(updated, encoding="utf-8", newline="\n")

    mode = "Would update" if dry_run else "Updated"
    print(f"{mode} {len(changed_files)} files")
    for path in changed_files[:50]:
        print(f"  {path.relative_to(ROOT)}")
    if len(changed_files) > 50:
        print(f"  ... and {len(changed_files) - 50} more")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
