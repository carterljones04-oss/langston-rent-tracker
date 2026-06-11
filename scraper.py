import requests
from bs4 import BeautifulSoup
import re
import os
from statistics import mean

GOOGLE_SCRIPT_URL = os.environ["GOOGLE_SCRIPT_URL"]

print("VERSION 2 TEST")

URLS = [
    {"floorplan": "A1", "url": "https://livethelangston.securecafe.com/onlineleasing/langston0/availableunits.aspx?myOlePropertyId=1888891&floorPlans=5473866"},
    {"floorplan": "A2", "url": "https://livethelangston.securecafe.com/onlineleasing/langston0/availableunits.aspx?myOlePropertyId=1888891&floorPlans=5473870"},
    {"floorplan": "A3", "url": "https://livethelangston.securecafe.com/onlineleasing/langston0/availableunits.aspx?myOlePropertyId=1888891&floorPlans=5475000"},
    {"floorplan": "A4", "url": "https://livethelangston.securecafe.com/onlineleasing/langston0/availableunits.aspx?myOlePropertyId=1888891&floorPlans=5473890"},
    {"floorplan": "A5.a", "url": "https://livethelangston.securecafe.com/onlineleasing/langston0/availableunits.aspx?myOlePropertyId=1888891&floorPlans=5473891"},
    {"floorplan": "B1", "url": "https://livethelangston.securecafe.com/onlineleasing/langston0/availableunits.aspx?myOlePropertyId=1888891&floorPlans=5473932"},
    {"floorplan": "C1", "url": "https://livethelangston.securecafe.com/onlineleasing/langston0/availableunits.aspx?myOlePropertyId=1888891&floorPlans=5474983"},
    {"floorplan": "C3", "url": "https://livethelangston.securecafe.com/onlineleasing/langston0/availableunits.aspx?myOlePropertyId=1888891&floorPlans=5474987"},
    {"floorplan": "C5", "url": "https://livethelangston.securecafe.com/onlineleasing/langston0/availableunits.aspx?myOlePropertyId=1888891&floorPlans=5474989"},
    {"floorplan": "C6", "url": "https://livethelangston.securecafe.com/onlineleasing/langston0/availableunits.aspx?myOlePropertyId=1888891&floorPlans=5474990"},
]

def scrape_page(floorplan, url):
    html = requests.get(url, timeout=20).text
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)

    pattern = r"#?(\d{3,5})\s+(\d{3,4})\s*\$([\d,]+)"
    matches = re.findall(pattern, text)

    rows = []

    for unit, sqft, rent in matches:
        sqft = int(sqft)
        rent = int(rent.replace(",", ""))

        rows.append({
            "floorplan": floorplan,
            "unit": unit,
            "sqft": sqft,
            "rent": rent,
            "rent_per_sqft": round(rent / sqft, 2),
            "url": url
        })

    print(f"{floorplan}: found {len(rows)} units")
    return rows

all_units = []
summary = []

for item in URLS:
    floorplan = item["floorplan"]
    url = item["url"]

    rows = scrape_page(floorplan, url)
    all_units.extend(rows)

    if rows:
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
    else:
        summary.append({
            "floorplan": floorplan,
            "available_units": 0,
            "avg_rent": "",
            "avg_sqft": "",
            "avg_rent_per_sqft": "",
            "min_rent": "",
            "max_rent": ""
        })

payload = {
    "units": all_units,
    "summary": summary
}

response = requests.post(GOOGLE_SCRIPT_URL, json=payload, timeout=20)
print(response.text)
