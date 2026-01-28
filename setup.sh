#!/bin/bash

# Clawdbot DeepSeek Setup Script

set -e

echo "======================================"
echo "  Clawdbot DeepSeek Setup"
echo "======================================"
echo ""

# Check for .env file
if [ ! -f ".env" ]; then
    echo "Creating .env from template..."
    cp .env.example .env
    echo ""
    echo "Please edit .env and add your DeepSeek API key:"
    echo "  DEEPSEEK_API_KEY=your_api_key_here"
    echo ""
    echo "Get your API key at: https://platform.deepseek.com"
    echo ""
    read -p "Press Enter after you've added your API key..."
fi

# Load environment
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Verify API key
if [ -z "$DEEPSEEK_API_KEY" ] || [ "$DEEPSEEK_API_KEY" = "your_deepseek_api_key_here" ]; then
    echo "Error: Please set your DEEPSEEK_API_KEY in .env"
    exit 1
fi

# Create memory directory
mkdir -p workspace/memory

echo ""
echo "Testing DeepSeek API connection..."
echo ""

# Test API connection
response=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"model": "deepseek-chat", "messages": [{"role": "user", "content": "Hello"}], "max_tokens": 5}' \
    https://api.deepseek.com/v1/chat/completions)

if [ "$response" = "200" ]; then
    echo "DeepSeek API connection successful!"
else
    echo "Warning: API test returned status $response"
    echo "Please verify your API key is correct."
fi

echo ""
echo "======================================"
echo "  Setup Complete!"
echo "======================================"
echo ""
echo "Your agent is ready. To get started:"
echo ""
echo "1. Review workspace/SOUL.md to understand your agent's personality"
echo "2. Edit workspace/USER.md with your info"
echo "3. Run your agent with your preferred interface"
echo ""
echo "For the full experience, install the Clawdbot runtime."
echo "See README.md for more details."
echo ""
