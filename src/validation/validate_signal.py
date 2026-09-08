
 #Signal Validator
#import Signal Parser
from urllib.parse import urlparse
from datetime import datetime, timezone

def get_freshness_days(signal):
    observed_at = datetime.fromisoformat(signal["observed_at"])
    now = datetime.now(timezone.utc)

    freshness = now - observed_at

    return freshness.days

def get_recency_score(signal):
    freshness_days = get_freshness_days(signal)

    if freshness_days <= 7:
        return 1.0
    elif freshness_days <= 30:
        return 0.8
    elif freshness_days <= 90:
        return 0.5
    else:
        return 0.2
def make_dedupe_key(signal):
    return (
        signal["company"].strip().lower(),
        signal["signal_type"],
        signal["source_url"],
        signal["evidence_text"].strip().lower(),
    )

def has_matching_entity(signal):
    return (
        signal["company"].strip().lower()
        == signal["entity"].strip().lower()
    )

def is_duplicate(signal, seen_signals):
    key = make_dedupe_key(signal)

    if key in seen_signals:
        return True

    seen_signals.add(key)
    return False


def has_valid_signal_type(signal):
    return signal["signal_type"] in ALLOWED_SIGNAL_TYPES
#defining source types 
ALLOWED_SOURCE_TYPES = {
    "company_careers",
    "company_newsroom",
    "company_website",
    "investor_announcement",
    "news",
    "regulatory_filing",
    "professional_profile",
    "other",
}
SOURCE_CONFIDENCE = {
    "company_careers": 0.95,
    "company_newsroom": 0.95,
    "company_website": 0.90,
    "investor_announcement": 0.95,
    "regulatory_filing": 1.00,
    "news": 0.80,
    "professional_profile": 0.70,
    "other": 0.50,
}
ALLOWED_SIGNAL_TYPES = {
    "funding",
    "gtm_hiring",
    "leadership_change",
}
#GTM Relevance:
GTM_RELEVANCE = {
    "funding": 0.8,
    "gtm_hiring": 1.0,
    "leadership_change": 0.9,
}
def get_gtm_relevance(signal):
    return GTM_RELEVANCE.get(signal["signal_type"], 0.5)
#defining variables
def has_valid_source_url(signal):
    parsed_url = urlparse(signal["source_url"])

    return (
        parsed_url.scheme in ["http", "https"]
        and parsed_url.netloc != ""
    )

def has_valid_source_type(signal):
    return signal["source_type"] in ALLOWED_SOURCE_TYPES

def get_source_confidence(signal):
    return SOURCE_CONFIDENCE.get(signal["source_type"], 0.50)

def has_required_fields(signal):
    required_fields = [
        "company",
        "signal_type",
        "source_url",
        "source_type",
        "observed_at",
        "evidence_text",
        "entity",
    ]

    return all(
        field in signal and signal[field] not in [None, ""]
        for field in required_fields
    )

def has_valid_timestamp(signal):
    try:
        datetime.fromisoformat(signal["observed_at"])
        return True
    except ValueError:
        return False

def get_signal_score(signal):
    source_confidence = get_source_confidence(signal)
    recency_score = get_recency_score(signal)
    gtm_relevance = get_gtm_relevance(signal)

    return source_confidence * recency_score * gtm_relevance

#Validation loop
def validate_signal(signal, seen_signals):
    if not has_required_fields(signal):
        return {
            "status": "needs_review",
            "reason": "missing_required_fields"
        }
    if not has_valid_timestamp(signal):
        return {
        "status": "needs_review",
        "reason": "invalid_observed_at"
        }

    if not has_valid_source_url(signal):
        return {
            "status": "needs_review",
            "reason": "invalid_source_url"
        }

    if not has_valid_signal_type(signal):
        return {
            "status": "needs_review",
            "reason": "invalid_signal_type"
        }

    if not has_valid_source_type(signal):
        return {
            "status": "needs_review",
            "reason": "invalid_source_type"
        }
    
    if not has_matching_entity(signal):
        return {
             "status": "needs_review",
            "reason": "entity_mismatch"
    }

    if is_duplicate(signal, seen_signals):
        return {
            "status": "rejected",
            "reason": "duplicate_signal"
        }

    return {
            "status": "validated",
            "reason": None
}

#Input company values 
test_signal = {
    "company": "Granola",
    "signal_type": "gtm_hiring",
    "source_url": "https://www.granola.ai/jobs",
    "source_type": "company_careers",
    "observed_at": "2026-09-01T12:00:18+00:00",
    "evidence_text": "Granola is recruiting a Revenue Operations Lead in San Francisco.",
    "entity": "Granola"
}

seen_signals = set()

print(validate_signal(test_signal, seen_signals))
print(validate_signal(test_signal, seen_signals))
print(get_source_confidence(test_signal))
print(get_recency_score(test_signal))
print(get_signal_score(test_signal))
print(get_gtm_relevance(test_signal))