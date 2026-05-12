import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timezone

URL = "https://polttoaine.net/espoo"

def scrape_prices():
    headers = {"User-Agent": "Mozilla/5.0 (compatible; bensahinnat-bot/1.0)"}
    resp = requests.get(URL, headers=headers, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # Etsi rivi jossa lukee "Keskihinnat:" — se on suoraan sivulla ylimpänä
    keskihinnat_row = None
    for row in soup.find_all("tr"):
        cells = row.find_all("td")
        for cell in cells:
            if "Keskihinnat" in cell.get_text():
                keskihinnat_row = cells
                break
        if keskihinnat_row:
            break

    if not keskihinnat_row:
        raise ValueError("Keskihinnat-riviä ei löydy sivulta!")

    # Kerää numeeriset arvot soluista
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
        "location": "Espoo",
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
