#!/bin/bash
# Railway Deployment Script for Clawdbot DeepSeek

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║     🚀 Deploying Clawdbot DeepSeek to Railway              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check Railway CLI
if ! command -v railway &> /dev/null; then
    echo -e "${YELLOW}Installing Railway CLI...${NC}"
    npm install -g @railway/cli
fi

# Load API key from .env
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

AI_PROVIDER="${AI_PROVIDER:-deepseek}"
if [ "$AI_PROVIDER" = "kimi" ]; then
    PROVIDER_KEY="${KIMI_API_KEY:-$MOONSHOT_API_KEY}"
    PROVIDER_KEY_NAME="KIMI_API_KEY or MOONSHOT_API_KEY"
else
    PROVIDER_KEY="$DEEPSEEK_API_KEY"
    PROVIDER_KEY_NAME="DEEPSEEK_API_KEY"
fi

if [ -z "$PROVIDER_KEY" ]; then
    echo "$PROVIDER_KEY_NAME not found in .env"
    exit 1
fi

echo -e "${GREEN}Provider key loaded${NC}"
COMMUNITY_TRANSPORT="${COMMUNITY_TRANSPORT:-telegram}"
if [ "$COMMUNITY_TRANSPORT" = "telegram" ] && [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo -e "${YELLOW}TELEGRAM_BOT_TOKEN not found; add it before starting the worker.${NC}"
fi

# Step 1: Login
echo ""
echo -e "${BLUE}Step 1: Login to Railway${NC}"
echo "This will open a browser for authentication..."
railway login

# Step 2: Initialize project
echo ""
echo -e "${BLUE}Step 2: Initialize Project${NC}"
read -p "Create new project? (y/n): " create_new

if [ "$create_new" = "y" ]; then
    railway init
else
    railway link
fi

# Step 3: Set environment variables
echo ""
echo -e "${BLUE}Step 3: Setting Environment Variables${NC}"
railway variables set AI_PROVIDER="$AI_PROVIDER"
railway variables set COMMUNITY_TRANSPORT="$COMMUNITY_TRANSPORT"
if [ "$AI_PROVIDER" = "kimi" ]; then
    [ -n "$KIMI_API_KEY" ] && railway variables set KIMI_API_KEY="$KIMI_API_KEY"
    [ -n "$MOONSHOT_API_KEY" ] && railway variables set MOONSHOT_API_KEY="$MOONSHOT_API_KEY"
else
    railway variables set DEEPSEEK_API_KEY="$DEEPSEEK_API_KEY"
    railway variables set DEEPSEEK_BASE_URL="${DEEPSEEK_BASE_URL:-https://api.deepseek.com/v1}"
    railway variables set DEEPSEEK_MODEL="${DEEPSEEK_MODEL:-deepseek-v4-flash}"
    railway variables set DEEPSEEK_REASONING_MODEL="${DEEPSEEK_REASONING_MODEL:-deepseek-v4-pro}"
fi
[ -n "$TELEGRAM_BOT_TOKEN" ] && railway variables set TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN"
railway variables set TELEGRAM_REQUIRE_COMMAND="${TELEGRAM_REQUIRE_COMMAND:-false}"
railway variables set WORKSPACE_PATH="/data/workspace"
railway variables set PORT="5000"
echo -e "${GREEN}✓ Variables set${NC}"

# Step 4: Add persistent volume
echo ""
echo -e "${BLUE}Step 4: Creating Volume${NC}"
echo "Go to Railway Dashboard → Your Project → Settings → Volumes"
echo "Add a volume with mount path: /data/workspace"
echo ""
read -p "Press Enter after creating the volume..."

# Step 5: Deploy
echo ""
echo -e "${BLUE}Step 5: Deploying...${NC}"
railway up

# Step 6: Show status
echo ""
echo -e "${GREEN}✓ Deployment Complete!${NC}"
echo ""
railway status

# Get domain
echo ""
echo -e "${BLUE}Your app is live at:${NC}"
railway domain

echo ""
echo "🎉 Access your Clawdbot at the URL above!"
echo ""
echo "Telegram worker start command:"
echo "  python plugins/telegram_bot.py"
