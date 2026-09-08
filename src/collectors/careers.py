import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

URL = "https://www.granola.ai/jobs"

BASE_DIR = Path(__file__).resolve().parents[2]
OUTPUT_PATH = BASE_DIR / "data" / "raw" / "granola_jobs.json"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(
    URL,
    headers=headers,
    timeout=10
)

response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")
links = soup.find_all("a")

seen = set()
jobs = []
observed_at = datetime.now(timezone.utc).isoformat()

for link in links:
    href = link.get("href")

    if href and href.startswith("/jobs/"):
        job_parts = link.find_all("p")

        if len(job_parts) < 2:
            continue

        title = job_parts[0].get_text(strip=True)
        location = job_parts[1].get_text(strip=True)

        dedupe_key = (href, title, location)

        if dedupe_key not in seen:
            seen.add(dedupe_key)

            job = {
                "company": "Granola",
                "title": title,
                "location": location,
                "url": urljoin(URL, href),
                "source_url": URL,
                "observed_at": observed_at
            }

            jobs.append(job)

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT_PATH.open("w") as file:
    json.dump(jobs, file, indent=2)

print(f"Collected {len(jobs)} jobs")
print(f"Saved to {OUTPUT_PATH}")
