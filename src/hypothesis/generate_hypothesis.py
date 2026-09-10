import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "granola_cluster.json"
)

OUTPUT_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "granola_hypothesis.json"
)

with INPUT_PATH.open() as file:
    cluster = json.load(file)

print(cluster)
cluster_type = cluster["cluster_type"]
cluster_strength = cluster["cluster_strength"]

if (
    cluster_type == "full_funnel_gtm_buildout"
    and cluster_strength == "strong"
):
    hypothesis = (
        "Granola appears to be deliberately building a more mature, "
        "segmented GTM organisation across pipeline generation, "
        "revenue conversion, customer success, and commercial infrastructure."
    )
else:
    hypothesis = (
        "Granola shows signs of GTM development, but the current signal cluster "
        "is not strong enough to support a full-funnel buildout hypothesis."
    )

print(f"Hypothesis: {hypothesis}")

hypothesis_record = {
    "company": cluster["company"],
    "cluster_type": cluster_type,
    "cluster_strength": cluster_strength,
    "hypothesis": hypothesis,
    "hypothesis_confidence": 0.9 if cluster_strength == "strong" else 0.6,
    "supporting_evidence": cluster["capability_counts"],
    "supporting_signal_ids": cluster["supporting_signal_ids"],
}

with OUTPUT_PATH.open("w") as file:
    json.dump(hypothesis_record, file, indent=2)

print(f"Saved hypothesis to {OUTPUT_PATH}")