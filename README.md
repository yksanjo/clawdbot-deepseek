# Clawdbot DeepSeek

An AI assistant agent powered by **DeepSeek** - forked from Clawdbot for the DeepSeek community.

## What is This?

Clawdbot DeepSeek is a personal AI assistant framework that:
- Uses **DeepSeek V3** (deepseek-chat) as its brain
- Maintains **persistent memory** across sessions
- Supports **proactive tasks** via heartbeats and cron
- Integrates with **messaging platforms** (WhatsApp, Telegram, Discord)
- Works with **OpenAI-compatible APIs**

## Why DeepSeek?

- **Cost-effective**: Significantly cheaper than GPT-4/Claude for comparable quality
- **Fast**: Low latency responses
- **Open weights**: DeepSeek models are open source
- **128K context**: Large context window for complex tasks
- **Great coding**: Excellent at programming tasks

## Quick Start

### 1. Get Your DeepSeek API Key

Sign up at [platform.deepseek.com](https://platform.deepseek.com) and get your API key.

### 2. Set Up Environment

```bash
# Clone this repo
git clone https://github.com/YOUR_USERNAME/clawdbot-deepseek.git
cd clawdbot-deepseek

# Copy environment template
cp .env.example .env

# Add your DeepSeek API key
echo "DEEPSEEK_API_KEY=your_api_key_here" >> .env
```

### 3. Configure the Agent

Edit `config/clawdbot-deepseek.json` and add your API key:

```json
{
  "models": {
    "providers": {
      "deepseek": {
        "apiKey": "YOUR_DEEPSEEK_API_KEY"
      }
    }
  }
}
```

### 4. Initialize Your Agent

Run the setup wizard to personalize your agent:

```bash
./setup.sh
```

Or manually review and customize:
- `workspace/SOUL.md` - Agent personality
- `workspace/USER.md` - Your preferences
- `workspace/IDENTITY.md` - Agent's name and vibe

## Project Structure

```
clawdbot-deepseek/
├── config/
│   └── clawdbot-deepseek.json    # Main configuration
├── workspace/                     # Agent's home
│   ├── SOUL.md                   # Personality & values
│   ├── AGENTS.md                 # Operating instructions
│   ├── USER.md                   # Info about you
│   ├── IDENTITY.md               # Agent's identity
│   ├── TOOLS.md                  # Local tool notes
│   ├── HEARTBEAT.md              # Proactive task config
│   └── memory/                   # Daily logs & long-term memory
├── plugins/                       # Integration plugins
├── scripts/                       # Utility scripts
├── .env.example                  # Environment template
└── README.md
```

## Configuration

### Model Settings

The default configuration uses `deepseek-chat` (DeepSeek V3):

```json
{
  "models": {
    "providers": {
      "deepseek": {
        "baseUrl": "https://api.deepseek.com/v1",
        "apiKey": "YOUR_API_KEY",
        "api": "openai-completions",
        "models": [
          {
            "id": "deepseek-chat",
            "name": "DeepSeek V3",
            "contextWindow": 128000,
            "maxTokens": 8192
          }
        ]
      }
    }
  }
}
```

### Adding DeepSeek Reasoner (R1)

For advanced reasoning tasks, add the reasoner model:

```json
{
  "id": "deepseek-reasoner",
  "name": "DeepSeek R1",
  "reasoning": true,
  "contextWindow": 64000,
  "maxTokens": 8192
}
```

### Multi-Model Setup

You can configure fallbacks for reliability:

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

## Features

### Persistent Memory

The agent maintains memory across sessions:
- **Daily logs**: `memory/YYYY-MM-DD.md` for raw session notes
- **Long-term memory**: `MEMORY.md` for curated important info

### Heartbeat System

Configure proactive checks in `HEARTBEAT.md`:
- Check emails
- Monitor calendars
- Track project status
- Custom periodic tasks

### Messaging Integrations

Supported platforms:
- WhatsApp (via plugin)
- Telegram (via BotFather)
- Discord (via bot token)
- Slack (via app)

## API Costs

DeepSeek V3 pricing (as of Jan 2025):
- Input: $0.14 / 1M tokens (cache hit: $0.014)
- Output: $0.28 / 1M tokens

This makes it **~50x cheaper** than GPT-4 for most tasks.

## Comparison

| Feature | Clawdbot DeepSeek | Original (Qwen) |
|---------|-------------------|-----------------|
| Model | DeepSeek V3 | Qwen |
| Cost | Very Low | Free (portal) |
| Speed | Fast | Fast |
| Context | 128K | 128K |
| Reasoning | R1 available | Limited |

## Community

This is a community fork for DeepSeek users. Contributions welcome!

- Report issues on GitHub
- Share your configurations
- Contribute plugins
- Improve documentation

## Credits

- Original [Clawdbot](https://github.com/clawdbot) framework
- [DeepSeek](https://deepseek.com) for the amazing models
- The open-source AI community

## License

MIT License - See LICENSE file
