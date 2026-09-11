import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

HIRING_PATH = BASE_DIR / "data" / "processed" / "granola_signals.json"
FUNDING_PATH = BASE_DIR / "data" / "processed" / "granola_funding_signals.json"
OUTPUT_PATH = BASE_DIR / "data" / "processed" / "granola_all_signals.json"


with HIRING_PATH.open() as file:
    hiring_signals = json.load(file)

with FUNDING_PATH.open() as file:
    funding_signals = json.load(file)


all_signals = hiring_signals + funding_signals


with OUTPUT_PATH.open("w") as file:
    json.dump(all_signals, file, indent=2)


print(f"Hiring signals: {len(hiring_signals)}")
print(f"Funding signals: {len(funding_signals)}")
print(f"Total canonical signals: {len(all_signals)}")
print(f"Saved to {OUTPUT_PATH}")
