# Signal Validator
from urllib.parse import urlparse

ALLOWED_SIGNAL_TYPES = {
    "funding",
    "gtm_hiring",
    "leadership_change",
}

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


def has_valid_signal_type(signal):
    return signal["signal_type"] in ALLOWED_SIGNAL_TYPES


def has_valid_source_url(signal):
    parsed_url = urlparse(signal["source_url"])

    return (
        parsed_url.scheme in ["http", "https"]
        and parsed_url.netloc != ""
    )


def has_valid_source_type(signal):
    return signal["source_type"] in ALLOWED_SOURCE_TYPES


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


def validate_signal(signal):
    if not has_required_fields(signal):
        return {
            "status": "needs_review",
            "reason": "missing_required_fields",
        }

    if not has_valid_source_url(signal):
        return {
            "status": "needs_review",
            "reason": "invalid_source_url",
        }

    if not has_valid_signal_type(signal):
        return {
            "status": "needs_review",
            "reason": "invalid_signal_type",
        }

    if not has_valid_source_type(signal):
        return {
            "status": "needs_review",
            "reason": "invalid_source_type",
        }

    return {
        "status": "validated",
        "reason": None,
    }


if __name__ == "__main__":
    test_signal = {
        "company": "Granola",
        "signal_type": "gtm_hiring",
        "source_url": "https://www.granola.ai/jobs",
        "source_type": "company_careers",
        "observed_at": "2026-09-01T12:00:18+00:00",
        "evidence_text": "Granola is recruiting a Revenue Operations Lead in San Francisco.",
        "entity": "Granola",
    }

    print(validate_signal(test_signal))
