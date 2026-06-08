"""Standalone Playwright fetcher — runs as a subprocess to avoid event loop issues."""
import json
import sys

from playwright.sync_api import sync_playwright

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)


def fetch(url: str) -> dict:
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"],
        )
        ctx = browser.new_context(
            user_agent=USER_AGENT,
            viewport={"width": 1920, "height": 1080},
        )
        page = ctx.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_selector("dt", timeout=20000)
        html = page.content()
        browser.close()
        return {"html": html}


if __name__ == "__main__":
    url = sys.argv[1]
    try:
        result = fetch(url)
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
