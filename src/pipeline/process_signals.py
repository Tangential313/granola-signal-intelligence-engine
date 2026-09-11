import json
from pathlib import Path

from src.validation.validate_signal import validate_signal, get_signal_score
BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_PATH = BASE_DIR / "data" / "processed" / "granola_signals.json"
OUTPUT_PATH = BASE_DIR / "data" / "processed" / "granola_validated_signals.json"


with INPUT_PATH.open() as file:
    signals = json.load(file)


import json
from pathlib import Path

from src.validation.validate_signal import validate_signal, get_signal_score


BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_PATH = BASE_DIR / "data" / "processed" / "granola_all_signals.json"
OUTPUT_PATH = BASE_DIR / "data" / "processed" / "granola_validated_signals.json"


with INPUT_PATH.open() as file:
    signals = json.load(file)


seen_signals = set()
processed_signals = []

for signal in signals:
    validation = validate_signal(signal, seen_signals)

    signal["validation_status"] = validation["status"]
    signal["validation_reason"] = validation["reason"]

    if validation["status"] == "validated":
        signal["signal_score"] = get_signal_score(signal)

    processed_signals.append(signal)


OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT_PATH.open("w") as file:
    json.dump(processed_signals, file, indent=2)


validated_count = sum(
    1
    for signal in processed_signals
    if signal["validation_status"] == "validated"
)

print(f"Loaded {len(signals)} normalized signals")
print(f"Validated {validated_count} signals")
print(f"Saved to {OUTPUT_PATH}")