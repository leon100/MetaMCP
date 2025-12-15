#!/usr/bin/env python3
"""Test script for Meta MCP Server with real credentials."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Settings
from src.errors import AuthenticationError, MetaMCPError
from src.meta_client import MetaClient


async def test_real_facebook():
    """Test Facebook with real credentials."""
    print("🧪 Testing Meta MCP Server with REAL credentials\n")
    print("=" * 60)

    # Load real settings from .env
    settings = Settings()

    print("📋 Configuration loaded:")
    print(f"   - Demo Mode: {settings.demo_mode}")
    print(f"   - API Version: {settings.meta_api_version}")
    print(f"   - Facebook Token: {'✅ Configured' if settings.facebook_page_access_token else '❌ Missing'}")
    print(f"   - Instagram Token: {'✅ Configured' if settings.instagram_access_token else '❌ Missing'}")
    print(f"   - WhatsApp Token: {'✅ Configured' if settings.whatsapp_access_token else '❌ Missing'}")
    print()

    if settings.demo_mode:
        print("⚠️  WARNING: DEMO_MODE is still enabled!")
        print("   Set DEMO_MODE=false or remove it from .env\n")
        return

    client = MetaClient(settings)

    # Test Facebook
    if settings.facebook_page_access_token:
        print("=" * 60)
        print("1️⃣  Testing Facebook Page Access")
        print("=" * 60)

        try:
            _ = client.get_adapter("facebook")
            print("✅ Facebook adapter created successfully")

            # Test: Get Page info (simple GET request)
            print("\n📊 Testing Facebook Graph API connectivity...")
            import httpx
            async with httpx.AsyncClient() as http_client:
                response = await http_client.get(
                    f"https://graph.facebook.com/{settings.meta_api_version}/me",
                    params={"access_token": settings.facebook_page_access_token}
                )

                if response.status_code == 200:
                    data = response.json()
                    print("✅ Connected to Facebook Page:")
                    print(f"   - Page ID: {data.get('id')}")
                    print(f"   - Page Name: {data.get('name', 'N/A')}")
                else:
                    print(f"❌ Error: {response.status_code}")
                    print(f"   {response.text}")

        except AuthenticationError as e:
            print(f"❌ Authentication Error: {e.message}")
        except MetaMCPError as e:
            print(f"❌ MCP Error: {e.message}")
        except Exception as e:
            print(f"❌ Unexpected Error: {str(e)}")
    else:
        print("⏭️  Skipping Facebook - no token configured\n")

    # Test Instagram
    if settings.instagram_access_token:
        print("\n" + "=" * 60)
        print("2️⃣  Testing Instagram Account Access")
        print("=" * 60)

        try:
            _ = client.get_adapter("instagram")
            print("✅ Instagram adapter created successfully")

            # Test: Get Instagram account info
            print("\n📊 Testing Instagram Graph API connectivity...")
            import httpx
            async with httpx.AsyncClient() as http_client:
                response = await http_client.get(
                    f"https://graph.facebook.com/{settings.meta_api_version}/me",
                    params={
                        "fields": "id,username,account_type",
                        "access_token": settings.instagram_access_token
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    print("✅ Connected to Instagram:")
                    print(f"   - Account ID: {data.get('id')}")
                    print(f"   - Username: {data.get('username', 'N/A')}")
                    print(f"   - Type: {data.get('account_type', 'N/A')}")
                else:
                    print(f"❌ Error: {response.status_code}")
                    print(f"   {response.text}")

        except AuthenticationError as e:
            print(f"❌ Authentication Error: {e.message}")
        except MetaMCPError as e:
            print(f"❌ MCP Error: {e.message}")
        except Exception as e:
            print(f"❌ Unexpected Error: {str(e)}")
    else:
        print("⏭️  Skipping Instagram - no token configured\n")

    # Test WhatsApp
    if settings.whatsapp_access_token and settings.whatsapp_phone_number_id:
        print("\n" + "=" * 60)
        print("3️⃣  Testing WhatsApp Business Access")
        print("=" * 60)

        try:
            _ = client.get_adapter("whatsapp")
            print("✅ WhatsApp adapter created successfully")
            print(f"   - Phone Number ID: {settings.whatsapp_phone_number_id}")

        except AuthenticationError as e:
            print(f"❌ Authentication Error: {e.message}")
        except MetaMCPError as e:
            print(f"❌ MCP Error: {e.message}")
        except Exception as e:
            print(f"❌ Unexpected Error: {str(e)}")
    else:
        print("⏭️  Skipping WhatsApp - no token/phone configured\n")

    print("\n" + "=" * 60)
    print("✨ Connection tests completed!")
    print("=" * 60)
    print("\n💡 Next steps:")
    print("   - If all connections succeeded, your credentials are valid!")
    print("   - You can now use the MCP server with real Meta APIs")
    print("   - To send a test message, you need a valid recipient ID")
    print("   - Use './venv/bin/python scripts/test_demo.py' for mock testing")


if __name__ == "__main__":
    asyncio.run(test_real_facebook())
