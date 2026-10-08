"""Capture the two demo views from a running Streamlit server (dev tool)."""
import sys
import re
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
MODE = sys.argv[1] if len(sys.argv) > 1 else "fixture"

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 1000}, device_scale_factor=1)
    page.goto("http://127.0.0.1:8501", wait_until="domcontentloaded")
    page.get_by_role("button", name="Find my next skill").wait_for(timeout=30000)
    if MODE in {"phase3_noida", "batch_a_noida", "batch_b_noida", "batch_b_replay", "batch_c_noida", "batch_c_noida_plan", "batch_c_noida_distance", "batch_d_noida", "batch_d_noida_plan", "batch_e_noida", "batch_e_noida_plan", "batch_e_noida_distance", "batch_e_replay"}:
        page.get_by_role("combobox", name="Demo role").click()
        page.get_by_role("option", name="Data Analyst, Noida").click()
        page.get_by_role("button", name="Find my next skill").click()
        page.get_by_text("Skills that could open more jobs").wait_for(timeout=60000)
    elif MODE in {"phase3_frontend", "batch_a_frontend", "batch_b_frontend", "batch_c_frontend", "batch_c_frontend_plan", "batch_c_frontend_distance", "batch_d_frontend", "batch_d_frontend_plan", "batch_e_frontend", "batch_e_frontend_plan", "batch_e_frontend_distance"}:
        page.get_by_role("button", name="Find my next skill").click()
        page.get_by_text("Skills that could open more jobs").wait_for(timeout=60000)
    elif MODE in {"fixture", "phase2_noida"}:
        page.get_by_text("Within reach threshold").wait_for()
        slider = page.get_by_role("slider", name="Within reach threshold")
        slider.focus()
        slider.press("Home")
        slider.press("ArrowRight")
        slider.press("ArrowRight")  # 0.4
        page.get_by_role("button", name="Find my next skill").click()
        page.get_by_text("Skills that could open more jobs").wait_for(timeout=30000)
    elif MODE == "phase2_frontend":
        page.get_by_role("textbox", name="Role").fill("Frontend Developer")
        page.get_by_role("textbox", name="City").fill("Bengaluru")
        page.get_by_role("textbox", name="Paste resume text").fill("HTML, CSS, JavaScript")
        page.get_by_text("Replay saved validation data", exact=True).click()
        page.get_by_role("button", name="Find my next skill").click()
        page.get_by_text("Skills that could open more jobs").wait_for(timeout=30000)
    elif MODE == "live":
        page.get_by_role("textbox", name="Role").fill("Business Analyst")
        page.get_by_role("textbox", name="City").fill("Hyderabad")
        page.get_by_role("textbox", name="Paste resume text").fill("Excel, SQL, Power BI")
        page.get_by_text("Replay saved validation data", exact=True).click()
        page.get_by_role("combobox", name="Job pages").click()
        page.get_by_role("option", name="1").click()
        slider = page.get_by_role("slider", name="Within reach threshold")
        slider.focus()
        slider.press("Home")
        slider.press("ArrowRight")
        slider.press("ArrowRight")
        page.get_by_role("button", name="Find my next skill").click()
        page.get_by_text("Skills that could open more jobs").wait_for(timeout=30000)
    else:
        raise ValueError("unknown screenshot mode")
    if MODE.startswith("batch_e_"):
        city = "Bengaluru" if "frontend" in MODE else "Noida"
        page.get_by_text(re.compile(r"Your profile matches .* saved listings in " + city)).wait_for(timeout=90000)
    page.get_by_text("Search replay", exact=True).wait_for(timeout=90000)
    if MODE.startswith(("batch_c_", "batch_d_", "batch_e_")):
        page.get_by_text("Opportunity curve", exact=True).wait_for(timeout=30000)
        page.get_by_text("Skill distance", exact=True).wait_for(timeout=30000)
        if MODE.endswith("_plan"):
            page.get_by_text("Opportunity curve", exact=True).evaluate("node => node.scrollIntoView({block: 'start'})")
            page.wait_for_timeout(500)
        elif MODE.endswith("_distance"):
            page.get_by_text("Skill distance", exact=True).evaluate("node => node.scrollIntoView({block: 'start'})")
            page.wait_for_timeout(500)
    page.wait_for_timeout(500)
    if MODE in {"batch_b_replay", "batch_e_replay"}:
        page.get_by_text("Search replay", exact=True).click()
        page.get_by_text("Listing origins", exact=True).wait_for(timeout=30000)
    if page.locator('[data-testid="stException"]').count():
        raise RuntimeError("Streamlit rendered an exception instead of the demo")
    page.screenshot(path=str(ROOT / "screenshots" / f"{MODE}.png"), full_page=True)
    print(f"screenshot={ROOT / 'screenshots' / f'{MODE}.png'}")
    browser.close()
