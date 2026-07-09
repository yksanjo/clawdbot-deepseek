#!/usr/bin/env python3
"""
Telegram community bot for Clawdbot.

Required env:
- TELEGRAM_BOT_TOKEN
- DEEPSEEK_API_KEY or KIMI_API_KEY/MOONSHOT_API_KEY
"""

import os
import re
import sys
import time
from collections import defaultdict, deque
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
PARTICIPATION_MODE = os.getenv("TELEGRAM_PARTICIPATION_MODE", "smart").lower()
SMART_REPLY_COOLDOWN_SECONDS = int(
    os.getenv("TELEGRAM_SMART_REPLY_COOLDOWN_SECONDS", "180")
)
TRIGGER_NAMES = tuple(
    item.strip().lower()
    for item in os.getenv(
        "TELEGRAM_TRIGGER_NAMES",
        "-agent,agent,breakout,breakout agent,clawdbot",
    ).split(",")
    if item.strip()
)
SMART_KEYWORDS = tuple(
    item.strip().lower()
    for item in os.getenv(
        "TELEGRAM_SMART_KEYWORDS",
        "agent,bot,ai,app,build,ship,launch,code,bug,idea,telegram,community",
    ).split(",")
    if item.strip()
)
CONTEXT_MESSAGES = int(os.getenv("TELEGRAM_CONTEXT_MESSAGES", "12"))
AI_MAX_TOKENS = int(os.getenv("TELEGRAM_AI_MAX_TOKENS", "900"))
DROP_PENDING_UPDATES_ON_START = os.getenv(
    "TELEGRAM_DROP_PENDING_UPDATES_ON_START",
    "true",
).lower() in {
    "1",
    "true",
    "yes",
}
DEBUG_MESSAGES = os.getenv("TELEGRAM_DEBUG_MESSAGES", "false").lower() in {
    "1",
    "true",
    "yes",
}
EMPTY_DIRECT_PROMPT = "Briefly introduce yourself and explain the shortest ways this Telegram group can call you."


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
        self.bot_id: Optional[int] = None
        self.username: Optional[str] = None
        self.contexts = defaultdict(lambda: deque(maxlen=CONTEXT_MESSAGES))
        self.last_smart_reply_at: dict[int, float] = {}

    def run(self) -> None:
        me = self._request("getMe")
        self.bot_id = me.get("id")
        self.username = me.get("username")
        self._set_commands()
        if DROP_PENDING_UPDATES_ON_START:
            self._request("deleteWebhook", {"drop_pending_updates": True}, timeout=15)
            if DEBUG_MESSAGES:
                print("telegram dropped pending updates on startup", flush=True)
        print(f"Clawdbot Telegram bot online as @{self.username}", flush=True)

        offset: Optional[int] = None
        while True:
            try:
                updates = self._request(
                    "getUpdates",
                    {
                        "timeout": POLL_TIMEOUT,
                        "offset": offset,
                        "allowed_updates": [
                            "message",
                            "edited_message",
                            "channel_post",
                            "edited_channel_post",
                        ],
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
        message = (
            update.get("message")
            or update.get("edited_message")
            or update.get("channel_post")
            or update.get("edited_channel_post")
            or {}
        )
        if DEBUG_MESSAGES:
            update_types = ",".join(key for key in update.keys() if key != "update_id")
            print(
                f"telegram update id={update.get('update_id')} types={update_types}",
                flush=True,
            )
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
        if user.get("is_bot"):
            return

        requester = self._requester_name(user)
        chat_type = chat.get("type", "private")
        is_group = chat_type in {"group", "supergroup"}
        self._debug_message(chat_id, requester, text)
        self._remember_context(chat_id, requester, text)

        command, command_text, addressed_to_this_bot = self._parse_command(text)
        if command and not addressed_to_this_bot:
            return

        if command in {"start", "help"}:
            self._send(
                chat_id,
                (
                    "Online. Use /a for quick asks, /app for build requests, "
                    "/requests for recent specs, or reply to me directly."
                ),
            )
            return

        if command in {"ping", "p"}:
            self._send(chat_id, "online")
            return

        if command in {"requests", "r"}:
            self._send(chat_id, self._recent_requests())
            return

        if command in {"app", "build", "make"} or is_app_request(text):
            self._capture_app_request(
                chat_id,
                command_text if command else text,
                requester,
                message,
            )
            return

        if command in {"ask", "a", "b", "agent", "ag", "talk"}:
            if command_text:
                self._chat(chat_id, command_text[:MAX_INPUT_CHARS], requester, message)
            else:
                self._send(chat_id, "Usage: /agent what should we build next?")
            return

        direct_text = self._directed_text(text, message)
        if direct_text is not None:
            prompt = direct_text.strip() or EMPTY_DIRECT_PROMPT
            self._chat(chat_id, prompt[:MAX_INPUT_CHARS], requester, message)
            return

        if REQUIRE_COMMAND:
            return

        if not is_group:
            self._chat(chat_id, text[:MAX_INPUT_CHARS])
            return

        if PARTICIPATION_MODE == "all":
            self._chat(chat_id, text[:MAX_INPUT_CHARS], requester, message)
            return

        if PARTICIPATION_MODE == "smart" and self._should_smart_reply(chat_id, text):
            self._chat(chat_id, text[:MAX_INPUT_CHARS], requester, message)

    def _requester_name(self, user: dict[str, Any]) -> str:
        username = user.get("username")
        if username:
            return f"@{username}"
        full_name = " ".join(
            part for part in [user.get("first_name"), user.get("last_name")] if part
        ).strip()
        return full_name or str(user.get("id", "telegram-user"))

    def _parse_command(self, text: str) -> tuple[Optional[str], str, bool]:
        first, _, rest = text.partition(" ")
        if not first.startswith("/"):
            return None, text, True

        raw_command = first[1:]
        command, _, target = raw_command.partition("@")
        command = command.lower()

        if target and self.username and target.lower() != self.username.lower():
            return command, rest.strip(), False

        return command, rest.strip(), True

    def _directed_text(self, text: str, message: dict[str, Any]) -> Optional[str]:
        reply = message.get("reply_to_message") or {}
        reply_user = reply.get("from") or {}
        if self.bot_id and reply_user.get("id") == self.bot_id:
            return text

        entity_text = self._directed_text_from_entities(text, message)
        if entity_text is not None:
            return entity_text

        if self.username:
            mention = f"@{self.username}".lower()
            if mention in text.lower():
                return re.sub(re.escape(mention), "", text, flags=re.IGNORECASE).strip()

        stripped = text.strip()
        lowered = stripped.lower()
        for name in TRIGGER_NAMES:
            pattern = rf"^(hey\s+)?{re.escape(name)}\b[:,\-\s]*(.*)$"
            match = re.match(pattern, lowered, flags=re.IGNORECASE)
            if match:
                return stripped[match.start(2):].strip()

        return None

    def _directed_text_from_entities(
        self,
        text: str,
        message: dict[str, Any],
    ) -> Optional[str]:
        entities = message.get("entities") or []
        for entity in entities:
            entity_type = entity.get("type")
            offset = entity.get("offset")
            length = entity.get("length")
            if not isinstance(offset, int) or not isinstance(length, int):
                continue

            if entity_type == "mention" and self.username:
                value = text[offset:offset + length]
                if value.lower() == f"@{self.username.lower()}":
                    return (text[:offset] + text[offset + length:]).strip()

            if entity_type == "text_mention" and self.bot_id:
                mentioned_user = entity.get("user") or {}
                if mentioned_user.get("id") == self.bot_id:
                    return (text[:offset] + text[offset + length:]).strip()

        return None

    def _should_smart_reply(self, chat_id: int, text: str) -> bool:
        now = time.time()
        last_reply = self.last_smart_reply_at.get(chat_id, 0)
        if now - last_reply < SMART_REPLY_COOLDOWN_SECONDS:
            return False

        lowered = text.lower()
        asks_group_question = lowered.endswith("?") or lowered.startswith(
            ("can we ", "should we ", "how do we ", "what if ", "why don't we ")
        )
        relevant = any(keyword in lowered for keyword in SMART_KEYWORDS)
        if asks_group_question and relevant:
            self.last_smart_reply_at[chat_id] = now
            return True
        return False

    def _remember_context(self, chat_id: int, requester: str, text: str) -> None:
        self.contexts[chat_id].append(f"{requester}: {text}")

    def _debug_message(self, chat_id: int, requester: str, text: str) -> None:
        if not DEBUG_MESSAGES:
            return
        preview = re.sub(r"\s+", " ", text).strip()[:160]
        print(
            f"telegram message chat={chat_id} requester={requester} text={preview}",
            flush=True,
        )

    def _context_prompt(self, chat_id: int, requester: str, text: str) -> str:
        recent = list(self.contexts[chat_id])[-CONTEXT_MESSAGES:]
        if not recent:
            return text
        context = "\n".join(recent)
        return f"""You are participating in a Telegram group.
Be concise, useful, and natural. Do not reply like a helpdesk unless asked.
Use the recent context only to answer the latest message.

Recent context:
{context}

Latest message from {requester}:
{text}"""

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

    def _chat(
        self,
        chat_id: int,
        text: str,
        requester: str = "telegram-user",
        message: Optional[dict[str, Any]] = None,
    ) -> None:
        if DEBUG_MESSAGES:
            preview = re.sub(r"\s+", " ", text).strip()[:160]
            print(f"telegram ai start chat={chat_id} text={preview}", flush=True)
        try:
            response = self.agent.chat(
                self._context_prompt(chat_id, requester, text),
                max_tokens=AI_MAX_TOKENS,
            )
            if DEBUG_MESSAGES:
                print(
                    f"telegram ai done chat={chat_id} chars={len(response)}",
                    flush=True,
                )
        except Exception as exc:
            response = f"AI provider error: {exc}"
            if DEBUG_MESSAGES:
                print(f"telegram ai error chat={chat_id} error={exc}", flush=True)
        self._send(chat_id, response, reply_to_message_id=(message or {}).get("message_id"))

    def _send(
        self,
        chat_id: int,
        text: str,
        reply_to_message_id: Optional[int] = None,
    ) -> None:
        remaining = text.strip() or "Done."
        while remaining:
            chunk = remaining[:3900]
            remaining = remaining[3900:]
            payload = {
                "chat_id": chat_id,
                "text": chunk,
                "disable_web_page_preview": True,
            }
            if reply_to_message_id:
                payload["reply_to_message_id"] = reply_to_message_id
                payload["allow_sending_without_reply"] = True
            if DEBUG_MESSAGES:
                print(
                    "telegram send "
                    f"chat={chat_id} reply_to={reply_to_message_id} chars={len(chunk)}",
                    flush=True,
                )
            self._request("sendMessage", payload)

    def _set_commands(self) -> None:
        commands = [
            {"command": "a", "description": "Ask the agent"},
            {"command": "b", "description": "Ask Breakout"},
            {"command": "agent", "description": "Ask the agent"},
            {"command": "ag", "description": "Ask the agent"},
            {"command": "talk", "description": "Talk to the agent"},
            {"command": "ask", "description": "Ask the agent"},
            {"command": "app", "description": "Capture an app request"},
            {"command": "build", "description": "Capture a build request"},
            {"command": "requests", "description": "Show recent app requests"},
            {"command": "ping", "description": "Check bot health"},
            {"command": "help", "description": "Show usage"},
        ]
        try:
            self._request("setMyCommands", {"commands": commands})
        except Exception as exc:
            print(f"Failed to set Telegram commands: {exc}", flush=True)


def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required.")
    TelegramBot(token).run()


if __name__ == "__main__":
    main()
