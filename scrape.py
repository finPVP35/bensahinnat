import json
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
        page.wait_for_selector("section.dash-summary-grid", timeout=15000)

        cards = page.query_selector_all("section.dash-summary-grid > *")
        for card in cards:
            text = card.inner_text()
            if "95 E10" in text:
                fuel = "95"
            elif "98 E5" in text:
                fuel = "98"
            elif "Diesel" in text:
                fuel = "diesel"
            else:
                continue

            lines = [l.strip() for l in text.splitlines() if l.strip()]
            for i, line in enumerate(lines):
                if "tänään" in line.lower():
                    for j in range(i, min(i+3, len(lines))):
                        val = parse_price(lines[j])
                        if val:
                            prices[fuel] = val
                            break
                    break

        browser.close()

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
