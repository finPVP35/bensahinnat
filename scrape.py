import json
import re
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright

URL = "https://www.hintatutka.net/?lang=fi"

def parse_price(text):
    text = text.replace(",", ".").replace("€/l", "").strip()
    try:
        val = float(text)
        if 0.5 < val < 5.0:
            return val
    except ValueError:
        pass
    return None

def scrape_prices():
    prices = {"95": None, "98": None, "diesel": None}

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(URL, wait_until="networkidle", timeout=30000)

        # Etsi "Keskiarvo tänään" tekstit ja niihin liittyvät hinnat
        content = page.content()
        browser.close()

    # Hae hinnat regex:llä renderöidystä HTML:stä
    # 95 E10
    m = re.search(r'95 E10.*?Keskiarvo tänään.*?([\d,]+)\s*€/l', content, re.DOTALL)
    if m:
        prices["95"] = parse_price(m.group(1))

    # 98 E5
    m = re.search(r'98 E5.*?Keskiarvo tänään.*?([\d,]+)\s*€/l', content, re.DOTALL)
    if m:
        prices["98"] = parse_price(m.group(1))

    # Diesel
    m = re.search(r'Diesel.*?Keskiarvo tänään.*?([\d,]+)\s*€/l', content, re.DOTALL)
    if m:
        prices["diesel"] = parse_price(m.group(1))

    if any(v is None for v in prices.values()):
        raise ValueError(f"Kaikkia hintoja ei löydy: {prices}")

    result = {
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": URL,
        "location": "Suomi (koko maa)",
        "prices": prices
    }

    return result

if __name__ == "__main__":
    data = scrape_prices()
    print(json.dumps(data, indent=2, ensure_ascii=False))

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("✅ data.json päivitetty!")
