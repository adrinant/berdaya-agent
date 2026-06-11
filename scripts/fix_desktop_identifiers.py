#!/usr/bin/env python3
"""Restore internal Hermes* identifiers broken by bulk Berdaya Agent text replace."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Longest matches first.
IDENTIFIER_FIXES = [
    ("launchBerdaya AgentDesktop", "launchHermesDesktop"),
    ("startingBerdaya AgentDesktop", "startingHermesDesktop"),
    ("getBerdaya AgentConfigDefaults", "getHermesConfigDefaults"),
    ("getBerdaya AgentConfigRecord", "getHermesConfigRecord"),
    ("getBerdaya AgentConfigSchema", "getHermesConfigSchema"),
    ("refreshBerdaya AgentConfig", "refreshHermesConfig"),
    ("checkBerdaya AgentUpdate", "checkHermesUpdate"),
    ("getBerdaya AgentConfig", "getHermesConfig"),
    ("saveBerdaya AgentConfig", "saveHermesConfig"),
    ("updateBerdaya Agent:", "updateHermes:"),
    ("updateBerdaya Agent", "updateHermes"),
    ("useBerdaya AgentConfig", "useHermesConfig"),
    ("canImportBerdaya AgentCli", "canImportHermesCli"),
    ("verifyBerdaya AgentCli", "verifyHermesCli"),
    ("resolveBerdaya AgentCliBinary", "resolveHermesCliBinary"),
    ("resolveBerdaya AgentBackend", "resolveHermesBackend"),
    ("resolveBerdaya AgentVersion", "resolveHermesVersion"),
    ("resolveBerdaya AgentCwd", "resolveHermesCwd"),
    ("resetBerdaya AgentConnection", "resetHermesConnection"),
    ("isBerdaya AgentSourceRoot", "isHermesSourceRoot"),
    ("venvBerdaya AgentShimPath", "venvHermesShimPath"),
    ("recentBerdaya AgentLog", "recentHermesLog"),
    ("initialBerdaya AgentDesktop", "initialHermesDesktop"),
    ("Berdaya AgentSyntaxHighlighterProps", "HermesSyntaxHighlighterProps"),
    ("Berdaya AgentReadDirResult", "HermesReadDirResult"),
    ("Berdaya AgentReadDirEntry", "HermesReadDirEntry"),
    ("Berdaya AgentConfigRecord", "HermesConfigRecord"),
    ("Berdaya AgentGateway", "HermesGateway"),
    ("Berdaya AgentConnection", "HermesConnection"),
    ("Berdaya AgentConfig", "HermesConfig"),
    ("Berdaya AgentRefType", "HermesRefType"),
    ("resolveBerdayaHome", "resolveHermesHome"),
]

TARGET_DIRS = [
    ROOT / "apps" / "desktop",
    ROOT / "apps" / "bootstrap-installer",
]

SKIP_SUFFIXES = {".png", ".jpg", ".ico", ".webp", ".woff", ".woff2", ".ttf", ".exe", ".dll"}


def main() -> None:
    changed = 0
    for base in TARGET_DIRS:
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix.lower() in SKIP_SUFFIXES:
                continue
            if "node_modules" in path.parts or "release" in path.parts or "dist" in path.parts:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            orig = text
            for old, new in IDENTIFIER_FIXES:
                text = text.replace(old, new)
            if text != orig:
                path.write_text(text, encoding="utf-8", newline="\n")
                changed += 1
                print(path.relative_to(ROOT))
    print(f"Fixed {changed} files")


if __name__ == "__main__":
    main()
