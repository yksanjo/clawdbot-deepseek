#!/usr/bin/env python3
"""
DeepSeek API Client for Clawdbot

A simple, standalone client for interacting with DeepSeek's API.
Compatible with the OpenAI SDK pattern.
"""

import os
import json
import requests
from typing import Optional, List, Dict, Generator
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Message:
    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class ChatResponse:
    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: str


class DeepSeekClient:
    """Client for DeepSeek API with OpenAI-compatible interface."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.deepseek.com/v1",
        model: str = "deepseek-chat",
    ):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError(
                "DeepSeek API key required. Set DEEPSEEK_API_KEY env var or pass api_key."
            )
        self.base_url = base_url.rstrip("/")
        self.default_model = model
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        )

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        stream: bool = False,
        **kwargs,
    ) -> ChatResponse | Generator[str, None, None]:
        """
        Send a chat completion request to DeepSeek.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use (default: deepseek-chat)
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
            stream: Whether to stream the response
            **kwargs: Additional parameters to pass to the API

        Returns:
            ChatResponse object or generator if streaming
        """
        model = model or self.default_model

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
            **kwargs,
        }

        response = self.session.post(
            f"{self.base_url}/chat/completions",
            json=payload,
            stream=stream,
        )
        response.raise_for_status()

        if stream:
            return self._stream_response(response)

        data = response.json()
        choice = data["choices"][0]

        return ChatResponse(
            content=choice["message"]["content"],
            model=data["model"],
            usage=data.get("usage", {}),
            finish_reason=choice.get("finish_reason", ""),
        )

    def _stream_response(self, response) -> Generator[str, None, None]:
        """Stream response chunks from the API."""
        for line in response.iter_lines():
            if line:
                line = line.decode("utf-8")
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        delta = chunk["choices"][0].get("delta", {})
                        if "content" in delta:
                            yield delta["content"]
                    except json.JSONDecodeError:
                        continue

    def simple_chat(self, prompt: str, system: Optional[str] = None, **kwargs) -> str:
        """
        Simple single-turn chat.

        Args:
            prompt: User message
            system: Optional system prompt
            **kwargs: Additional parameters for chat()

        Returns:
            Assistant's response as a string
        """
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = self.chat(messages, **kwargs)
        return response.content

    def reason(self, prompt: str, **kwargs) -> str:
        """
        Use DeepSeek Reasoner (R1) for complex reasoning tasks.

        Args:
            prompt: The problem or question requiring reasoning
            **kwargs: Additional parameters

        Returns:
            Reasoned response
        """
        return self.simple_chat(prompt, model="deepseek-reasoner", **kwargs)


class ClawdbotAgent:
    """
    Clawdbot agent wrapper around DeepSeek client.
    Handles workspace files, memory, and agent personality.
    """

    def __init__(
        self,
        workspace_path: str = "./workspace",
        api_key: Optional[str] = None,
    ):
        self.workspace = Path(workspace_path)
        self.client = DeepSeekClient(api_key=api_key)
        self.memory_dir = self.workspace / "memory"
        self.memory_dir.mkdir(exist_ok=True)

    def _load_file(self, filename: str) -> Optional[str]:
        """Load a workspace file."""
        path = self.workspace / filename
        if path.exists():
            return path.read_text()
        return None

    def _get_system_prompt(self) -> str:
        """Build system prompt from workspace files."""
        parts = []

        soul = self._load_file("SOUL.md")
        if soul:
            parts.append(f"# Your Soul\n{soul}")

        identity = self._load_file("IDENTITY.md")
        if identity:
            parts.append(f"# Your Identity\n{identity}")

        user = self._load_file("USER.md")
        if user:
            parts.append(f"# About Your Human\n{user}")

        agents = self._load_file("AGENTS.md")
        if agents:
            parts.append(f"# Operating Instructions\n{agents}")

        return "\n\n---\n\n".join(parts)

    def chat(self, message: str, **kwargs) -> str:
        """
        Chat with the agent.

        Args:
            message: User message
            **kwargs: Additional parameters

        Returns:
            Agent's response
        """
        system = self._get_system_prompt()
        return self.client.simple_chat(message, system=system, **kwargs)

    def save_memory(self, content: str, filename: Optional[str] = None):
        """
        Save content to memory.

        Args:
            content: Content to save
            filename: Optional filename (default: today's date)
        """
        from datetime import date

        filename = filename or f"{date.today().isoformat()}.md"
        path = self.memory_dir / filename

        # Append to existing file or create new
        mode = "a" if path.exists() else "w"
        with open(path, mode) as f:
            f.write(f"\n---\n{content}\n")


def main():
    """Example usage of the DeepSeek client."""
    import argparse

    parser = argparse.ArgumentParser(description="Chat with DeepSeek")
    parser.add_argument("message", nargs="?", help="Message to send")
    parser.add_argument("--model", default="deepseek-chat", help="Model to use")
    parser.add_argument("--stream", action="store_true", help="Stream response")
    parser.add_argument("--agent", action="store_true", help="Use Clawdbot agent mode")
    args = parser.parse_args()

    if args.agent:
        agent = ClawdbotAgent()
        if args.message:
            print(agent.chat(args.message))
        else:
            # Interactive mode
            print("Clawdbot DeepSeek Agent (type 'quit' to exit)")
            print("-" * 40)
            while True:
                try:
                    user_input = input("You: ").strip()
                    if user_input.lower() in ("quit", "exit", "q"):
                        break
                    if not user_input:
                        continue
                    response = agent.chat(user_input)
                    print(f"Agent: {response}\n")
                except KeyboardInterrupt:
                    break
    else:
        client = DeepSeekClient(model=args.model)
        if args.message:
            if args.stream:
                for chunk in client.chat(
                    [{"role": "user", "content": args.message}], stream=True
                ):
                    print(chunk, end="", flush=True)
                print()
            else:
                print(client.simple_chat(args.message))
        else:
            # Interactive mode
            print(f"DeepSeek Chat ({args.model}) - type 'quit' to exit")
            print("-" * 40)
            while True:
                try:
                    user_input = input("You: ").strip()
                    if user_input.lower() in ("quit", "exit", "q"):
                        break
                    if not user_input:
                        continue
                    response = client.simple_chat(user_input)
                    print(f"DeepSeek: {response}\n")
                except KeyboardInterrupt:
                    break


if __name__ == "__main__":
    main()
