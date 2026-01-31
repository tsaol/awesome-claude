#!/usr/bin/env python3
"""
AWS AgentCore Browser Test Script
Usage: python browser_test.py <url> [--screenshot <path>] [--check-api] [--json]
"""

import argparse
import asyncio
import sys
import json

# Auto-install dependencies if missing
def ensure_dependencies():
    required = ["bedrock_agentcore", "playwright", "nest_asyncio", "boto3"]
    missing = []
    for pkg in required:
        try:
            __import__(pkg.replace("-", "_"))
        except ImportError:
            missing.append(pkg.replace("_", "-"))

    if missing:
        print(f"Installing missing dependencies: {', '.join(missing)}")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing + ["-q"])

ensure_dependencies()

from bedrock_agentcore.tools.browser_client import browser_session
from playwright.sync_api import sync_playwright
import nest_asyncio

nest_asyncio.apply()


def test_url(
    url: str,
    screenshot_path: str = None,
    check_api: bool = False,
    region: str = "us-west-2"
) -> dict:
    """
    Test a URL using AWS AgentCore Browser.

    Args:
        url: The URL to test
        screenshot_path: Optional path to save screenshot
        check_api: Whether to check /api/health endpoint
        region: AWS region for AgentCore Browser

    Returns:
        Dictionary with test results
    """
    results = {
        "url": url,
        "status": "unknown",
        "title": None,
        "errors": [],
        "api_check": None,
        "screenshot": None
    }

    print(f"🚀 Starting browser session in {region}...")

    try:
        with browser_session(region) as client:
            print(f"✅ Browser session started")

            # Get WebSocket URL and headers
            ws_url, headers = client.generate_ws_headers()

            # Connect with Playwright
            with sync_playwright() as p:
                print("🔗 Connecting to remote browser...")
                browser = p.chromium.connect_over_cdp(ws_url, headers=headers)

                context = browser.contexts[0]
                page = context.pages[0] if context.pages else context.new_page()

                # Capture console errors
                console_errors = []
                page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

                # Navigate to URL
                print(f"🌐 Navigating to {url}...")
                response = page.goto(url, wait_until="networkidle", timeout=60000)

                results["status"] = response.status if response else "no_response"
                results["title"] = page.title()

                print(f"📄 Page title: {results['title']}")
                print(f"📊 HTTP status: {results['status']}")

                # Wait for any async errors
                page.wait_for_timeout(2000)

                # Check for console errors
                if console_errors:
                    results["errors"] = console_errors[:10]
                    print(f"⚠️  Console errors found: {len(console_errors)}")
                    for err in console_errors[:5]:
                        print(f"   - {err[:100]}...")

                # Check API if requested
                if check_api:
                    api_url = url.rstrip("/") + "/api/health"
                    print(f"🔍 Checking API: {api_url}")
                    try:
                        api_response = page.goto(api_url, timeout=10000)
                        api_text = page.content()
                        results["api_check"] = {
                            "url": api_url,
                            "status": api_response.status if api_response else "no_response",
                            "body": api_text[:500] if api_text else None
                        }
                        print(f"   API status: {results['api_check']['status']}")
                    except Exception as e:
                        results["api_check"] = {"url": api_url, "error": str(e)}
                        print(f"   API error: {e}")

                # Take screenshot if requested
                if screenshot_path:
                    # Navigate back to main page for screenshot
                    page.goto(url, wait_until="networkidle", timeout=60000)
                    page.screenshot(path=screenshot_path, full_page=True)
                    results["screenshot"] = screenshot_path
                    print(f"📸 Screenshot saved: {screenshot_path}")

                browser.close()

            print("🧹 Session cleaned up")

    except Exception as e:
        results["errors"].append(str(e))
        print(f"❌ Error: {e}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Test a URL using AWS AgentCore Browser",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python browser_test.py https://example.com
  python browser_test.py https://example.com --screenshot shot.png
  python browser_test.py https://example.com --check-api --json
        """
    )
    parser.add_argument("url", help="URL to test")
    parser.add_argument("--screenshot", "-s", metavar="PATH", help="Path to save screenshot")
    parser.add_argument("--check-api", "-a", action="store_true", help="Check /api/health endpoint")
    parser.add_argument("--region", "-r", default="us-west-2", help="AWS region (default: us-west-2)")
    parser.add_argument("--json", "-j", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    # Run the test
    results = test_url(
        url=args.url,
        screenshot_path=args.screenshot,
        check_api=args.check_api,
        region=args.region
    )

    # Output results
    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print("\n" + "=" * 50)
        print("📋 Test Results")
        print("=" * 50)
        print(f"URL: {results['url']}")
        print(f"Status: {results['status']}")
        print(f"Title: {results['title']}")
        if results["errors"]:
            print(f"Errors: {len(results['errors'])}")
        if results["api_check"]:
            print(f"API: {results['api_check']}")
        if results["screenshot"]:
            print(f"Screenshot: {results['screenshot']}")

        # Summary
        if results["status"] == 200 and not results["errors"]:
            print("\n✅ All checks passed!")
            sys.exit(0)
        else:
            print("\n⚠️  Issues detected")
            sys.exit(1)


if __name__ == "__main__":
    main()
