#!/bin/bash
# Clawdbot DeepSeek - Deployment Script
# Supports: Railway, Render, Fly.io, Docker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║        Clawdbot DeepSeek - Deployment Script               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if DEEPSEEK_API_KEY is set
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo -e "${RED}❌ Error: DEEPSEEK_API_KEY is not set!${NC}"
    echo "Get your API key at: https://platform.deepseek.com"
    echo ""
    echo "Set it with:"
    echo "  export DEEPSEEK_API_KEY=your_key_here"
    exit 1
fi

echo -e "${GREEN}✓ DEEPSEEK_API_KEY is set${NC}"

# Function to deploy to Railway
deploy_railway() {
    echo -e "\n${BLUE}🚀 Deploying to Railway...${NC}"
    
    if ! command -v railway &> /dev/null; then
        echo -e "${YELLOW}⚠️  Railway CLI not found. Installing...${NC}"
        npm install -g @railway/cli
    fi
    
    echo "Logging in to Railway..."
    railway login
    
    echo "Initializing project..."
    railway init
    
    echo "Setting environment variables..."
    railway variables set DEEPSEEK_API_KEY="$DEEPSEEK_API_KEY"
    railway variables set WORKSPACE_PATH="/data/workspace"
    
    echo "Deploying..."
    railway up
    
    echo -e "${GREEN}✓ Deployment complete!${NC}"
    echo "Visit your dashboard: https://railway.app/dashboard"
}

# Function to deploy to Render
deploy_render() {
    echo -e "\n${BLUE}🚀 Deploying to Render...${NC}"
    
    echo -e "${YELLOW}Render uses 'render.yaml' for blueprint deployment.${NC}"
    echo ""
    echo "Steps:"
    echo "1. Push your code to GitHub"
    echo "2. Go to https://dashboard.render.com/blueprints"
    echo "3. Click 'New Blueprint Instance'"
    echo "4. Connect your GitHub repo"
    echo "5. Set DEEPSEEK_API_KEY in environment variables"
    echo ""
    echo -e "${YELLOW}Or use Render CLI (if installed):${NC}"
    
    if command -v render &> /dev/null; then
        echo "Creating service..."
        render blueprint apply
    else
        echo "Install Render CLI: https://render.com/docs/cli"
    fi
}

# Function to deploy to Fly.io
deploy_fly() {
    echo -e "\n${BLUE}🚀 Deploying to Fly.io...${NC}"
    
    if ! command -v flyctl &> /dev/null; then
        echo -e "${YELLOW}⚠️  Fly CLI not found. Installing...${NC}"
        curl -L https://fly.io/install.sh | sh
        export PATH="$HOME/.fly/bin:$PATH"
    fi
    
    echo "Creating volume for persistent storage..."
    fly volumes create workspace_data --region iad --size 1 -y || true
    
    echo "Setting secrets..."
    fly secrets set DEEPSEEK_API_KEY="$DEEPSEEK_API_KEY"
    fly secrets set WORKSPACE_PATH="/app/workspace"
    
    echo "Deploying..."
    fly deploy
    
    echo -e "${GREEN}✓ Deployment complete!${NC}"
    fly status
    fly open
}

# Function to deploy with Docker
deploy_docker() {
    echo -e "\n${BLUE}🐳 Building Docker image...${NC}"
    
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker not found. Please install Docker first.${NC}"
        exit 1
    fi
    
    echo "Building image..."
    docker build -t clawdbot-deepseek .
    
    echo "Running container..."
    docker run -d \
        --name clawdbot \
        -p 8080:8080 \
        -e DEEPSEEK_API_KEY="$DEEPSEEK_API_KEY" \
        -e PORT=8080 \
        -v "$(pwd)/workspace:/data/workspace" \
        --restart unless-stopped \
        clawdbot-deepseek
    
    echo -e "${GREEN}✓ Container running!${NC}"
    echo "Access at: http://localhost:8080"
    echo ""
    echo "View logs: docker logs -f clawdbot"
    echo "Stop: docker stop clawdbot"
    echo "Remove: docker rm clawdbot"
}

# Function to run locally
run_local() {
    echo -e "\n${BLUE}🏠 Running locally...${NC}"
    
    # Check dependencies
    if ! python -c "import flask" 2>/dev/null; then
        echo -e "${YELLOW}Installing dependencies...${NC}"
        pip install -r requirements-deploy.txt
    fi
    
    echo "Starting server on http://localhost:5000"
    python app.py
}

# Show menu
echo ""
echo "Choose deployment target:"
echo ""
echo -e "${BLUE}Cloud Platforms:${NC}"
echo "  1) Railway (easiest, $5/mo credit)"
echo "  2) Render (free tier available)"
echo "  3) Fly.io (performance, low cost)"
echo ""
echo -e "${BLUE}Self-Hosted:${NC}"
echo "  4) Docker (local or VPS)"
echo "  5) Run locally (development)"
echo ""
echo -e "${BLUE}Other:${NC}"
echo "  6) Show deployment guide"
echo "  q) Quit"
echo ""

read -p "Enter choice (1-6 or q): " choice

case $choice in
    1)
        deploy_railway
        ;;
    2)
        deploy_render
        ;;
    3)
        deploy_fly
        ;;
    4)
        deploy_docker
        ;;
    5)
        run_local
        ;;
    6)
        echo ""
        echo "╔════════════════════════════════════════════════════════════╗"
        echo "║                  Deployment Guide                          ║"
        echo "╚════════════════════════════════════════════════════════════╝"
        echo ""
        echo "Railway (Recommended for beginners):"
        echo "  - Easiest setup with GitHub integration"
        echo "  - $5/month free credit"
        echo "  - Automatic HTTPS"
        echo "  - Persistent volumes available"
        echo "  - URL: https://railway.app"
        echo ""
        echo "Render:"
        echo "  - Generous free tier"
        echo "  - Good for side projects"
        echo "  - Blueprint-based deployment"
        echo "  - URL: https://render.com"
        echo ""
        echo "Fly.io:"
        echo "  - Edge deployment (fast globally)"
        echo "  - Very low cost"
        echo "  - Docker-based"
        echo "  - URL: https://fly.io"
        echo ""
        echo "Docker:"
        echo "  - Full control"
        echo "  - Run anywhere (VPS, local, etc.)"
        echo "  - Requires Docker knowledge"
        echo ""
        echo "For all platforms, you need:"
        echo "  1. DEEPSEEK_API_KEY from https://platform.deepseek.com"
        echo "  2. Git repository pushed to GitHub"
        echo ""
        ;;
    q|Q)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac
