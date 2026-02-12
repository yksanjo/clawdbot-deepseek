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

if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "❌ DEEPSEEK_API_KEY not found in .env"
    exit 1
fi

echo -e "${GREEN}✓ API Key loaded${NC}"

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
railway variables set DEEPSEEK_API_KEY="$DEEPSEEK_API_KEY"
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
