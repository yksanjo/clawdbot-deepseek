# Community Release

Use this runbook to put Clawdbot in a Telegram community.

## 1. Create The Telegram Bot

1. Open Telegram.
2. Message `@BotFather`.
3. Run `/newbot`.
4. Follow the prompts and copy the bot token.
5. Optional: add the bot to your group.

For groups, BotFather privacy mode can stay enabled if you only want command
messages such as `/app`, `/a`, and `/requests` to reach the bot. Disable privacy
mode if you want the agent to read normal group comments and participate when useful.

## 2. Configure Secrets

Update `.env` locally or your host's environment variables:

```bash
AI_PROVIDER=deepseek
COMMUNITY_TRANSPORT=telegram
DEEPSEEK_API_KEY=sk-your-fresh-deepseek-key
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-v4-flash
DEEPSEEK_REASONING_MODEL=deepseek-v4-pro
AI_REQUEST_TIMEOUT_SECONDS=45

TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_REQUIRE_COMMAND=false
TELEGRAM_PARTICIPATION_MODE=smart
TELEGRAM_TRIGGER_NAMES=-agent,agent,breakout,breakout agent,clawdbot
TELEGRAM_AI_MAX_TOKENS=900
TELEGRAM_DROP_PENDING_UPDATES_ON_START=true
```

Optional safety limits:

```bash
TELEGRAM_ALLOWED_CHAT_IDS=123456789,-1001234567890
TELEGRAM_MAX_INPUT_CHARS=3500
TELEGRAM_SMART_REPLY_COOLDOWN_SECONDS=180
TELEGRAM_DEBUG_MESSAGES=false
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

Start the Telegram worker:

```bash
.venv/bin/python plugins/telegram_bot.py
```

In Telegram:

```text
/ping
/a what can you do?
/b what should we ship next?
/app build a waitlist page for our community app
/requests
agent: summarize the last few comments
-agent summarize the last few comments
```

## 4. Deploy

Recommended first release: Railway or a small VPS.

Railway worker start command:

```bash
python plugins/telegram_bot.py
```

Railway web API start command, if you also want the web chat/API:

```bash
python app.py
```

Set these variables in the host dashboard:

```text
AI_PROVIDER
COMMUNITY_TRANSPORT
DEEPSEEK_API_KEY
DEEPSEEK_BASE_URL
DEEPSEEK_MODEL
DEEPSEEK_REASONING_MODEL
TELEGRAM_BOT_TOKEN
TELEGRAM_REQUIRE_COMMAND
TELEGRAM_PARTICIPATION_MODE
WORKSPACE_PATH
```

Use `WORKSPACE_PATH=/data/workspace` when the host has a persistent volume.

Fly.io process scale after deploy:

```bash
fly scale count app=1 worker=1
```

## 5. Community Safety Defaults

- The Telegram bot supports `/app`, `/build`, `/a`, `/ask`, `/requests`, `/ping`, and direct callouts like `-agent` or `agent:`.
- In groups, use BotFather `/setprivacy` -> select bot -> `Disable` if you want it to read all normal comments.
- `TELEGRAM_PARTICIPATION_MODE=smart` listens to comments but replies only when addressed or when a relevant group question appears.
- App requests are captured as specs in `workspace/app_requests/`.
- Automatic app builds are disabled by default.
- Do not enable `APP_REQUEST_AUTOBUILD=true` until the build command is approval-gated.
