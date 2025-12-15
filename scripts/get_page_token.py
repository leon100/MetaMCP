#!/usr/bin/env python3
"""Get Page Access Token from User Access Token."""

import asyncio
import sys
from pathlib import Path

import httpx

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Settings


async def get_page_token():
    """Exchange user token for page token."""
    print("=" * 70)
    print("🔄 CONVERTING USER TOKEN TO PAGE TOKEN")
    print("=" * 70)

    settings = Settings()
    user_token = settings.facebook_page_access_token

    async with httpx.AsyncClient() as client:
        # Get list of pages
        print("\n[1] 📄 Getting your Facebook Pages...")
        print("-" * 70)

        try:
            response = await client.get(
                f"https://graph.facebook.com/{settings.meta_api_version}/me/accounts",
                params={"access_token": user_token}
            )

            if response.status_code == 200:
                data = response.json()
                pages = data.get('data', [])

                if not pages:
                    print("❌ No pages found! You need to:")
                    print("   1. Create a Facebook Page")
                    print("   2. Make sure you're an admin of the page")
                    return

                print(f"✅ Found {len(pages)} page(s):\n")

                for i, page in enumerate(pages, 1):
                    print(f"{i}. {page['name']}")
                    print(f"   ID: {page['id']}")
                    print(f"   Category: {page.get('category', 'N/A')}")
                    print(f"   Access Token: {page['access_token'][:20]}...")
                    print()

                # Show how to use page token
                print("=" * 70)
                print("📝 UPDATE YOUR .env FILE")
                print("=" * 70)
                print("\nReplace FACEBOOK_PAGE_ACCESS_TOKEN with one of these:\n")

                for i, page in enumerate(pages, 1):
                    print(f"# For page: {page['name']}")
                    print(f"FACEBOOK_PAGE_ACCESS_TOKEN={page['access_token']}")
                    print()

                # Test first page token
                if pages:
                    print("=" * 70)
                    print("🧪 TESTING FIRST PAGE TOKEN")
                    print("=" * 70)

                    page = pages[0]
                    page_token = page['access_token']

                    # Test token
                    response = await client.get(
                        f"https://graph.facebook.com/{settings.meta_api_version}/me",
                        params={
                            "fields": "id,name,access_token,tasks",
                            "access_token": page_token
                        }
                    )

                    if response.status_code == 200:
                        page_data = response.json()
                        print("\n✅ Page token verified!")
                        print(f"   Page: {page_data.get('name')}")
                        print(f"   ID: {page_data.get('id')}")
                        print(f"   Tasks: {page_data.get('tasks', [])}")

                        # Check permissions
                        response = await client.get(
                            f"https://graph.facebook.com/{settings.meta_api_version}/debug_token",
                            params={
                                "input_token": page_token,
                                "access_token": user_token
                            }
                        )

                        if response.status_code == 200:
                            token_data = response.json().get('data', {})
                            print(f"\n   Token Type: {token_data.get('type')}")
                            print(f"   Valid: {token_data.get('is_valid')}")

                            scopes = token_data.get('scopes', [])
                            if scopes:
                                print("\n   Permissions on this token:")
                                for scope in sorted(scopes):
                                    print(f"      ✓ {scope}")
                    else:
                        print(f"   ❌ Error testing token: {response.text}")

            else:
                print(f"❌ Error: {response.text}")

        except Exception as e:
            print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(get_page_token())
