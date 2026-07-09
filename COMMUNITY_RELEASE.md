# Community Release

Use this runbook to put Clawdbot in a Discord community.

## 1. Create The Discord Bot

1. Open the Discord Developer Portal.
2. Create a new application.
3. Add a bot user.
4. Enable `Message Content Intent` for the bot.
5. Copy the bot token.
6. Invite the bot to your server with these permissions:
   - View Channels
   - Send Messages
   - Read Message History

Invite URL format:

```text
https://discord.com/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=3072&scope=bot
```

## 2. Configure Secrets

Update `.env` locally or your host's environment variables:

```bash
AI_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-your-fresh-deepseek-key
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-v4-flash
DEEPSEEK_REASONING_MODEL=deepseek-v4-pro

DISCORD_BOT_TOKEN=your_discord_bot_token
DISCORD_COMMAND_PREFIX=!
DISCORD_REQUIRE_MENTION=true
```

Optional safety limits:

```bash
DISCORD_ALLOWED_GUILD_IDS=123456789012345678
DISCORD_APP_REQUEST_CHANNEL_IDS=123456789012345678
DISCORD_MAX_INPUT_CHARS=3500
```

Optional Kimi routing for app specs:

```bash
APP_REQUEST_PROVIDER=kimi
APP_REQUEST_MODEL=kimi-k2.7-code
KIMI_API_KEY=sk-your-kimi-key
```

## 3. Validate Locally

```bash
cd /Users/yoshikondo/clawdbot-deepseek
python3.11 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/release_check.py
.venv/bin/python scripts/test_connection.py
```

Start the Discord worker:

```bash
.venv/bin/python plugins/discord_bot.py
```

In Discord:

```text
!ping
@YourBot what can you do?
!app build a waitlist page for our community app
!requests
```

## 4. Deploy

Recommended first release: Railway or a small VPS.

Railway worker start command:

```bash
python plugins/discord_bot.py
```

Railway web API start command, if you also want the web chat/API:

```bash
python app.py
```

Set these variables in the host dashboard:

```text
AI_PROVIDER
DEEPSEEK_API_KEY
DEEPSEEK_BASE_URL
DEEPSEEK_MODEL
DEEPSEEK_REASONING_MODEL
DISCORD_BOT_TOKEN
DISCORD_REQUIRE_MENTION
WORKSPACE_PATH
```

Use `WORKSPACE_PATH=/data/workspace` when the host has a persistent volume.

Fly.io process scale after deploy:

```bash
fly scale count app=1 worker=1
```

## 5. Community Safety Defaults

- The bot only replies in server channels when mentioned or when commands are used.
- App requests are captured as specs in `workspace/app_requests/`.
- Automatic app builds are disabled by default.
- Do not enable `APP_REQUEST_AUTOBUILD=true` until the build command is approval-gated.
