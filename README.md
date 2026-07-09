<p align="center">
  <img src="https://img.shields.io/badge/DeepSeek-V3%20%7C%20R1-00D4AA?style=for-the-badge&logo=openai&logoColor=white" alt="DeepSeek">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/PRs-Welcome-brightgreen?style=for-the-badge" alt="PRs Welcome">
</p>

<h1 align="center">Clawdbot DeepSeek</h1>

<p align="center">
  <strong>Open-source alternative to $20/mo memory apps.</strong><br>
  <em>Persistent AI memory. Self-hosted. 50x cheaper than GPT-4.</em><br>
  <code>Your AI that actually remembers.</code>
</p>

<p align="center">
  <a href="#-self-host-in-5-minutes">Quick Start</a> |
  <a href="#-why-clawdbot-vs-alternatives">Why Clawdbot</a> |
  <a href="#-the-problem--the-solution">Problem/Solution</a> |
  <a href="#-features">Features</a>
</p>

---

## 💰 The Problem / The Solution

### Before Clawdbot
```
You: "Remember the app idea I mentioned last week?"
ChatGPT: "I don't have memory of previous conversations."

You: "The meeting with Sarah about the Q3 budget..."
ChatGPT: "I don't have access to past conversations."

You: *Copy-pastes context for the 47th time*
```

### After Clawdbot
```
You: "What's the status of that app idea?"
Clawdbot: "You mean the habit tracker with AI coaching? 
          You wanted to start with the iOS prototype 
          and had concerns about the subscription model. 
          Want me to draft the MVP requirements?"

You: "Remind me about the Sarah meeting."
Clawdbot: "Budget review scheduled for tomorrow 2pm. 
          You were worried about the 15% overrun in 
          engineering costs. Want me to pull the numbers?"
```

**Persistent memory changes everything.**

---

## ⚡ Clawdbot vs Competitors

| Feature | Clawdbot DeepSeek | Mem.ai | Notion AI | ChatGPT Plus |
|---------|-------------------|--------|-----------|--------------|
| **Monthly Cost** | ~$1-5 | $20 | $20 | $20 |
| **Persistent Memory** | ✅ Unlimited | ✅ Yes | ⚠️ Limited | ⚠️ Limited |
| **Self-Hosted** | ✅ Yes | ❌ No | ❌ No | ❌ No |
| **Data Privacy** | ✅ Local | ❌ Cloud | ❌ Cloud | ❌ Cloud |
| **Open Source** | ✅ MIT | ❌ No | ❌ No | ❌ No |
| **Custom Personality** | ✅ Full control | ⚠️ Limited | ❌ No | ❌ No |
| **Proactive Tasks** | ✅ Heartbeats | ❌ No | ❌ No | ❌ No |
| **WhatsApp/Telegram** | ✅ Built-in | ⚠️ Limited | ❌ No | ❌ No |

---

## 🎯 Why Clawdbot vs Alternatives

### vs Mem.ai
- **Mem.ai**: $20/mo, your data in their cloud, limited integrations
- **Clawdbot**: Self-hosted, data stays on your machine, unlimited custom integrations

### vs Notion AI
- **Notion AI**: $20/mo, tied to documents, no persistent conversation memory
- **Clawdbot**: True conversational memory, not document-based, learns over time

### vs ChatGPT Plus
- **ChatGPT Plus**: $20/mo, memory limited to specific facts, no proactive capabilities
- **Clawdbot**: Full conversation history, proactive heartbeats, 50x cheaper API costs

### vs Building Your Own
- **From scratch**: Weeks of development, API integration headaches, memory management complexity
- **Clawdbot**: Clone and run in 5 minutes, battle-tested memory system, active community

---

## 🚀 Self-Host in 5 Minutes

### Step 1: Clone & Setup (1 min)
```bash
git clone https://github.com/yksanjo/clawdbot-deepseek.git
cd clawdbot-deepseek
./setup.sh
```

