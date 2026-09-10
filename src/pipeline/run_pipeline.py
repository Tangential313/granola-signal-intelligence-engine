import subprocess
import sys


STEPS = [
    "src.normalization.normalize_jobs",
    "src.pipeline.process_signals",
    "src.clustering.cluster_signals",
    "src.hypothesis.generate_hypothesis",
    "src.action.recommend_action",
]


for step in STEPS:
    print(f"\nRunning: {step}")
    subprocess.run(
        [sys.executable, "-m", step],
        check=True,
    )

print("\nPipeline complete.")
