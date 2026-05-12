import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timezone

URL = "https://polttoaine.net/espoo"

FUEL_NAMES = {
    "95": ["95", "95E10"],
    "98": ["98", "98E5"],
    "D":  ["Diesel", "D"],
}

def scrape_prices():
    headers = {"User-Agent": "Mozilla/5.0 (compatible; bensahinnat-bot/1.0)"}
    resp = requests.get(URL, headers=headers, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    prices = {"95": [], "98": [], "D": []}

    # polttoaine.net käyttää taulukkoa hintojen näyttämiseen
    rows = soup.select("table tr")
    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 3:
            continue

        fuel_cell = cells[1].get_text(strip=True) if len(cells) > 1 else ""
        price_cell = cells[2].get_text(strip=True) if len(cells) > 2 else ""

        # Kokeile myös eri sarakerakennetta
        for fuel_key, aliases in FUEL_NAMES.items():
            for alias in aliases:
                if alias.lower() in fuel_cell.lower():
                    try:
                        price_str = price_cell.replace(",", ".").replace("€", "").strip()
                        price = float(price_str)
                        if 0.5 < price < 5.0:  # järkevä hintaväli
                            prices[fuel_key].append(price)
                    except ValueError:
                        pass

    # Laske keskiarvot
    averages = {}
    for fuel_key, price_list in prices.items():
        if price_list:
            averages[fuel_key] = round(sum(price_list) / len(price_list), 3)
        else:
            averages[fuel_key] = None

    result = {
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": URL,
        "location": "Espoo",
        "prices": {
            "95": averages["95"],
            "98": averages["98"],
            "diesel": averages["D"],
        }
    }

    return result


if __name__ == "__main__":
    data = scrape_prices()
    print(json.dumps(data, indent=2, ensure_ascii=False))

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("✅ data.json päivitetty!")