### Step 2: Add API Key (1 min)
Get your key at [platform.deepseek.com](https://platform.deepseek.com) (free $5 credit)

```bash
# .env file is created automatically
# Just edit and add:
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxx
```

### Step 3: Start Chatting (30 sec)
```bash
python scripts/deepseek_client.py --agent
```

**Done!** Your AI assistant with persistent memory is now running.

---

## 💸 Cost Breakdown

### DeepSeek vs Competitors

| Metric | DeepSeek V3 | GPT-4 | Claude 3.5 |
|--------|-------------|-------|------------|
| **Input Cost** | $0.14/1M tokens | $10/1M tokens | $3/1M tokens |
| **Output Cost** | $0.28/1M tokens | $30/1M tokens | $15/1M tokens |
| **Context Window** | 128K | 128K | 200K |
| **Open Weights** | ✅ Yes | ❌ No | ❌ No |

**Bottom line**: DeepSeek V3 delivers comparable quality at **~50x lower cost**.

### Your Actual Monthly Cost

| Usage Level | Daily Tokens | Monthly Cost |
|-------------|--------------|--------------|
| **Light** (casual use) | 100K | ~$1.20 |
| **Moderate** (daily work) | 500K | ~$6.30 |
| **Heavy** (power user) | 2M | ~$25 |

Compare to: Mem.ai ($20), Notion AI ($20), ChatGPT Plus ($20) — all with **less memory capability**.

---

## ✨ Features

### 🧠 Persistent Memory
Your agent remembers across sessions:

```
workspace/
├── memory/
│   ├── 2025-01-28.md    # Today's conversations
│   ├── 2025-01-27.md    # Yesterday's context
│   └── ...
└── MEMORY.md            # Long-term curated memories
```

### 🎭 Soul System
Define your agent's personality in `SOUL.md`:

```markdown
## Core Truths

**Be genuinely helpful, not performatively helpful.**
Skip the "Great question!" - just help.

**Have opinions.**
An assistant with no personality is just a search engine.
```

### 💓 Heartbeat System
Proactive task execution in `HEARTBEAT.md`:

```markdown
- [ ] Check email for urgent messages (every 4h)
- [ ] Review calendar for upcoming events
- [ ] Monitor project builds
```

### 🔌 Multi-Platform Integration

| Platform | Status | Setup |
|----------|--------|-------|
| WhatsApp | ✅ Ready | QR code pairing |
| Telegram | ✅ Ready | BotFather token |
| Slack | ✅ Ready | App installation |
| CLI | ✅ Ready | Built-in |

---

## 📁 Project Structure

```
clawdbot-deepseek/
├── config/
│   └── clawdbot-deepseek.json    # DeepSeek API config
├── workspace/                     # Agent's home
│   ├── SOUL.md                   # Personality & values
│   ├── AGENTS.md                 # Operating instructions
│   ├── USER.md                   # About you
│   ├── IDENTITY.md               # Agent's identity
│   ├── TOOLS.md                  # Tool configurations
│   ├── HEARTBEAT.md              # Proactive tasks
│   ├── BOOTSTRAP.md              # First-run wizard
│   └── memory/                   # Persistent memory
├── scripts/
│   ├── deepseek_client.py        # Python client (CLI + lib)
│   └── test_connection.py        # Connection tester
├── plugins/                       # Platform integrations
├── setup.sh                      # Setup wizard
├── requirements.txt              # Dependencies
└── README.md
```

---

## 💻 Usage

For community deployment, see [COMMUNITY_RELEASE.md](COMMUNITY_RELEASE.md).

### 24/7 Telegram Community Bot

Clawdbot can run as a Telegram worker that replies to messages and captures app
requests with `/app`.

```bash
python3.11 -m venv .venv
.venv/bin/pip install -r requirements.txt

# .env
DEEPSEEK_API_KEY=sk-your-key
DEEPSEEK_MODEL=deepseek-v4-flash
COMMUNITY_TRANSPORT=telegram
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_REQUIRE_COMMAND=false

.venv/bin/python plugins/telegram_bot.py
```

Community app requests are saved under `workspace/app_requests/` as JSON and
Markdown specs. Use:

```text
/app build a landing page for our token with wallet connect and a waitlist
/requests
```

For coding-heavy spec generation, add a Kimi key and route app requests to Kimi:

```bash
KIMI_API_KEY=sk-your-kimi-key
APP_REQUEST_PROVIDER=kimi
APP_REQUEST_MODEL=kimi-k2.7-code
```

Automatic build execution is disabled by default. Only enable
`APP_REQUEST_AUTOBUILD=true` with an approval-gated command.

### CLI Quick Chat
```bash
# Quick question
python scripts/deepseek_client.py "What is quantum computing?"

# Agent mode with memory
python scripts/deepseek_client.py --agent

# Stream response
python scripts/deepseek_client.py --stream "Tell me a story"

# Use R1 for reasoning
python scripts/deepseek_client.py --model deepseek-reasoner "Solve this logic puzzle"
```

### Python Library
```python
from scripts.deepseek_client import DeepSeekClient, ClawdbotAgent

# Simple chat
client = DeepSeekClient()
response = client.simple_chat("What is the capital of France?")

# With persistent memory
agent = ClawdbotAgent(workspace_path="./workspace")
response = agent.chat("Help me write a Python function")

# Use R1 for reasoning
answer = client.reason("Solve: If 3x + 5 = 20, what is x?")
```

---

## 🔧 Personalization

### Give Your Agent a Name
Edit `workspace/IDENTITY.md`:
```markdown
# Name
Atlas

# Identity
Your helpful AI companion with persistent memory.
```

### Teach It About You
Edit `workspace/USER.md`:
```markdown
# About the User
- Software engineer focused on AI/ML
- Prefers concise answers
- Working on: open-source AI projects
```

### Define Its Personality
Edit `workspace/SOUL.md`:
```markdown
## Tone
Direct, helpful, occasionally witty.

## Values
- Truth over comfort
- Action over analysis
- Progress over perfection
```

---

## 🗺️ Roadmap

- [x] Core agent framework
- [x] DeepSeek V3 integration
- [x] DeepSeek R1 (reasoner) support
- [x] Persistent memory system
- [x] Python client with streaming
- [x] Telegram plugin
- [ ] WhatsApp plugin
- [ ] Voice support (ElevenLabs)
- [ ] Web dashboard
- [ ] Docker deployment
- [ ] Multi-agent orchestration

---

## 🤝 Community

This is a **community project** for DeepSeek users. We welcome:

- Bug reports and feature requests
- Plugin contributions
- Documentation improvements
- Sharing your agent configurations

### Contributing
```bash
# Fork the repo
git clone https://github.com/YOUR_USERNAME/clawdbot-deepseek.git

# Create a branch
git checkout -b feature/amazing-feature

# Make changes and commit
git commit -m "Add amazing feature"

# Push and create PR
git push origin feature/amazing-feature
```

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file

---

<p align="center">
  <strong>Stop paying $20/mo for AI memory that forgets.</strong><br>
  <em>Self-host Clawdbot and own your AI assistant.</em>
</p>

<p align="center">
  <a href="https://github.com/yksanjo/clawdbot-deepseek/stargazers">
    <img src="https://img.shields.io/github/stars/yksanjo/clawdbot-deepseek?style=social" alt="Stars">
  </a>
  <a href="https://github.com/yksanjo/clawdbot-deepseek/network/members">
    <img src="https://img.shields.io/github/forks/yksanjo/clawdbot-deepseek?style=social" alt="Forks">
  </a>
</p>
