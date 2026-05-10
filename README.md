# clawdbot-deepseek

A self-hostable personal AI chatbot with persistent memory. Flask
API + DeepSeek backend. Roughly the architecture of a paid memory
chat app, runnable on your own infrastructure for the cost of
DeepSeek API calls (~$0.14 per million tokens).

```bash
docker build -t clawdbot .
docker run -p 5000:5000 -e DEEPSEEK_API_KEY=sk-... clawdbot
```

[![License](https://img.shields.io/github/license/yksanjo/clawdbot-deepseek)](LICENSE)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Status](https://img.shields.io/badge/status-beta-orange)

---

## What it is

A Flask web service that wraps a DeepSeek chat agent with:

- **Persistent conversation memory** stored on disk (the workspace
  directory), so the assistant remembers previous turns across
  sessions and process restarts.
- **REST API** for sending chat messages and streaming responses.
- **Embedded web UI** (single-file HTML, no separate frontend build)
  for browser use.
- **Deploy configs** for Railway, Render, Fly.io, and plain Docker.

## Why

- **Cost.** DeepSeek pricing is ~1–2% of frontier model pricing, so
  running your own assistant against the DeepSeek API typically costs
  cents per day at hobbyist usage.
- **Self-hostable.** Your conversation history stays on your server.
  No third party can read it.
- **Hackable.** Single-file Flask app (`app.py`), straightforward
  DeepSeek client wrapper (`scripts/deepseek_client.py`), small
  surface area to extend.

## Honest limitations

- **Memory is a flat conversation log, not RAG or vector search.** It
  preserves message history; it does not retrieve semantically.
  Adding retrieval (Chroma, sqlite-vss, etc.) is straightforward but
  not implemented.
- **No authentication on the API.** Anyone with the URL can chat.
  Production deployments must add an auth layer (reverse proxy with
  basic auth, an API key check, or OAuth).
- **Single-user model.** State is stored per-workspace, not
  per-user.
- **Quality gap vs frontier models.** DeepSeek V3-class is excellent
  for the price, but trails Claude / GPT-4 on complex reasoning.

## Quick start

### Local (Python)

```bash
git clone https://github.com/yksanjo/clawdbot-deepseek.git
cd clawdbot-deepseek
pip install -r requirements.txt
export DEEPSEEK_API_KEY=sk-...
python app.py
# Browser: http://localhost:5000
```

### Docker

```bash
docker build -t clawdbot .
docker run -p 5000:5000 -e DEEPSEEK_API_KEY=sk-... clawdbot
```

### Hosted (Railway / Render / Fly.io)

See `DEPLOY.md`. The repo ships with `railway.toml`, `render.yaml`,
`fly.toml`, and `Procfile` for the major hosts. All require
`DEEPSEEK_API_KEY` as an environment variable.

## API

```bash
# Send a message
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "remember that my favorite color is blue"}'

# Stream a response (Server-Sent Events)
curl -N -X POST http://localhost:5000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "what is my favorite color?"}'

# Health check
curl http://localhost:5000/health
```

## Architecture

```
.
├── app.py                       # Flask server, routes, web UI
├── scripts/
│   ├── deepseek_client.py       # DeepSeek API wrapper
│   │                            # ChatResponse, ClawdbotAgent class
│   └── test_connection.py       # API smoke test
├── tools/                       # Tool plugins (extension point)
├── workspace/                   # Persistent state (conversation log)
├── Dockerfile                   # Multi-stage Docker build
└── {fly,railway,render}.toml    # Host-specific deploy configs
```

## Cost reference

For a chatty personal assistant (~50 turns/day, ~500 tokens in /
~300 tokens out per turn):

- DeepSeek: ~$0.01/day → ~$0.30/month
- Claude Sonnet equivalent: ~$1.25/day → ~$37/month

For most personal-assistant workloads, the cost is rounding noise.

## Contributing

PRs welcome. See `CONTRIBUTING.md`. Particularly useful additions:

- Vector/retrieval memory (Chroma, sqlite-vss, or pgvector).
- Authentication middleware (API key, OAuth, or a Cloudflare Access
  pattern).
- Tool-use loop (currently the agent is conversational only).

## License

MIT. See `LICENSE`.

## Disclosures

Developed with assistance from AI coding tools.
