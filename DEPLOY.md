# 🚀 Clawdbot DeepSeek - Deployment Guide

Deploy your AI assistant with persistent memory to the cloud!

## Quick Start

```bash
# 1. Set your DeepSeek API key
export DEEPSEEK_API_KEY=sk-your-key-here

# 2. Run the deployment script
./deploy.sh

# 3. Choose your platform (1-5)
```

## Platform Options

### 1. Railway (⭐ Recommended)

**Best for:** Beginners, quick deployment, free tier ($5 credit)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

**Features:**
- ✅ Easiest setup
- ✅ Automatic HTTPS
- ✅ Persistent volumes
- ✅ Git-based deployments
- ✅ $5/month free credit

**Pricing:** ~$5-10/mo for typical usage

---

### 2. Render

**Best for:** Free tier, simple apps

```bash
# Deploy via Blueprint
# 1. Push to GitHub
# 2. Go to https://dashboard.render.com/blueprints
# 3. Connect repo
```

**Features:**
- ✅ Free tier available
- ✅ Automatic deploys
- ✅ Blueprint configuration
- ⚠️ Free tier sleeps after inactivity

**Pricing:** Free tier available, $7/mo for standard

---

### 3. Fly.io

**Best for:** Performance, global edge deployment

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Deploy
fly launch
fly deploy
```

**Features:**
- ✅ Edge deployment (fast globally)
- ✅ Low cost
- ✅ Docker-based
- ✅ Volumes for persistence

**Pricing:** ~$2-5/mo for typical usage

---

### 4. Docker (Self-Hosted)

**Best for:** Full control, VPS deployment

```bash
# Build and run
docker build -t clawdbot-deepseek .
docker run -d \
  -p 8080:8080 \
  -e DEEPSEEK_API_KEY=$DEEPSEEK_API_KEY \
  -v $(pwd)/workspace:/data/workspace \
  clawdbot-deepseek
```

**Features:**
- ✅ Run anywhere
- ✅ Full control
- ✅ Portable

**Pricing:** Cost of VPS ($5-20/mo)

---

### 5. Local Development

```bash
# Install dependencies
pip install -r requirements-deploy.txt

# Run server
python app.py

# Access at http://localhost:5000
```

---

## API Endpoints

Once deployed, your API is available at:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web UI |
| `/health` | GET | Health check |
| `/api/chat` | POST | Send message |
| `/api/reason` | POST | Use R1 reasoner |
| `/api/memory` | GET | List memory files |
| `/api/memory/<file>` | GET | Get memory content |
| `/api/personality` | GET | Get personality files |

### Example API Calls

```bash
# Chat
curl -X POST https://your-app.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'

# Reasoning (R1)
curl -X POST https://your-app.com/api/reason \
  -H "Content-Type: application/json" \
  -d '{"message": "Solve: 3x + 5 = 20"}'

# Get memory files
curl https://your-app.com/api/memory
```

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DEEPSEEK_API_KEY` | ✅ | - | Your DeepSeek API key |
| `WORKSPACE_PATH` | ❌ | `./workspace` | Path to workspace files |
| `PORT` | ❌ | `5000` | Server port |

---

## File Structure After Deployment

```
/workspace                    # Persistent volume
├── SOUL.md                  # Agent personality
├── IDENTITY.md              # Agent identity
├── USER.md                  # User profile
├── AGENTS.md                # Instructions
├── memory/                  # Conversation history
│   ├── 2025-01-28.md
│   └── ...
└── ...
```

---

## Troubleshooting

### Health Check Failing
```bash
# Check logs
docker logs clawdbot  # For Docker
railway logs          # For Railway
fly logs              # For Fly.io
```

### API Key Issues
- Ensure `DEEPSEEK_API_KEY` is set correctly
- Verify key at https://platform.deepseek.com

### Memory Not Persisting
- Check `WORKSPACE_PATH` is set correctly
- Verify volume is mounted (Docker/Fly)
- Check file permissions

---

## Need Help?

- [DeepSeek API Docs](https://platform.deepseek.com)
- [Railway Docs](https://docs.railway.app)
- [Render Docs](https://render.com/docs)
- [Fly.io Docs](https://fly.io/docs)

---

## Cost Comparison

| Platform | Monthly Cost | Free Tier | Persistence |
|----------|-------------|-----------|-------------|
| Railway | $5-10 | $5 credit | ✅ |
| Render | $0-7 | ✅ | ✅ |
| Fly.io | $2-5 | ❌ | ✅ |
| VPS (Docker) | $5-20 | ❌ | ✅ |

---

Happy deploying! 🚀
