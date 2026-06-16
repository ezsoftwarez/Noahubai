#!/usr/bin/env python3
"""Setup.exe — install / refresh AI Hub on Disc B (PyInstaller)."""
from __future__ import annotations

import ctypes
import os
import shutil
import sys
from pathlib import Path

SKIP_NAMES = {"setup", "__pycache__", ".git"}
SKIP_SUFFIX = {".pyc"}


def package_root() -> Path:
    exe = Path(sys.executable).resolve()
    parent = exe.parent
    if parent.name.lower() == "setup":
        return parent.parent
    return parent


def default_target() -> Path:
    return Path(r"B:\AI HUB oVerk1LL")


def should_skip(path: Path) -> bool:
    if path.name.lower() in SKIP_NAMES:
        return True
    if path.suffix.lower() in SKIP_SUFFIX:
        return True
    return False


def copy_tree(src: Path, dst: Path) -> int:
    n = 0
    for item in src.iterdir():
        if should_skip(item):
            continue
        dest = dst / item.name
        if item.is_dir():
            if dest.exists():
                n += copy_tree(item, dest)
            else:
                shutil.copytree(item, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
                n += 1
        else:
            dst.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dest)
            n += 1
    return n


def msgbox(text: str, title: str = "AI Hub Setup", flags: int = 0x40) -> None:
    try:
        ctypes.windll.user32.MessageBoxW(0, text, title, flags)
    except Exception:
        print(text)


def main() -> None:
    src = package_root()
    tgt = default_target()
    if not src.is_dir():
        msgbox("Install package folder not found.\nExtract AI HUB v1.zip first.", "AI Hub Setup", 0x10)
        sys.exit(1)
    try:
        tgt.mkdir(parents=True, exist_ok=True)
        copy_tree(src, tgt)
        note = tgt / "VERSION-oVerk1LL.txt"
        if not note.is_file():
            note.write_text(
                "AI Hub installed by Setup.exe\nTarget: " + str(tgt) + "\n",
                encoding="utf-8",
            )
        msgbox(
            "AI Hub installed to:\n" + str(tgt) + "\n\n"
            "Run:\n  " + str(tgt / "Setup" / "AI HUB.exe") + "\n"
            "or RUN-AI-HUB.bat",
            "AI Hub Setup",
        )
    except OSError as e:
        msgbox("Setup failed:\n" + str(e), "AI Hub Setup", 0x10)
        sys.exit(1)


if __name__ == "__main__":
    main()
