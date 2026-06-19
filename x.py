

import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()

API_URL = "https://api.myscheme.gov.in/schemes/v6/public/schemes?slug=ioap&lang=en"

HEADERS = {
    "x-api-key": os.getenv("MY_SCHEME_API"),
    "Origin": "https://www.myscheme.gov.in",
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(
    API_URL,
    headers=HEADERS,
    timeout=30
)

response.raise_for_status()

data = response.json()
print(data)
