#!/usr/bin/env python3
"""
Clawdbot DeepSeek - Web API Server
Deployable to Railway, Render, Fly.io, etc.

Provides:
- REST API for chat
- Web UI interface
- Health checks
- Memory persistence
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from functools import wraps

from flask import Flask, request, jsonify, render_template_string, Response
from scripts.deepseek_client import DeepSeekClient, ClawdbotAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configuration
WORKSPACE_PATH = os.getenv("WORKSPACE_PATH", "./workspace")
API_KEY = os.getenv("DEEPSEEK_API_KEY")
PORT = int(os.getenv("PORT", 5000))

# Initialize agent
agent = None


def get_agent():
    """Lazy initialization of agent."""
    global agent
    if agent is None:
        agent = ClawdbotAgent(workspace_path=WORKSPACE_PATH, api_key=API_KEY)
        logger.info(f"Agent initialized with workspace: {WORKSPACE_PATH}")
    return agent


# =============================================================================
# HTML TEMPLATES
# =============================================================================

INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Clawdbot DeepSeek</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
            padding: 20px;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
        }
        header {
            text-align: center;
            padding: 40px 0;
        }
        h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #00d4ff, #7b2cbf);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .subtitle {
            color: #888;
            font-size: 1.1em;
        }
        .chat-container {
            background: rgba(255,255,255,0.05);
            border-radius: 20px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }
        .messages {
            height: 400px;
            overflow-y: auto;
            padding: 10px;
            margin-bottom: 20px;
        }
        .message {
            margin-bottom: 15px;
            padding: 15px;
            border-radius: 12px;
            max-width: 80%;
            animation: fadeIn 0.3s ease;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .user {
            background: linear-gradient(135deg, #00d4ff, #0099cc);
            margin-left: auto;
            color: #fff;
        }
        .assistant {
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
        }
        .input-area {
            display: flex;
            gap: 10px;
        }
        input[type="text"] {
            flex: 1;
            padding: 15px 20px;
            border: none;
            border-radius: 12px;
            background: rgba(255,255,255,0.1);
            color: #fff;
            font-size: 1em;
            outline: none;
        }
        input[type="text"]::placeholder {
            color: #666;
        }
        button {
            padding: 15px 30px;
            border: none;
            border-radius: 12px;
            background: linear-gradient(135deg, #7b2cbf, #9d4edd);
            color: #fff;
            font-size: 1em;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(123,44,191,0.4);
        }
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        .loading {
            display: none;
            text-align: center;
            padding: 10px;
            color: #888;
        }
        .status {
            text-align: center;
            padding: 10px;
            margin-bottom: 20px;
            border-radius: 8px;
            font-size: 0.9em;
        }
        .status.connected {
            background: rgba(0,212,255,0.2);
            color: #00d4ff;
        }
        .status.error {
            background: rgba(255,71,87,0.2);
            color: #ff4757;
        }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 30px;
        }
        .info-card {
            background: rgba(255,255,255,0.05);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
        }
        .info-card h3 {
            color: #00d4ff;
            margin-bottom: 10px;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .info-card p {
            color: #888;
            font-size: 0.9em;
        }
        .api-section {
            margin-top: 30px;
            padding: 20px;
            background: rgba(0,0,0,0.3);
            border-radius: 12px;
        }
        .api-section h2 {
            color: #00d4ff;
            margin-bottom: 15px;
        }
        .api-section code {
            background: rgba(0,0,0,0.5);
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Monaco', monospace;
            font-size: 0.9em;
        }
        .api-section pre {
            background: rgba(0,0,0,0.5);
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 Clawdbot DeepSeek</h1>
            <p class="subtitle">Your AI assistant with persistent memory</p>
        </header>
        
        <div class="chat-container">
            <div id="status" class="status">Connecting...</div>
            <div id="messages" class="messages"></div>
            <div id="loading" class="loading">Thinking...</div>
            <div class="input-area">
                <input type="text" id="messageInput" placeholder="Type your message..." autofocus>
                <button id="sendBtn" onclick="sendMessage()">Send</button>
            </div>
        </div>
        
        <div class="info-grid">
            <div class="info-card">
                <h3>💾 Memory</h3>
                <p>Persistent across sessions</p>
            </div>
            <div class="info-card">
                <h3>⚡ Model</h3>
                <p>DeepSeek V3 / R1</p>
            </div>
            <div class="info-card">
                <h3>🔒 Privacy</h3>
                <p>Self-hosted</p>
            </div>
        </div>
        
        <div class="api-section">
            <h2>API Documentation</h2>
            <p>Send POST requests to <code>/api/chat</code>:</p>
            <pre>curl -X POST https://your-app.com/api/chat \\
  -H "Content-Type: application/json" \\
  -d '{"message": "Hello!"}'</pre>
        </div>
    </div>
    
    <script>
        const messagesDiv = document.getElementById('messages');
        const messageInput = document.getElementById('messageInput');
        const loading = document.getElementById('loading');
        const status = document.getElementById('status');
        const sendBtn = document.getElementById('sendBtn');
        
        // Check health on load
        fetch('/health')
            .then(r => r.json())
            .then(data => {
                status.className = 'status connected';
                status.textContent = '✓ Connected';
            })
            .catch(err => {
                status.className = 'status error';
                status.textContent = '✗ Connection failed';
            });
        
        function addMessage(text, sender) {
            const div = document.createElement('div');
            div.className = `message ${sender}`;
            div.textContent = text;
            messagesDiv.appendChild(div);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        async function sendMessage() {
            const text = messageInput.value.trim();
            if (!text) return;
            
            addMessage(text, 'user');
            messageInput.value = '';
            loading.style.display = 'block';
            sendBtn.disabled = true;
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });
                
                const data = await response.json();
                
                if (data.response) {
                    addMessage(data.response, 'assistant');
                } else if (data.error) {
                    addMessage('Error: ' + data.error, 'assistant');
                }
            } catch (err) {
                addMessage('Error: Failed to connect', 'assistant');
            } finally {
                loading.style.display = 'none';
                sendBtn.disabled = false;
            }
        }
        
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
    </script>
</body>
</html>
"""


