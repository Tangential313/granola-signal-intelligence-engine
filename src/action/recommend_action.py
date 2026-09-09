import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "granola_hypothesis.json"
)

OUTPUT_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "granola_action.json"
)


with INPUT_PATH.open() as file:
    hypothesis_record = json.load(file)


cluster_type = hypothesis_record["cluster_type"]
cluster_strength = hypothesis_record["cluster_strength"]


if (
    cluster_type == "full_funnel_gtm_buildout"
    and cluster_strength == "strong"
):
    recommended_action = (
        "Prioritize this account for strategic outreach focused on "
        "GTM infrastructure, segmentation, routing, forecasting, "
        "and cross-functional revenue operations."
    )
else:
    recommended_action = (
        "Keep the account under observation and wait for additional "
        "signals before prioritizing strategic outreach."
    )


action_record = {
    "company": hypothesis_record["company"],
    "hypothesis": hypothesis_record["hypothesis"],
    "hypothesis_confidence": hypothesis_record["hypothesis_confidence"],
    "recommended_crm_action": recommended_action,
}


with OUTPUT_PATH.open("w") as file:
    json.dump(action_record, file, indent=2)


print(f"Recommended action: {recommended_action}")
print(f"Saved action to {OUTPUT_PATH}")