"""Capture a screenshot of every site page from a running Streamlit server (dev tool).

Usage: python -m scripts.capture_site [port] [prefix] [width]"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PORT = sys.argv[1] if len(sys.argv) > 1 else "8501"
PREFIX = sys.argv[2] if len(sys.argv) > 2 else "site"
WIDTH = int(sys.argv[3]) if len(sys.argv) > 3 else 1280
PAGES = {"home": "", "find": "find", "prep": "prep", "compare": "compare", "live": "live",
         "methods": "methods", "about": "about"}
READY = {"home": "Try it with Priya's profile", "find": "Skills we read from your text", "prep": "Readiness for this job",
         "compare": "Share matched", "live": "Live search", "methods": "What the numbers mean", "about": "What happens to your resume"}

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": WIDTH, "height": 900})
    for name, path in PAGES.items():
        page.goto(f"http://127.0.0.1:{PORT}/{path}", wait_until="domcontentloaded")
        try:
            page.get_by_text(READY[name]).first.wait_for(timeout=60000)
        except Exception:
            if name == "live":
                print("skipped live (no key on this server)")
                continue
            raise
        page.wait_for_timeout(1500)
        height = page.evaluate("document.querySelector('[data-testid=\"stMain\"]').scrollHeight")
        page.set_viewport_size({"width": WIDTH, "height": min(int(height) + 80, 12000)})
        page.wait_for_timeout(800)
        if page.locator('[data-testid="stException"]').count():
            raise RuntimeError(f"{name} rendered an exception")
        overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
        out = ROOT / "screenshots" / f"{PREFIX}_{name}.png"
        page.screenshot(path=str(out), full_page=True)
        print(name, "horizontal overflow px:", overflow, out.name)
    browser.close()
