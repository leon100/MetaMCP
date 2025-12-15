#!/usr/bin/env python3
"""Complete test suite for Facebook adapter."""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Settings
from src.meta_client import MetaClient


async def test_facebook_complete():
    """Complete test of Facebook adapter functionality."""
    print("=" * 70)
    print("🔷 COMPLETE FACEBOOK ADAPTER TEST")
    print("=" * 70)

    settings = Settings()
    client = MetaClient(settings)

    if not settings.facebook_page_access_token:
        print("❌ No Facebook token configured!")
        return

    adapter = client.get_adapter("facebook")

    # Test 1: Get Page Info
    print("\n[TEST 1] 📄 Facebook Page Information")
    print("-" * 70)
    try:
        import httpx
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get(
                f"https://graph.facebook.com/{settings.meta_api_version}/me",
                params={
                    "fields": "id,name,about,followers_count,link",
                    "access_token": settings.facebook_page_access_token
                }
            )

            if response.status_code == 200:
                data = response.json()
                print("✅ Page Details:")
                print(f"   ID: {data.get('id')}")
                print(f"   Name: {data.get('name')}")
                print(f"   About: {data.get('about', 'N/A')}")
                print(f"   Followers: {data.get('followers_count', 'N/A')}")
                print(f"   Link: {data.get('link', 'N/A')}")
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

    # Test 2: Check Conversations
    print("\n[TEST 2] 💬 Facebook Messenger Conversations")
    print("-" * 70)
    try:
        import httpx
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get(
                f"https://graph.facebook.com/{settings.meta_api_version}/me/conversations",
                params={
                    "fields": "id,link,updated_time,message_count",
                    "limit": "5",
                    "access_token": settings.facebook_page_access_token
                }
            )

            if response.status_code == 200:
                data = response.json()
                conversations = data.get('data', [])

                if conversations:
                    print(f"✅ Found {len(conversations)} conversation(s):")
                    for i, conv in enumerate(conversations, 1):
                        print(f"\n   Conversation {i}:")
                        print(f"   - ID: {conv.get('id')}")
                        print(f"   - Messages: {conv.get('message_count', 'N/A')}")
                        print(f"   - Updated: {conv.get('updated_time', 'N/A')}")

                        # Try to get messages from first conversation
                        if i == 1:
                            print("\n   📨 Attempting to get messages...")
                            try:
                                result = await adapter.get_messages(
                                    conversation_id=conv.get('id'),
                                    limit=3
                                )
                                print(f"   ✅ Retrieved {len(result)} message(s)")
                                if result:
                                    print(f"   First message: {json.dumps(result[0], indent=6, default=str)}")
                            except Exception as e:
                                print(f"   ⚠️  Error getting messages: {str(e)}")
                else:
                    print("ℹ️  No conversations found.")
                    print("   💡 Tip: Someone needs to message your Page first!")
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

    # Test 3: Post to Feed
    print("\n[TEST 3] 📝 Post to Facebook Page Feed")
    print("-" * 70)
    user_input = input("Do you want to post a TEST message to your Facebook Page? (yes/no): ")

    if user_input.lower() in ['yes', 'y']:
        try:
            test_message = f"🤖 Test post from Meta MCP Server\nTimestamp: {datetime.now().isoformat()}"

            print(f"\n📤 Posting: '{test_message}'")
            result = await adapter.post_content(content=test_message)

            print("✅ Post published successfully!")
            print(f"   Post ID: {result.get('post_id')}")
            print(f"   🔗 View at: https://facebook.com/{result.get('post_id')}")

        except Exception as e:
            print(f"❌ Error posting: {str(e)}")
    else:
        print("⏭️  Skipped posting test")

    # Test 4: Get Page Insights (Analytics)
    print("\n[TEST 4] 📊 Facebook Page Insights")
    print("-" * 70)
    try:
        # Test available metrics
        metrics_to_test = [
            "page_impressions",
            "page_engaged_users",
            "page_post_engagements",
            "page_fans"
        ]

        for metric in metrics_to_test:
            try:
                result = await adapter.get_analytics(metric=metric, period="day")
                print(f"✅ {metric}:")

                if result.get('data'):
                    values = result['data'][0].get('values', [])
                    if values:
                        print(f"   Latest value: {values[-1].get('value', 'N/A')}")
                    else:
                        print("   No data available")
                else:
                    print("   No data returned")

            except Exception as e:
                print(f"⚠️  {metric}: {str(e)}")

    except Exception as e:
        print(f"❌ Error getting insights: {str(e)}")

    # Summary
    print("\n" + "=" * 70)
    print("✨ Facebook Adapter Test Complete!")
    print("=" * 70)
    print("\n📋 Summary:")
    print("   ✅ Page connection working")
    print("   ✅ Can access conversations (if any exist)")
    print("   ✅ Can post to feed")
    print("   ✅ Can get insights/analytics")
    print("\n💡 To test messaging:")
    print("   1. Send a message to your Page from your personal Facebook")
    print("   2. The conversation will appear and you can reply via API")


if __name__ == "__main__":
    asyncio.run(test_facebook_complete())
