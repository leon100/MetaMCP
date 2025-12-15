#!/usr/bin/env python3
"""Check Facebook permissions and token info."""

import asyncio
import sys
from pathlib import Path

import httpx

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Settings


async def check_permissions():
    """Check what permissions the Facebook token has."""
    print("=" * 70)
    print("🔍 CHECKING FACEBOOK TOKEN PERMISSIONS")
    print("=" * 70)

    settings = Settings()

    if not settings.facebook_page_access_token:
        print("❌ No Facebook token configured!")
        return

    async with httpx.AsyncClient() as client:
        # Check token info
        print("\n[1] 🔑 Token Information")
        print("-" * 70)
        try:
            response = await client.get(
                f"https://graph.facebook.com/{settings.meta_api_version}/me",
                params={
                    "fields": "id,name,category",
                    "access_token": settings.facebook_page_access_token
                }
            )

            if response.status_code == 200:
                data = response.json()
                print("✅ Connected to:")
                print(f"   ID: {data.get('id')}")
                print(f"   Name: {data.get('name')}")
                print(f"   Category: {data.get('category', 'N/A')}")
            else:
                print(f"❌ Error: {response.text}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

        # Debug token to see permissions
        print("\n[2] 🔐 Token Permissions")
        print("-" * 70)
        try:
            response = await client.get(
                f"https://graph.facebook.com/{settings.meta_api_version}/debug_token",
                params={
                    "input_token": settings.facebook_page_access_token,
                    "access_token": settings.facebook_page_access_token
                }
            )

            if response.status_code == 200:
                data = response.json().get('data', {})
                print(f"✅ Token is valid: {data.get('is_valid')}")
                print(f"   App ID: {data.get('app_id')}")
                print(f"   Type: {data.get('type')}")
                print(f"   Expires: {data.get('expires_at', 'Never')}")

                scopes = data.get('scopes', [])
                if scopes:
                    print(f"\n   📋 Granted Permissions ({len(scopes)}):")
                    for scope in sorted(scopes):
                        print(f"      ✓ {scope}")
                else:
                    print("\n   ⚠️  No permissions found in token debug")
            else:
                print(f"❌ Error: {response.text}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

        # Test simple post
        print("\n[3] 📝 Test Simple Post")
        print("-" * 70)
        user_input = input("Post a test message? (yes/no): ")

        if user_input.lower() in ['yes', 'y']:
            try:
                response = await client.post(
                    f"https://graph.facebook.com/{settings.meta_api_version}/me/feed",
                    params={"access_token": settings.facebook_page_access_token},
                    json={"message": "🤖 Test from Meta MCP Server"}
                )

                if response.status_code == 200:
                    data = response.json()
                    print("✅ Posted successfully!")
                    print(f"   Post ID: {data.get('id')}")
                else:
                    print(f"❌ Error: {response.status_code}")
                    print(f"   {response.text}")
            except Exception as e:
                print(f"❌ Error: {str(e)}")

        print("\n" + "=" * 70)
        print("✨ Permission check complete!")
        print("=" * 70)


if __name__ == "__main__":
    asyncio.run(check_permissions())
