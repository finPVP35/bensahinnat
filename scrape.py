import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timezone

URL = "https://polttoaine.net/index.php"

def scrape_prices():
    headers = {"User-Agent": "Mozilla/5.0 (compatible; bensahinnat-bot/1.0)"}
    resp = requests.get(URL, headers=headers, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    keskihinnat_row = None
    rows = soup.find_all("tr")
    for i, row in enumerate(rows):
        if "keskihinnat" in row.get_text().lower():
            if i + 1 < len(rows):
                keskihinnat_row = rows[i + 1].find_all("td")
            break

    if not keskihinnat_row:
        raise ValueError("Keskihinnat-riviä ei löydy sivulta!")

    prices = []
    for cell in keskihinnat_row:
        text = cell.get_text(strip=True).replace(",", ".")
        try:
            val = float(text)
            if 0.5 < val < 5.0:
                prices.append(val)
        except ValueError:
            pass

    if len(prices) < 3:
        raise ValueError(f"Löydettiin vain {len(prices)} hintaa, odotettiin 3")

    result = {
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": URL,
        "location": "Suomi (koko maa)",
        "prices": {
            "95": prices[0],
            "98": prices[1],
            "diesel": prices[2],
        }
    }
    return result

if __name__ == "__main__":
    data = scrape_prices()
    print(json.dumps(data, indent=2, ensure_ascii=False))
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("✅ data.json päivitetty!")
