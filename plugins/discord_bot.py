#!/usr/bin/env python3
"""
Discord community bot for Clawdbot.

Required env:
- DISCORD_BOT_TOKEN
- DEEPSEEK_API_KEY or KIMI_API_KEY/MOONSHOT_API_KEY
"""

import asyncio
import os
import sys
from pathlib import Path

import discord
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.app_requests import AppRequestStore, is_app_request, strip_app_prefix
from scripts.deepseek_client import ClawdbotAgent


load_dotenv(ROOT / ".env")

WORKSPACE_PATH = os.getenv("WORKSPACE_PATH", str(ROOT / "workspace"))
COMMAND_PREFIX = os.getenv("DISCORD_COMMAND_PREFIX", "!")
REQUIRE_MENTION = os.getenv("DISCORD_REQUIRE_MENTION", "true").lower() in {
    "1",
    "true",
    "yes",
}
MAX_INPUT_CHARS = int(os.getenv("DISCORD_MAX_INPUT_CHARS", "3500"))


def _ids_from_env(name: str) -> set[int]:
    raw = os.getenv(name, "")
    ids = set()
    for part in raw.split(","):
        part = part.strip()
        if part.isdigit():
            ids.add(int(part))
    return ids


ALLOWED_GUILD_IDS = _ids_from_env("DISCORD_ALLOWED_GUILD_IDS")
APP_REQUEST_CHANNEL_IDS = _ids_from_env("DISCORD_APP_REQUEST_CHANNEL_IDS")


intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

agent = ClawdbotAgent(workspace_path=WORKSPACE_PATH)
app_requests = AppRequestStore(workspace_path=WORKSPACE_PATH)


def _allowed_guild(message: discord.Message) -> bool:
    if message.guild is None:
        return True
    if not ALLOWED_GUILD_IDS:
        return True
    return message.guild.id in ALLOWED_GUILD_IDS


def _clean_message(message: discord.Message) -> str:
    content = message.content.strip()
    if client.user:
        content = content.replace(f"<@{client.user.id}>", "")
        content = content.replace(f"<@!{client.user.id}>", "")
    return content.strip()


def _should_answer(message: discord.Message, text: str) -> bool:
    if message.guild is None:
        return True
    if message.channel.id in APP_REQUEST_CHANNEL_IDS and is_app_request(text):
        return True
    if client.user and client.user in message.mentions:
        return True
    if text.startswith(f"{COMMAND_PREFIX}ask "):
        return True
    if text.startswith(f"{COMMAND_PREFIX}app "):
        return True
    if text.startswith(f"{COMMAND_PREFIX}requests"):
        return True
    return not REQUIRE_MENTION


async def _send_chunks(channel: discord.abc.Messageable, text: str) -> None:
    chunks = []
    remaining = text.strip()
    while remaining:
        chunks.append(remaining[:1900])
        remaining = remaining[1900:]
    for chunk in chunks or ["Done."]:
        await channel.send(chunk)


async def _handle_app_request(message: discord.Message, text: str) -> None:
    description = strip_app_prefix(text)
    if not description:
        await message.channel.send(f"Usage: `{COMMAND_PREFIX}app build a ...`")
        return

    async with message.channel.typing():
        request = await asyncio.to_thread(
            app_requests.create,
            description[:MAX_INPUT_CHARS],
            str(message.author),
            f"discord:{message.channel.id}",
            {
                "message_id": message.id,
                "channel_id": message.channel.id,
                "guild_id": message.guild.id if message.guild else None,
            },
        )

    response = (
        f"Captured app request `{request.request_id}`: **{request.title}**\n"
        "I saved the build spec for maintainer review before any code runs."
    )
    await _send_chunks(message.channel, response)


async def _handle_recent_requests(message: discord.Message) -> None:
    recent = await asyncio.to_thread(app_requests.list_recent, 5)
    if not recent:
        await message.channel.send("No app requests captured yet.")
        return
    lines = ["Recent app requests:"]
    for request in recent:
        lines.append(f"- `{request.request_id}` - {request.title}")
    await _send_chunks(message.channel, "\n".join(lines))


async def _handle_chat(message: discord.Message, text: str) -> None:
    if text.startswith(f"{COMMAND_PREFIX}ask "):
        text = text[len(f"{COMMAND_PREFIX}ask "):].strip()
    if not text:
        return

    async with message.channel.typing():
        response = await asyncio.to_thread(agent.chat, text[:MAX_INPUT_CHARS])
    await _send_chunks(message.channel, response)


@client.event
async def on_ready() -> None:
    user = client.user
    print(f"Clawdbot Discord bot online as {user} ({user.id if user else 'unknown'})")


@client.event
async def on_message(message: discord.Message) -> None:
    if message.author.bot or not _allowed_guild(message):
        return

    text = _clean_message(message)
    if not text:
        return

    if text == f"{COMMAND_PREFIX}ping":
        await message.channel.send("online")
        return

    if not _should_answer(message, text):
        return

    if text.startswith(f"{COMMAND_PREFIX}requests"):
        await _handle_recent_requests(message)
        return

    if text.startswith(f"{COMMAND_PREFIX}app ") or is_app_request(text):
        await _handle_app_request(message, text)
        return

    await _handle_chat(message, text)


def main() -> None:
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        raise RuntimeError("DISCORD_BOT_TOKEN is required.")
    client.run(token)


if __name__ == "__main__":
    main()
