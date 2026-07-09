#!/usr/bin/env python3
"""Validate local environment for a community release."""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def require(name: str, aliases: tuple[str, ...] = ()) -> bool:
    names = (name, *aliases)
    if any(os.getenv(item) for item in names):
        print(f"ok: {' or '.join(names)} is set")
        return True
    print(f"missing: {' or '.join(names)}")
    return False


def main() -> int:
    provider = os.getenv("AI_PROVIDER", "deepseek")
    transport = os.getenv("COMMUNITY_TRANSPORT", "telegram")
    print(f"provider: {provider}")
    print(f"transport: {transport}")

    checks = []
    if transport != "telegram":
        print("unsupported transport: only telegram is enabled for this release")
        checks.append(False)
    else:
        checks.append(require("TELEGRAM_BOT_TOKEN"))

    if provider == "kimi":
        checks.append(require("KIMI_API_KEY", ("MOONSHOT_API_KEY",)))
    else:
        checks.append(require("DEEPSEEK_API_KEY"))

    try:
        import flask  # noqa: F401
        import requests  # noqa: F401

        print("ok: runtime dependencies import")
        checks.append(True)
    except ImportError as exc:
        print(f"missing dependency: {exc}")
        checks.append(False)

    workspace = Path(os.getenv("WORKSPACE_PATH", ROOT / "workspace"))
    try:
        (workspace / "app_requests").mkdir(parents=True, exist_ok=True)
        print(f"ok: workspace writable at {workspace}")
        checks.append(True)
    except OSError as exc:
        print(f"workspace not writable: {exc}")
        checks.append(False)

    if all(checks):
        print("release check passed")
        return 0

    print("release check failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
