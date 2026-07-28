#!/usr/bin/env python3
"""Verify an installed Codex Self Growing Memory setup."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    import tomllib
except ImportError:
    tomllib = None

PLUGIN_NAME = "codex-self-growing-memory"
BEGIN_MARKER = "<!-- BEGIN codex-self-growing-memory -->"
END_MARKER = "<!-- END codex-self-growing-memory -->"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify the installed memory mechanism.")
    parser.add_argument("--home", type=Path)
    parser.add_argument("--codex-home", type=Path)
    parser.add_argument("--vault", type=Path)
    return parser.parse_args()


def check(name: str, ok: bool, detail: str = "") -> dict[str, Any]:
    return {"check": name, "ok": bool(ok), "detail": detail}


def read_runtime(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def active_global_agents(codex: Path) -> Path:
    override = codex / "AGENTS.override.md"
    try:
        if override.is_file() and override.read_text(encoding="utf-8").strip():
            return override
    except OSError:
        pass
    return codex / "AGENTS.md"


def configured_hook_events(path: Path) -> set[str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()
    hooks = data.get("hooks", {}) if isinstance(data, dict) else {}
    if not isinstance(hooks, dict):
        return set()
    found: set[str] = set()
    for event, groups in hooks.items():
        if not isinstance(groups, list):
            continue
        for group in groups:
            handlers = group.get("hooks", []) if isinstance(group, dict) else []
            if any(
                isinstance(handler, dict)
                and PLUGIN_NAME in str(handler.get("command", ""))
                for handler in handlers
            ):
                found.add(event)
                break
    return found


def simulate_hook(
    hook: Path, event: str, input_data: dict[str, Any], codex: Path, plugin_root: Path
) -> tuple[bool, str]:
    env = os.environ.copy()
    env["CODEX_HOME"] = str(codex)
    env["PLUGIN_ROOT"] = str(plugin_root)
    try:
        result = subprocess.run(
            [sys.executable, str(hook), event],
            input=json.dumps(input_data, ensure_ascii=False),
            text=True,
            capture_output=True,
            timeout=10,
            env=env,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return False, str(error)
    if result.returncode != 0:
        return False, result.stderr.strip()
    try:
        output = json.loads(result.stdout or "{}")
    except json.JSONDecodeError:
        return False, "hook output is not JSON"
    if not isinstance(output, dict):
        return False, "hook output is not an object"
    return True, result.stdout.strip()[:400]


def main() -> int:
    args = parse_args()
    home = (args.home or Path.home()).expanduser().resolve()
    codex = (args.codex_home or home / ".codex").expanduser().resolve()
    runtime_path = codex / f"{PLUGIN_NAME}.json"
    runtime = read_runtime(runtime_path)
    vault = (
        args.vault
        or (Path(runtime["vault_path"]) if isinstance(runtime.get("vault_path"), str) else None)
    )
    plugin_root = home / "plugins" / PLUGIN_NAME
    marketplace = home / ".agents" / "plugins" / "marketplace.json"
    checks: list[dict[str, Any]] = []

    config_path = codex / "config.toml"
    config_ok = False
    config_detail = ""
    if config_path.is_file():
        text = config_path.read_text(encoding="utf-8")
        if tomllib is not None:
            try:
                data = tomllib.loads(text)
                config_ok = (
                    data.get("features", {}).get("memories") is True
                    and data.get("features", {}).get("hooks") is True
                    and data.get("memories", {}).get("generate_memories") is True
                    and data.get("memories", {}).get("use_memories") is True
                )
            except Exception as error:
                config_detail = str(error)
        else:
            config_ok = all(
                token in text
                for token in (
                    "[features]",
                    "memories = true",
                    "[memories]",
                    "generate_memories = true",
                    "use_memories = true",
                )
            )
    checks.append(check("native_memories_config", config_ok, config_detail))

    agents_path = active_global_agents(codex)
    agents_text = agents_path.read_text(encoding="utf-8") if agents_path.is_file() else ""
    checks.append(
        check(
            "global_agents_auto_load",
            BEGIN_MARKER in agents_text and END_MARKER in agents_text,
            str(agents_path),
        )
    )
    checks.append(check("runtime_config", bool(runtime), str(runtime_path)))
    checks.append(check("plugin_manifest", (plugin_root / ".codex-plugin" / "plugin.json").is_file(), str(plugin_root)))

    user_hooks = codex / "hooks.json"
    hook_events = configured_hook_events(user_hooks)
    required_hook_events = {"SessionStart", "UserPromptSubmit", "SessionEnd"}
    checks.append(
        check(
            "user_hooks_auto_load",
            required_hook_events.issubset(hook_events),
            f"{user_hooks}: {', '.join(sorted(hook_events))}",
        )
    )
    hook = codex / PLUGIN_NAME / "memory_hook.py"
    checks.append(check("user_hook_runtime", hook.is_file(), str(hook)))

    marketplace_ok = False
    if marketplace.is_file():
        try:
            data = json.loads(marketplace.read_text(encoding="utf-8"))
            marketplace_ok = any(
                isinstance(item, dict) and item.get("name") == PLUGIN_NAME
                for item in data.get("plugins", [])
            )
        except (OSError, json.JSONDecodeError):
            pass
    checks.append(check("personal_marketplace", marketplace_ok, str(marketplace)))

    vault_ok = bool(vault and Path(vault).is_dir())
    checks.append(check("knowledge_base", vault_ok, str(vault) if vault else "not configured"))
    if vault_ok:
        required = [
            "START-HERE.md",
            "AGENTS.md",
            "08-System/决策记录.md",
            "08-System/防踩坑记录.md",
        ]
        checks.append(
            check(
                "knowledge_base_structure",
                all((Path(vault) / relative).is_file() for relative in required),
                ", ".join(required),
            )
        )

    if hook.is_file():
        ok, detail = simulate_hook(
            hook,
            "session-start",
            {"source": "startup", "cwd": str(home)},
            codex,
            plugin_root,
        )
        checks.append(check("session_start_hook", ok, detail))
        ok, detail = simulate_hook(
            hook,
            "prompt",
            {"prompt": "检查防踩坑记录并继续已有项目", "cwd": str(home)},
            codex,
            plugin_root,
        )
        checks.append(check("prompt_retrieval_hook", ok, detail))
    else:
        checks.append(check("session_start_hook", False, "memory_hook.py missing"))
        checks.append(check("prompt_retrieval_hook", False, "memory_hook.py missing"))

    failed = [item for item in checks if not item["ok"]]
    zero_trigger_ok = not failed and required_hook_events.issubset(hook_events)
    result = {
        "status": "pass" if not failed else "fail",
        "plugin": PLUGIN_NAME,
        "zero_trigger_ready": zero_trigger_ok,
        "scope": "all new local Codex chats and projects using this CODEX_HOME",
        "checks": checks,
        "next": (
            [
                "Restart Codex.",
                "Review and trust the user-level hooks once.",
                "After trust is granted, new chats and projects require no trigger phrase.",
            ]
            if not failed
            else ["Fix only the failed checks, then run verify.py again."]
        ),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
