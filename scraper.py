import requests
from bs4 import BeautifulSoup
import re
import os
from statistics import mean

GOOGLE_SCRIPT_URL = os.environ["GOOGLE_SCRIPT_URL"]

URLS = [
    {
        "floorplan": "A1",
        "url": "https://livethelangston.securecafe.com/onlineleasing/langston0/availableunits.aspx?myOlePropertyId=1888891&MoveInDate=&t=0.18951492733233122&floorPlans=5473866"
    }
]

def scrape_page(floorplan, url):
    html = requests.get(url, timeout=20).text
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)

    pattern = r"(#\d+)\s+(\d{3,4})\s*\$([\d,]+)"
    matches = re.findall(pattern, text)

    rows = []
    for unit, sqft, rent in matches:
        sqft = int(sqft)
        rent = int(rent.replace(",", ""))

        rows.append({
            "floorplan": floorplan,
            "unit": unit.replace("#", ""),
            "sqft": sqft,
            "rent": rent,
            "rent_per_sqft": round(rent / sqft, 2),
            "url": url
        })

    return rows

all_units = []

for item in URLS:
    all_units.extend(scrape_page(item["floorplan"], item["url"]))

summary = []

for floorplan in sorted(set(row["floorplan"] for row in all_units)):
    rows = [row for row in all_units if row["floorplan"] == floorplan]

    rents = [row["rent"] for row in rows]
    sqfts = [row["sqft"] for row in rows]
    rent_per_sqfts = [row["rent_per_sqft"] for row in rows]

    summary.append({
        "floorplan": floorplan,
        "available_units": len(rows),
        "avg_rent": round(mean(rents), 2),
        "avg_sqft": round(mean(sqfts), 2),
        "avg_rent_per_sqft": round(mean(rent_per_sqfts), 2),
        "min_rent": min(rents),
        "max_rent": max(rents)
    })

payload = {
    "units": all_units,
    "summary": summary
}

if all_units:
    response = requests.post(GOOGLE_SCRIPT_URL, json=payload, timeout=20)
    print(response.text)
else:
    print("No available units found.")
