#!/usr/bin/env python3
"""
Telegram community bot for Clawdbot.

Required env:
- TELEGRAM_BOT_TOKEN
- DEEPSEEK_API_KEY or KIMI_API_KEY/MOONSHOT_API_KEY
"""

import os
import sys
import time
from pathlib import Path
from typing import Any, Optional

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.app_requests import AppRequestStore, is_app_request, strip_app_prefix
from scripts.deepseek_client import ClawdbotAgent


load_dotenv(ROOT / ".env")

WORKSPACE_PATH = os.getenv("WORKSPACE_PATH", str(ROOT / "workspace"))
MAX_INPUT_CHARS = int(os.getenv("TELEGRAM_MAX_INPUT_CHARS", "3500"))
POLL_TIMEOUT = int(os.getenv("TELEGRAM_POLL_TIMEOUT", "30"))
REQUIRE_COMMAND = os.getenv("TELEGRAM_REQUIRE_COMMAND", "false").lower() in {
    "1",
    "true",
    "yes",
}


def _ids_from_env(name: str) -> set[int]:
    raw = os.getenv(name, "")
    ids = set()
    for part in raw.split(","):
        part = part.strip()
        if part.lstrip("-").isdigit():
            ids.add(int(part))
    return ids


ALLOWED_CHAT_IDS = _ids_from_env("TELEGRAM_ALLOWED_CHAT_IDS")


class TelegramBot:
    def __init__(self, token: str):
        self.token = token
        self.api_url = f"https://api.telegram.org/bot{token}"
        self.session = requests.Session()
        self.agent = ClawdbotAgent(workspace_path=WORKSPACE_PATH)
        self.app_requests = AppRequestStore(workspace_path=WORKSPACE_PATH)

    def run(self) -> None:
        me = self._request("getMe")
        username = me.get("username", "<unknown>")
        print(f"Clawdbot Telegram bot online as @{username}", flush=True)

        offset: Optional[int] = None
        while True:
            try:
                updates = self._request(
                    "getUpdates",
                    {
                        "timeout": POLL_TIMEOUT,
                        "offset": offset,
                        "allowed_updates": ["message"],
                    },
                    timeout=POLL_TIMEOUT + 10,
                )
                for update in updates:
                    offset = update["update_id"] + 1
                    self._handle_update(update)
            except KeyboardInterrupt:
                raise
            except Exception as exc:
                print(f"Telegram worker error: {exc}", flush=True)
                time.sleep(5)

    def _request(
        self,
        method: str,
        payload: Optional[dict[str, Any]] = None,
        timeout: int = 30,
    ) -> Any:
        response = self.session.post(
            f"{self.api_url}/{method}",
            json=payload or {},
            timeout=timeout,
        )
        response.raise_for_status()
        data = response.json()
        if not data.get("ok"):
            raise RuntimeError(data)
        return data.get("result")

    def _handle_update(self, update: dict[str, Any]) -> None:
        message = update.get("message") or {}
        chat = message.get("chat") or {}
        chat_id = chat.get("id")
        if chat_id is None:
            return
        if ALLOWED_CHAT_IDS and chat_id not in ALLOWED_CHAT_IDS:
            return

        text = (message.get("text") or "").strip()
        if not text:
            return

        user = message.get("from") or {}
        requester = self._requester_name(user)

        if text.startswith("/start"):
            self._send(
                chat_id,
                "Online. Send /app followed by an app idea, /requests for recent specs, or a normal message to chat.",
            )
            return

        if text.startswith("/ping"):
            self._send(chat_id, "online")
            return

        if text.startswith("/requests"):
            self._send(chat_id, self._recent_requests())
            return

        if text.startswith("/app") or is_app_request(text):
            self._capture_app_request(chat_id, text, requester, message)
            return

        if REQUIRE_COMMAND and not text.startswith("/ask"):
            return

        if text.startswith("/ask"):
            text = text[len("/ask"):].strip()

        if text:
            self._chat(chat_id, text[:MAX_INPUT_CHARS])

    def _requester_name(self, user: dict[str, Any]) -> str:
        username = user.get("username")
        if username:
            return f"@{username}"
        full_name = " ".join(
            part for part in [user.get("first_name"), user.get("last_name")] if part
        ).strip()
        return full_name or str(user.get("id", "telegram-user"))

    def _capture_app_request(
        self,
        chat_id: int,
        text: str,
        requester: str,
        message: dict[str, Any],
    ) -> None:
        description = strip_app_prefix(text)
        if not description:
            self._send(chat_id, "Usage: /app build a ...")
            return

        request = self.app_requests.create(
            description[:MAX_INPUT_CHARS],
            requester,
            f"telegram:{chat_id}",
            {
                "message_id": message.get("message_id"),
                "chat_id": chat_id,
            },
        )
        self._send(
            chat_id,
            (
                f"Captured app request {request.request_id}: {request.title}\n"
                "I saved the build spec for maintainer review before any code runs."
            ),
        )

    def _recent_requests(self) -> str:
        recent = self.app_requests.list_recent(limit=5)
        if not recent:
            return "No app requests captured yet."
        lines = ["Recent app requests:"]
        for request in recent:
            lines.append(f"- {request.request_id} - {request.title}")
        return "\n".join(lines)

    def _chat(self, chat_id: int, text: str) -> None:
        try:
            response = self.agent.chat(text)
        except Exception as exc:
            response = f"AI provider error: {exc}"
        self._send(chat_id, response)

    def _send(self, chat_id: int, text: str) -> None:
        remaining = text.strip() or "Done."
        while remaining:
            chunk = remaining[:3900]
            remaining = remaining[3900:]
            self._request(
                "sendMessage",
                {
                    "chat_id": chat_id,
                    "text": chunk,
                    "disable_web_page_preview": True,
                },
            )


def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required.")
    TelegramBot(token).run()


if __name__ == "__main__":
    main()
