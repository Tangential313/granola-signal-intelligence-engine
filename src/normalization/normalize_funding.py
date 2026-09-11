import json
import hashlib
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_PATH = BASE_DIR / "data" / "raw" / "granola_funding.json"
OUTPUT_PATH = BASE_DIR / "data" / "processed" / "granola_funding_signals.json"


def make_signal_id(signal):
    identity = (
        f'{signal["company"]}|'
        f'{signal["signal_type"]}|'
        f'{signal["source_url"]}|'
        f'{signal["published_at"]}'
    )

    digest = hashlib.sha256(identity.encode()).hexdigest()[:12]

    return f"sig_{digest}"


with INPUT_PATH.open() as file:
    funding_records = json.load(file)


normalized_funding = []

for record in funding_records:
    normalized_funding.append(
        {
            "signal_id": make_signal_id(record),
            "company": record["company"],
            "signal_type": record["signal_type"],
            "source_url": record["source_url"],
            "source_type": record["source_type"],
            "observed_at": record["observed_at"],
            "published_at": record["published_at"],
            "evidence_text": record["evidence_text"],
            "entity": record["entity"],
        }
    )


OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT_PATH.open("w") as file:
    json.dump(normalized_funding, file, indent=2)


print(f"Normalized {len(normalized_funding)} funding signals")
print(f"Saved to {OUTPUT_PATH}")