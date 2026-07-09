#!/usr/bin/env python3
"""
Test DeepSeek API connection and verify setup.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from deepseek_client import DeepSeekClient


def test_connection():
    """Test the DeepSeek API connection."""
    print("Testing DeepSeek API Connection...")
    print("-" * 40)

    try:
        client = DeepSeekClient()
        print(f"API Key: {'*' * 20}{client.api_key[-4:]}")
        print(f"Base URL: {client.base_url}")
        print(f"Default Model: {client.default_model}")
        print()

        # Test simple chat
        print("Sending test message...")
        response = client.simple_chat("Say 'Hello from DeepSeek!' in exactly those words.")
        print(f"Response: {response}")
        print()

        # Check for expected response
        if "hello" in response.lower() and "deepseek" in response.lower():
            print("Connection test PASSED!")
            return True
        else:
            print("Connection test PASSED (response received)")
            return True

    except Exception as e:
        print(f"Connection test FAILED: {e}")
        return False


def test_models():
    """Test available models."""
    print("\nTesting available models...")
    print("-" * 40)

    client = DeepSeekClient()

    models = [
        os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash"),
        os.getenv("DEEPSEEK_REASONING_MODEL", "deepseek-v4-pro"),
    ]

    for model in models:
        try:
            response = client.simple_chat("What is 2+2?", model=model, max_tokens=50)
            print(f"{model}: OK")
        except Exception as e:
            print(f"{model}: FAILED - {e}")


def test_streaming():
    """Test streaming responses."""
    print("\nTesting streaming...")
    print("-" * 40)

    try:
        client = DeepSeekClient()
        print("Response: ", end="")
        for chunk in client.chat(
            [{"role": "user", "content": "Count from 1 to 5."}],
            stream=True,
            max_tokens=50,
        ):
            print(chunk, end="", flush=True)
        print("\nStreaming test PASSED!")
    except Exception as e:
        print(f"\nStreaming test FAILED: {e}")


if __name__ == "__main__":
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(env_path)

    print("=" * 40)
    print("  DeepSeek Connection Test")
    print("=" * 40)
    print()

    if test_connection():
        test_models()
        test_streaming()

    print()
    print("=" * 40)
    print("  Test Complete")
    print("=" * 40)
