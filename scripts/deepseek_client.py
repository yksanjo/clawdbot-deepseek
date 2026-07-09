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


@dataclass(frozen=True)
class ProviderConfig:
    name: str
    api_key_envs: tuple[str, ...]
    base_url_env: str
    model_env: str
    default_base_url: str
    default_model: str


PROVIDERS = {
    "deepseek": ProviderConfig(
        name="deepseek",
        api_key_envs=("DEEPSEEK_API_KEY",),
        base_url_env="DEEPSEEK_BASE_URL",
        model_env="DEEPSEEK_MODEL",
        default_base_url="https://api.deepseek.com/v1",
        default_model="deepseek-v4-flash",
    ),
    "kimi": ProviderConfig(
        name="kimi",
        api_key_envs=("KIMI_API_KEY", "MOONSHOT_API_KEY"),
        base_url_env="KIMI_BASE_URL",
        model_env="KIMI_MODEL",
        default_base_url="https://api.moonshot.ai/v1",
        default_model="kimi-k2.7-code",
    ),
}


def _first_env(keys: tuple[str, ...]) -> Optional[str]:
    for key in keys:
        value = os.getenv(key)
        if value:
            return value
    return None


class OpenAICompatibleClient:
    """Client for OpenAI-compatible chat completion APIs."""

    def __init__(
        self,
        provider: str = "deepseek",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ):
        if provider not in PROVIDERS:
            supported = ", ".join(sorted(PROVIDERS))
            raise ValueError(f"Unsupported provider '{provider}'. Supported: {supported}")

        self.provider = provider
        config = PROVIDERS[provider]
        self.api_key = api_key or _first_env(config.api_key_envs)
        if not self.api_key:
            env_names = " or ".join(config.api_key_envs)
            raise ValueError(
                f"{provider} API key required. Set {env_names} env var or pass api_key."
            )

        self.base_url = (
            base_url
            or os.getenv(config.base_url_env)
            or config.default_base_url
        ).rstrip("/")
        self.default_model = model or os.getenv(config.model_env) or config.default_model
        self.timeout = float(
            os.getenv("AI_REQUEST_TIMEOUT_SECONDS")
            or os.getenv("DEEPSEEK_TIMEOUT_SECONDS")
            or "45"
        )
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
        request_timeout = kwargs.pop("request_timeout", self.timeout)

        if self.provider == "kimi" and model.startswith("kimi-k2.7-code"):
            # Kimi K2.7 Code only accepts fixed sampling parameters.
            temperature = 1.0

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
            **kwargs,
        }

        if self.provider == "deepseek" and "thinking" not in payload:
            payload["thinking"] = {"type": "disabled"}

        response = self.session.post(
            f"{self.base_url}/chat/completions",
            json=payload,
            stream=stream,
            timeout=request_timeout,
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
        Use provider reasoning mode/model for complex reasoning tasks.

        Args:
            prompt: The problem or question requiring reasoning
            **kwargs: Additional parameters

        Returns:
            Reasoned response
        """
        if self.provider == "deepseek":
            kwargs.setdefault(
                "model",
                os.getenv("DEEPSEEK_REASONING_MODEL", "deepseek-v4-pro"),
            )
            kwargs.setdefault("thinking", {"type": "enabled"})
            kwargs.setdefault("reasoning_effort", "high")
        elif self.provider == "kimi":
            kwargs.setdefault("model", os.getenv("KIMI_REASONING_MODEL", self.default_model))

        return self.simple_chat(prompt, **kwargs)


class DeepSeekClient(OpenAICompatibleClient):
    """Client for DeepSeek API with OpenAI-compatible interface."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ):
        super().__init__(
            provider="deepseek",
            api_key=api_key,
            base_url=base_url,
            model=model,
        )


class KimiClient(OpenAICompatibleClient):
    """Client for Kimi/Moonshot API with OpenAI-compatible interface."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ):
        super().__init__(
            provider="kimi",
            api_key=api_key,
            base_url=base_url,
            model=model,
        )


class ClawdbotAgent:
    """
    Clawdbot agent wrapper around DeepSeek client.
    Handles workspace files, memory, and agent personality.
    """

    def __init__(
        self,
        workspace_path: str = "./workspace",
        api_key: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.workspace = Path(workspace_path)
        self.client = OpenAICompatibleClient(
            provider=provider or os.getenv("AI_PROVIDER", "deepseek"),
            api_key=api_key,
            model=model,
        )
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
        client = OpenAICompatibleClient(
            provider=os.getenv("AI_PROVIDER", "deepseek"),
            model=args.model,
        )
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
