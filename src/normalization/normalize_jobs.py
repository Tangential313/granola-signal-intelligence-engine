
import json
from pathlib import Path

def is_gtm_role(job):
    title = job["title"].lower()

    gtm_keywords = [
        "sales",
        "account executive",
        "customer success",
        "revenue operations",
    ]

    return any(keyword in title for keyword in gtm_keywords)

def normalize_job(job):
    return {
        "company": job["company"],
        "signal_type": "gtm_hiring",
        "source_url": job["url"],
        "source_type": "company_careers",
        "observed_at": job["observed_at"],
        "published_at": None,
        "evidence_text": (
            f'{job["company"]} is recruiting '
            f'{job["title"]} in {job["location"]}.'
        ),
        "entity": job["company"],
    }


BASE_DIR = Path(__file__).resolve().parents[2]
INPUT_PATH = BASE_DIR / "data" / "raw" / "granola_jobs.json"

with INPUT_PATH.open() as file:
    raw_jobs = json.load(file)

normalized_jobs = [
    normalize_job(job)
    for job in raw_jobs
    if is_gtm_role(job)
]

for job in normalized_jobs:
    print(job["evidence_text"])

OUTPUT_PATH = BASE_DIR / "data" / "processed" / "granola_signals.json"

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT_PATH.open("w") as file:
    json.dump(normalized_jobs, file, indent=2)
print(f"Normalized {len(normalized_jobs)} jobs")
print(f"Saved to {OUTPUT_PATH}")