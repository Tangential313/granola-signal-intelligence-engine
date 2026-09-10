import json
from pathlib import Path
from collections import Counter


BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "granola_validated_signals.json"
)
OUTPUT_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "granola_cluster.json"
)


def get_capability(signal):
    evidence = signal["evidence_text"].lower()

    if "sales development representative" in evidence:
        return "pipeline_generation"

    if "account executive" in evidence:
        return "revenue_conversion"

    if "customer success manager" in evidence:
        return "customer_success"

    if "revenue operations" in evidence:
        return "commercial_infrastructure"

    return "other"

with INPUT_PATH.open() as file:
    signals = json.load(file)

print(f"Loaded {len(signals)} validated signals")
capabilities = [
    get_capability(signal)
    for signal in signals
]

capability_counts = Counter(capabilities)
required_capabilities = {
    "pipeline_generation",
    "revenue_conversion",
    "customer_success",
    "commercial_infrastructure",
}

if required_capabilities.issubset(capability_counts.keys()):
    cluster_type = "full_funnel_gtm_buildout"
else:
    cluster_type = "partial_gtm_buildout"

capability_breadth = len(capability_counts)
evidence_count = sum(capability_counts.values())

if capability_breadth == 4 and evidence_count >= 7:
    cluster_strength = "strong"
elif capability_breadth >= 3 and evidence_count >= 4:
    cluster_strength = "moderate"
else:
    cluster_strength = "weak"

supporting_signal_ids = [
    signal["signal_id"]
    for signal in signals
]

cluster = {
    "company": "Granola",
    "cluster_type": cluster_type,
    "cluster_strength": cluster_strength,
    "capability_counts": dict(capability_counts),
    "evidence_count": evidence_count,
    "supporting_signal_ids": supporting_signal_ids,
}

with OUTPUT_PATH.open("w") as file:
    json.dump(cluster, file, indent=2)

print(f"Cluster strength: {cluster_strength}")
print(f"Cluster type: {cluster_type}") 
print(f"Saved cluster to {OUTPUT_PATH}")
print(capability_counts)
print(capabilities)
