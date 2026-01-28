<p align="center">
  <img src="https://img.shields.io/badge/DeepSeek-V3%20%7C%20R1-00D4AA?style=for-the-badge&logo=openai&logoColor=white" alt="DeepSeek">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/PRs-Welcome-brightgreen?style=for-the-badge" alt="PRs Welcome">
</p>

<h1 align="center">Clawdbot DeepSeek</h1>

<p align="center">
  <strong>Your Personal AI Assistant Powered by DeepSeek</strong><br>
  <em>50x cheaper than GPT-4. Open source. Community-driven.</em>
</p>

<p align="center">
  <a href="#-quick-start">Quick Start</a> |
  <a href="#-features">Features</a> |
  <a href="#-why-deepseek">Why DeepSeek</a> |
  <a href="#-community">Community</a>
</p>

---

## What is Clawdbot DeepSeek?

Clawdbot DeepSeek is a **personal AI assistant framework** forked for the DeepSeek community. It's not just a chatbot - it's an agent that:

- **Remembers** conversations across sessions with persistent memory
- **Acts proactively** with heartbeats and scheduled tasks
- **Integrates** with WhatsApp, Telegram, Discord, and more
- **Costs pennies** compared to proprietary alternatives
- **Respects privacy** with local-first design

```
"Hey. I just came online. Who am I? Who are you?"
```

Your agent introduces itself, learns about you, and becomes genuinely useful over time.

---

## Why DeepSeek?

| Metric | DeepSeek V3 | GPT-4 | Claude 3.5 |
|--------|-------------|-------|------------|
| **Input Cost** | $0.14/1M tokens | $10/1M tokens | $3/1M tokens |
| **Output Cost** | $0.28/1M tokens | $30/1M tokens | $15/1M tokens |
| **Context Window** | 128K | 128K | 200K |
| **Open Weights** | Yes | No | No |
| **Coding Ability** | Excellent | Excellent | Excellent |

**Bottom line**: DeepSeek V3 delivers comparable quality at **~50x lower cost**.

### Models Supported

| Model | Use Case | Best For |
|-------|----------|----------|
| `deepseek-chat` | General assistant | Daily tasks, coding, writing |
| `deepseek-reasoner` | Complex reasoning | Math, logic, multi-step problems |

---

## Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/yksanjo/clawdbot-deepseek.git
cd clawdbot-deepseek

# Copy environment template
cp .env.example .env
```

### 2. Add Your API Key

Get your key at [platform.deepseek.com](https://platform.deepseek.com)

```bash
# Edit .env and add your key
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxx
```

### 3. Install & Test

```bash
# Install dependencies
pip install -r requirements.txt

# Test connection
python scripts/test_connection.py

# Start chatting!
python scripts/deepseek_client.py --agent
```

### 4. Personalize Your Agent

```bash
# Run the setup wizard
./setup.sh
```

Or manually edit:
- `workspace/SOUL.md` - Agent's personality and values
- `workspace/USER.md` - Your preferences and info
- `workspace/IDENTITY.md` - Give your agent a name!

---

## Features

### Persistent Memory

Your agent remembers across sessions:

```
workspace/
├── memory/
│   ├── 2025-01-28.md    # Today's conversations
│   ├── 2025-01-27.md    # Yesterday's context
│   └── ...
└── MEMORY.md            # Long-term curated memories
```

### Soul System

Define your agent's personality in `SOUL.md`:

```markdown
## Core Truths

**Be genuinely helpful, not performatively helpful.**
Skip the "Great question!" - just help.

**Have opinions.**
An assistant with no personality is just a search engine.
```

### Heartbeat System

Proactive task execution in `HEARTBEAT.md`:

```markdown
- [ ] Check email for urgent messages (every 4h)
- [ ] Review calendar for upcoming events
- [ ] Monitor project builds
```

### Multi-Platform Integration

| Platform | Status | Setup |
|----------|--------|-------|
| WhatsApp | Ready | QR code pairing |
| Telegram | Ready | BotFather token |
| Discord | Ready | Bot token |
| Slack | Ready | App installation |
| CLI | Ready | Built-in |

---

## Project Structure

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

## Configuration

### Basic Setup

```json
{
  "models": {
    "providers": {
      "deepseek": {
        "baseUrl": "https://api.deepseek.com/v1",
        "apiKey": "${DEEPSEEK_API_KEY}",
        "models": [
          {
            "id": "deepseek-chat",
            "name": "DeepSeek V3",
            "contextWindow": 128000
          }
        ]
      }
    }
  }
}
```

### Advanced: Multi-Model with Fallbacks

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "deepseek/deepseek-chat",
        "fallbacks": ["deepseek/deepseek-reasoner"]
      }
    }
  }
}
```

---

## Python Client Usage

### As a Library

```python
from scripts.deepseek_client import DeepSeekClient, ClawdbotAgent

# Simple chat
client = DeepSeekClient()
response = client.simple_chat("What is the capital of France?")

# With agent personality
agent = ClawdbotAgent(workspace_path="./workspace")
response = agent.chat("Help me write a Python function")

# Streaming
for chunk in client.chat(messages, stream=True):
    print(chunk, end="")

# Use R1 for reasoning
answer = client.reason("Solve: If 3x + 5 = 20, what is x?")
```

### CLI Usage

```bash
# Quick chat
python scripts/deepseek_client.py "What is quantum computing?"

# Agent mode (uses workspace personality)
python scripts/deepseek_client.py --agent

# Stream response
python scripts/deepseek_client.py --stream "Tell me a story"

# Use R1 reasoner
python scripts/deepseek_client.py --model deepseek-reasoner "Prove P != NP"
```

---

## Cost Calculator

| Usage | Tokens/Day | Daily Cost | Monthly Cost |
|-------|------------|------------|--------------|
| Light | 100K | $0.04 | $1.20 |
| Moderate | 500K | $0.21 | $6.30 |
| Heavy | 2M | $0.84 | $25.20 |

*Based on 50/50 input/output split with DeepSeek V3*

---

## Roadmap

- [x] Core agent framework
- [x] DeepSeek V3 integration
- [x] DeepSeek R1 (reasoner) support
- [x] Persistent memory system
- [x] Python client with streaming
- [ ] WhatsApp plugin
- [ ] Telegram plugin
- [ ] Discord plugin
- [ ] Voice support (ElevenLabs)
- [ ] Web dashboard
- [ ] Docker deployment
- [ ] Multi-agent orchestration

---

## Community

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

## Credits

- Original [Clawdbot](https://github.com/clawdbot) framework
- [DeepSeek](https://deepseek.com) for the incredible models
- The open-source AI community
- All contributors!

---

## License

MIT License - See [LICENSE](LICENSE) file

---

<p align="center">
  <strong>Built for the DeepSeek Community</strong><br>
  <em>Star this repo if you find it useful!</em>
</p>

<p align="center">
  <a href="https://github.com/yksanjo/clawdbot-deepseek/stargazers">
    <img src="https://img.shields.io/github/stars/yksanjo/clawdbot-deepseek?style=social" alt="Stars">
  </a>
  <a href="https://github.com/yksanjo/clawdbot-deepseek/network/members">
    <img src="https://img.shields.io/github/forks/yksanjo/clawdbot-deepseek?style=social" alt="Forks">
  </a>
</p>
