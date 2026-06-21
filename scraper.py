import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()

API_URL = "https://api.myscheme.gov.in/search/v6/schemes"

HEADERS = {
    "x-api-key": os.getenv("MY_SCHEME_API"),
    "Origin": "https://www.myscheme.gov.in",
    "User-Agent": "Mozilla/5.0"
}


def search_schemes(filters):
    params = {
        "lang": "en",
        "q": json.dumps(filters),
        "keyword": "",
        "sort": "",
        "from": 0,
        "size": 20
    }

    response = requests.get(
        API_URL,
        params=params,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    return data["data"]["hits"]["items"]