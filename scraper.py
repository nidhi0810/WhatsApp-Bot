import requests
import json
import time
import os
from dotenv import load_dotenv
load_dotenv()

API_URL = "https://api.myscheme.gov.in/search/v6/schemes"
HEADERS = {
    "x-api-key": os.getenv("MY_SCHEME_API"),
    "Origin": "https://www.myscheme.gov.in",
    "User-Agent": "Mozilla/5.0"
}

# ==========================
# HARDCODED USER PROFILE
# ==========================

filters = [
    {"identifier":"caste","value":"SC"},
    {"identifier":"gender","value":"Female"},
    {"identifier":"beneficiaryState","value":"Maharashtra"},
    {"identifier":"schemeCategory","value":"Education & Learning"},
]
# ==========================
# FETCH ALL SCHEMES
# ==========================

all_schemes = []

offset = 0
page_size = 100

while True:

    params = {
        "lang": "en",
        "q": json.dumps(filters),
        "keyword": "",
        "sort": "",
        "from": offset,
        "size": page_size
    }

    response = requests.get(
        API_URL,
        params=params,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()
    print(response.status_code)
    print(response.text[:1000])
    data = response.json()

    items = data["data"]["hits"]["items"]

    if not items:
        break

    all_schemes.extend(items)

    print(f"Fetched {len(all_schemes)} schemes")

    offset += page_size

    time.sleep(0.5)

print("\n")
print("=" * 100)
print("TOTAL SCHEMES FOUND:", len(all_schemes))
print("=" * 100)

# ==========================
# DISPLAY SCHEMES
# ==========================
print(data["data"]["hits"]["page"])
for i, scheme in enumerate(all_schemes, start=1):

    fields = scheme.get("fields", {})

    print("\n" + "=" * 100)
    print(f"{i}. {fields.get('schemeName', 'N/A')}")
    print("=" * 100)

    print("Ministry:")
    print(fields.get("nodalMinistryName", "N/A"))

    print("\nCategory:")
    print(", ".join(fields.get("schemeCategory", [])))

    print("\nLevel:")
    print(fields.get("level", "N/A"))

    print("\nScheme For:")
    print(fields.get("schemeFor", "N/A"))

    print("\nDescription:")
    print(fields.get("briefDescription", "N/A"))

    print("\nTags:")
    print(", ".join(fields.get("tags", [])))

    print("\nSlug:")
    print(fields.get("slug", "N/A"))

# ==========================
# SAVE JSON
# ==========================

with open("schemes.json", "w", encoding="utf-8") as f:
    json.dump(all_schemes, f, indent=2, ensure_ascii=False)

print("\nSaved to schemes.json")