# =============================================================================
# API ROUTES
# =============================================================================

@app.route("/")
def index():
    """Serve the web UI."""
    return render_template_string(INDEX_HTML)


@app.route("/health")
def health():
    """Health check endpoint."""
    try:
        agent = get_agent()
        return jsonify({
            "status": "healthy",
            "workspace": WORKSPACE_PATH,
            "agent_ready": True,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 503


@app.route("/api/chat", methods=["POST"])
def chat():
    """Chat endpoint."""
    try:
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"error": "Missing 'message' field"}), 400
        
        message = data["message"]
        stream = data.get("stream", False)
        model = data.get("model", "deepseek-chat")
        
        logger.info(f"Chat request: {message[:50]}...")
        
        agent = get_agent()
        
        if stream:
            def generate():
                # Note: Streaming implementation would go here
                # For now, return full response
                response = agent.chat(message, model=model)
                yield f"data: {json.dumps({'content': response})}\n\n"
            
            return Response(generate(), mimetype='text/event-stream')
        else:
            response = agent.chat(message, model=model)
            
            # Save to memory
            try:
                agent.save_memory(f"User: {message}\n\nAgent: {response}")
            except Exception as e:
                logger.warning(f"Failed to save memory: {e}")
            
            return jsonify({
                "response": response,
                "model": model,
                "timestamp": datetime.now().isoformat()
            })
    
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/reason", methods=["POST"])
def reason():
    """Reasoning endpoint using DeepSeek R1."""
    try:
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"error": "Missing 'message' field"}), 400
        
        message = data["message"]
        
        logger.info(f"Reason request: {message[:50]}...")
        
        agent = get_agent()
        response = agent.client.reason(message)
        
        return jsonify({
            "response": response,
            "model": "deepseek-reasoner",
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Reason error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/memory", methods=["GET"])
def get_memory():
    """Get memory files list."""
    try:
        memory_dir = Path(WORKSPACE_PATH) / "memory"
        if not memory_dir.exists():
            return jsonify({"files": []})
        
        files = sorted([f.name for f in memory_dir.glob("*.md")], reverse=True)
        return jsonify({
            "files": files,
            "workspace": WORKSPACE_PATH
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/memory/<filename>", methods=["GET"])
def get_memory_file(filename):
    """Get specific memory file content."""
    try:
        file_path = Path(WORKSPACE_PATH) / "memory" / filename
        
        # Security check - prevent directory traversal
        if not str(file_path.resolve()).startswith(str(Path(WORKSPACE_PATH).resolve())):
            return jsonify({"error": "Invalid filename"}), 400
        
        if not file_path.exists():
            return jsonify({"error": "File not found"}), 404
        
        content = file_path.read_text()
        return jsonify({
            "filename": filename,
            "content": content
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/personality", methods=["GET"])
def get_personality():
    """Get agent personality files."""
    try:
        workspace = Path(WORKSPACE_PATH)
        files = ["SOUL.md", "IDENTITY.md", "USER.md", "AGENTS.md"]
        
        personality = {}
        for filename in files:
            file_path = workspace / filename
            if file_path.exists():
                personality[filename] = file_path.read_text()
        
        return jsonify(personality)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    # Validate environment
    if not API_KEY:
        logger.error("DEEPSEEK_API_KEY not set!")
        print("❌ Error: DEEPSEEK_API_KEY environment variable is required")
        print("Set it with: export DEEPSEEK_API_KEY=your_key_here")
        exit(1)
    
    # Ensure workspace exists
    Path(WORKSPACE_PATH).mkdir(parents=True, exist_ok=True)
    (Path(WORKSPACE_PATH) / "memory").mkdir(exist_ok=True)
    
    logger.info(f"Starting Clawdbot server on port {PORT}")
    logger.info(f"Workspace: {WORKSPACE_PATH}")
    
    # Run server
    app.run(
        host="0.0.0.0",
        port=PORT,
        debug=False,
        threaded=True
    )
