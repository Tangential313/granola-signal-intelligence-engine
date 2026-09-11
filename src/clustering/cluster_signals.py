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
    role = signal["role_title"].lower()

    if "sales development representative" in role:
        return "pipeline_generation"

    if "account executive" in role:
        return "revenue_conversion"

    if "customer success" in role:
        return "customer_success"

    if "revenue operations" in role:
        return "commercial_infrastructure"

    return "other"

with INPUT_PATH.open() as file:
    signals = json.load(file)

print(f"Loaded {len(signals)} validated signals")

hiring_signals = [
    signal
    for signal in signals
    if signal["signal_type"] == "gtm_hiring"
]

capabilities = [
    get_capability(signal)
    for signal in hiring_signals
]

capability_counts = Counter(capabilities)

signal_families = sorted({
    signal["signal_type"]
    for signal in signals
})

hiring_evidence_count = sum(capability_counts.values())
total_evidence_count = len(signals)

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

capability_breadth = len(
    required_capabilities.intersection(capability_counts.keys())
)
hiring_evidence_count = sum(capability_counts.values())
total_evidence_count = len(signals)

if capability_breadth == 4 and hiring_evidence_count >= 7:
    cluster_strength = "strong"
elif capability_breadth >= 3 and hiring_evidence_count >= 4:
    cluster_strength = "moderate"
else:
    cluster_strength = "weak"

    
supporting_signal_ids = [
    signal["signal_id"]
    for signal in signals
]

companies = {signal["company"] for signal in signals}

if len(companies) != 1:
    raise ValueError("Expected signals from exactly one company")

company = companies.pop()

cluster = {
    "company": company,
    "cluster_type": cluster_type,
    "cluster_strength": cluster_strength,
    "signal_families": signal_families,
    "capability_counts": dict(capability_counts),
    "hiring_evidence_count": hiring_evidence_count,
    "total_evidence_count": total_evidence_count,
    "supporting_signal_ids": supporting_signal_ids,
}

with OUTPUT_PATH.open("w") as file:
    json.dump(cluster, file, indent=2)

print(f"Cluster strength: {cluster_strength}")
print(f"Cluster type: {cluster_type}") 
print(f"Saved cluster to {OUTPUT_PATH}")
print(capability_counts)
print(capabilities)
