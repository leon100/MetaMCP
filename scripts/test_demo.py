#!/usr/bin/env python3
"""Simple test client for Meta MCP Server in demo mode."""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Settings
from src.meta_client import MetaClient


async def test_demo_mode():
    """Test MCP server in demo mode."""
    print("🧪 Testing Meta MCP Server in DEMO mode\n")

    # Initialize settings in demo mode
    settings = Settings(demo_mode=True)
    client = MetaClient(settings)

    # Test 1: Send message
    print("1️⃣  Testing meta_send_message (Facebook)...")
    try:
        adapter = client.get_adapter("facebook")
        result = await adapter.send_message(
            recipient_id="user_123",
            content="Hello from demo!"
        )
        print(f"   ✅ Result: {json.dumps(result, indent=2)}\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")

    # Test 2: Get messages
    print("2️⃣  Testing meta_get_messages (Instagram)...")
    try:
        adapter = client.get_adapter("instagram")
        messages = await adapter.get_messages(
            conversation_id="conv_456",
            limit=3
        )
        print(f"   ✅ Retrieved {len(messages)} messages")
        print(f"   First message: {json.dumps(messages[0], indent=2)}\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")

    # Test 3: Post content
    print("3️⃣  Testing meta_post_content (Facebook)...")
    try:
        adapter = client.get_adapter("facebook")
        result = await adapter.post_content(
            content="Demo post!",
            media_urls=["https://example.com/image.jpg"]
        )
        print(f"   ✅ Result: {json.dumps(result, indent=2)}\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")

    # Test 4: Get analytics
    print("4️⃣  Testing meta_get_analytics (Instagram)...")
    try:
        adapter = client.get_adapter("instagram")
        result = await adapter.get_analytics(
            metric="reach",
            period="week"
        )
        print(f"   ✅ Result: {json.dumps(result, indent=2, default=str)}\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")

    print("✨ All tests completed!")


if __name__ == "__main__":
    asyncio.run(test_demo_mode())
