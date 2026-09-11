from pathlib import Path
import sys
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.normalization.normalize_jobs import make_signal_id
from src.clustering.cluster_signals import get_capability
from src.validation.validate_signal import validate_signal
from collections import Counter

from src.clustering.cluster_signals import (
    get_capability_breadth,
    get_cluster_strength,
    get_signal_families,
)

def test_other_capability_does_not_inflate_breadth():
    capability_counts = Counter({
        "pipeline_generation": 1,
        "revenue_conversion": 1,
        "customer_success": 1,
        "commercial_infrastructure": 1,
        "other": 5,
    })

    required_capabilities = {
        "pipeline_generation",
        "revenue_conversion",
        "customer_success",
        "commercial_infrastructure",
    }

    breadth = get_capability_breadth(
        capability_counts,
        required_capabilities,
    )

    assert breadth == 4


def test_full_breadth_and_seven_hiring_signals_is_strong():
    strength = get_cluster_strength(
        capability_breadth=4,
        hiring_evidence_count=7,
    )

    assert strength == "strong"


def test_signal_families_are_distinct_and_sorted():
    signals = [
        {"signal_type": "gtm_hiring"},
        {"signal_type": "gtm_hiring"},
        {"signal_type": "funding"},
    ]

    families = get_signal_families(signals)

    assert families == ["funding", "gtm_hiring"]

def test_same_url_different_location_gets_different_signal_ids():
    london_job = {
        "company": "Granola",
        "title": "Sales Development Representative",
        "location": "London",
        "url": "https://www.granola.ai/jobs/sales-development-representative",
    }

    sf_job = {
        "company": "Granola",
        "title": "Sales Development Representative",
        "location": "San Francisco Office",
        "url": "https://www.granola.ai/jobs/sales-development-representative",
    }

    london_id = make_signal_id(london_job)
    sf_id = make_signal_id(sf_job)

    assert london_id != sf_id


def test_gtm_role_maps_to_expected_capability():
    signal = {
        "role_title": "Account Executive, Enterprise"
    }

    assert get_capability(signal) == "revenue_conversion"


def test_funding_signal_validates():
    signal = {
        "signal_id": "sig_testfunding",
        "company": "Granola",
        "signal_type": "funding",
        "source_url": "https://www.granola.ai/blog/series-c",
        "source_type": "company_newsroom",
        "observed_at": "2026-09-10T00:00:00+00:00",
        "published_at": "2026-03-25T00:00:00+00:00",
        "evidence_text": "Granola announced a $125M Series C.",
        "entity": "Granola",
    }

def test_partial_capability_coverage_is_not_full_funnel():
    capability_counts = Counter({
        "pipeline_generation": 2,
        "revenue_conversion": 2,
        "customer_success": 1,
    })

    required_capabilities = {
        "pipeline_generation",
        "revenue_conversion",
        "customer_success",
        "commercial_infrastructure",
    }

    breadth = get_capability_breadth(
        capability_counts,
        required_capabilities,
    )

    assert breadth == 3


def test_funding_does_not_become_a_hiring_capability():
    signals = [
        {
            "signal_type": "gtm_hiring",
            "role_title": "Account Executive, Enterprise",
        },
        {
            "signal_type": "funding",
        },
    ]

    hiring_signals = [
        signal
        for signal in signals
        if signal["signal_type"] == "gtm_hiring"
    ]

    capabilities = [
        get_capability(signal)
        for signal in hiring_signals
    ]

    assert capabilities == ["revenue_conversion"]
