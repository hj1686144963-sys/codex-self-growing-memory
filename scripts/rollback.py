#!/usr/bin/env python3
"""Restore the pre-install state from a recorded backup."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

PLUGIN_NAME = "codex-self-growing-memory"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rollback the memory plugin installation.")
    parser.add_argument("--latest", action="store_true", help="Restore the newest backup.")
    parser.add_argument("--backup", type=Path, help="Restore a specific backup directory.")
    parser.add_argument("--home", type=Path)
    parser.add_argument("--codex-home", type=Path)
    return parser.parse_args()


def remove_path(path: Path) -> None:
    if not path.exists():
        return
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()


def restore(source: Path, destination: Path, existed: bool) -> None:
    if existed:
        if not source.exists():
            raise RuntimeError(f"Backup is incomplete: {source}")
        remove_path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, destination)
        else:
            shutil.copy2(source, destination)
    else:
        remove_path(destination)


def main() -> int:
    args = parse_args()
    home = (args.home or Path.home()).expanduser().resolve()
    codex = (args.codex_home or home / ".codex").expanduser().resolve()
    backup_root = codex / "backups" / PLUGIN_NAME
    if args.backup:
        backup = args.backup.expanduser().resolve()
    elif args.latest:
        backups = sorted(path for path in backup_root.iterdir() if path.is_dir()) if backup_root.is_dir() else []
        if not backups:
            raise RuntimeError(f"No backups found under {backup_root}")
        backup = backups[-1]
    else:
        raise RuntimeError("Use --latest or --backup PATH.")

    state_path = backup / "state.json"
    state: dict[str, Any] = json.loads(state_path.read_text(encoding="utf-8"))
    paths = state.get("paths", {})
    existed = state.get("existed", {})
    global_guidance = Path(paths["Global guidance"])
    targets = {
        "config": (backup / "config.toml", Path(paths["Codex config"])),
        "agents": (backup / global_guidance.name, global_guidance),
        "hooks": (backup / "hooks.json", Path(paths["User hooks"])),
        "hook_runtime": (backup / "hook-runtime", Path(paths["Hook runtime"])),
        "runtime": (backup / f"{PLUGIN_NAME}.json", Path(paths["Runtime config"])),
        "marketplace": (backup / "marketplace.json", Path(paths["Personal marketplace"])),
        "plugin": (backup / "plugin", Path(paths["Plugin"])),
    }
    for name, (source, destination) in targets.items():
        restore(source, destination, bool(existed.get(name)))

    print(
        json.dumps(
            {
                "status": "rolled_back",
                "backup": str(backup),
                "knowledge_base_preserved": paths.get("Knowledge base"),
                "next": ["Restart Codex."],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
