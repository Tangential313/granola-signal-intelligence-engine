# Signal Data Contract

This document defines the canonical shape of a signal record used by the Granola Signal Intelligence Engine.

The purpose of the contract is simple: every observed signal should enter the system in a consistent, traceable format before enrichment, scoring, or hypothesis generation occurs.

## Core principle

The pipeline separates **observed evidence** from **derived logic** and **generated interpretation**.

A signal record should therefore answer three questions:

1. What did we observe?
2. Where did the observation come from?
3. Has the record passed validation strongly enough to be used downstream?

## Canonical signal record

```json
{
  "company": "Granola",
  "signal_type": "gtm_hiring",
  "source_url": "https://example.com/source",
  "source_type": "company_careers",
  "observed_at": "2026-08-31T00:00:00Z",
  "published_at": "2026-08-29T00:00:00Z",
  "evidence_text": "Synthetic example evidence describing an open GTM role.",
  "entity": "Granola",
  "freshness_days": 2,
  "source_confidence": 0.95,
  "validation_status": "validated",
  "notes": "Synthetic example only. Not a real Granola signal."
}
```

> **Important:** The example above is synthetic and exists only to demonstrate structure. Real signal records must contain verifiable public evidence.

## Field definitions

| Field | Type | Required | Description |
|---|---|---:|---|
| `company` | string | yes | Normalised company name used throughout the pipeline. |
| `signal_type` | enum/string | yes | Category assigned to the observed event, such as `funding`, `gtm_hiring`, or `leadership_change`. |
| `source_url` | string | yes | Direct URL to the evidence source. |
| `source_type` | enum/string | yes | Source category, such as `company_careers`, `company_newsroom`, `news`, or `regulatory_filing`. |
| `observed_at` | ISO 8601 datetime | yes | Timestamp when the engine captured or reviewed the signal. |
| `published_at` | ISO 8601 datetime/null | no | Publication or event date where known. |
| `evidence_text` | string | yes | Concise factual extract or paraphrase describing the observed event. |
| `entity` | string | yes | Entity to which the signal applies. Usually the company, but may later support people, products, or business units. |
| `freshness_days` | integer | derived | Number of days between `published_at` and `observed_at`. |
| `source_confidence` | float 0.0–1.0 | derived/assigned | Confidence in the source as evidence for the claimed event. |
| `validation_status` | enum | yes | Current validation outcome: `pending`, `validated`, `needs_review`, or `rejected`. |
| `notes` | string/null | no | Analyst or system notes, ambiguity flags, or context that should not be stored inside the factual evidence field. |

## Initial signal types

Version 1 will focus on three signal categories:

### `funding`

Evidence that the company has raised capital or announced a financing event.

Potential sources:

- company newsroom or founder announcement
- investor announcement
- reputable business or technology publication
- regulatory filing where relevant

### `gtm_hiring`

Evidence that the company is recruiting roles associated with commercial growth, including sales, marketing, partnerships, revenue operations, customer success, or GTM leadership.

Potential sources:

- company careers page
- applicant tracking system
- verified company LinkedIn jobs page

### `leadership_change`

Evidence of a new senior leader or material leadership change relevant to commercial strategy, operations, product, or expansion.

Potential sources:

- company announcement
- executive profile
- reputable publication

Additional categories may be introduced only after the first end-to-end pipeline is working.

## Source types

Initial accepted values:

```text
company_careers
company_newsroom
company_website
investor_announcement
news
regulatory_filing
professional_profile
other
```

A source type describes **where the evidence came from**, not what the signal means.

## Validation statuses

### `pending`

The record has been captured but validation has not been completed.

### `validated`

The evidence supports the signal, entity resolution is correct, and the record is suitable for downstream scoring.

### `needs_review`

The signal is plausible but one or more elements are ambiguous, incomplete, or conflicting.

### `rejected`

The evidence is stale, duplicated, misattributed, unsupported, or otherwise unsuitable for downstream use.

## Validation rules

A record should not receive `validated` status unless the following checks pass.

### 1. Source traceability

- `source_url` must be present and reachable at time of capture.
- The source must support the factual claim represented by `evidence_text`.
- Generated text is never accepted as the original evidence source.

### 2. Entity match

- The signal must clearly refer to the intended company or entity.
- Similar company names, subsidiaries, and acquired brands should be checked before validation.

### 3. Timestamp and freshness

- `observed_at` is always recorded.
- `published_at` should be captured where available.
- `freshness_days` must be calculated deterministically, not generated by an LLM.

### 4. Duplicate detection

Potential duplicates should be checked using a combination of:

- company
- signal type
- source URL
- event or publication date
- materially equivalent evidence

Multiple independent sources supporting the same event may be retained as corroborating evidence, but they should not be treated as multiple separate commercial events.

### 5. Evidence vs interpretation

`evidence_text` contains what is observed.

It must not contain speculative conclusions such as:

```text
Granola is definitely preparing to enter enterprise sales.
```

A factual record might instead state:

```text
Granola has advertised three enterprise account executive roles.
```

The first is a hypothesis. The second is observable evidence.

### 6. Confidence assignment

`source_confidence` represents confidence in the source as evidence for the event, not confidence in a later GTM hypothesis.

Initial guidance:

| Confidence | Interpretation |
|---:|---|
| 0.90–1.00 | Primary or highly authoritative source |
| 0.75–0.89 | Strong secondary source |
| 0.50–0.74 | Useful but requires corroboration |
| below 0.50 | Insufficient for automatic downstream use |

These thresholds are provisional and may change after testing.

## Observed vs derived vs generated fields

The project intentionally distinguishes data lineage.

### Observed

Directly captured from evidence:

```text
company
signal_type
source_url
source_type
observed_at
published_at
evidence_text
entity
```

### Derived

Calculated through deterministic logic:

```text
freshness_days
validation_status
source_confidence
```

### Generated later

Produced after validated records are available:

```text
signal_score
account_priority_score
account_hypothesis
recommended_crm_action
hypothesis_confidence
```

Generated fields do not overwrite the evidence layer.

## Minimum viable record

A signal cannot enter downstream scoring without:

```text
company
signal_type
source_url
source_type
observed_at
evidence_text
entity
validation_status = validated
```

If a required field cannot be established, the record remains `needs_review` or is rejected.

## Why this matters

Signal intelligence is only useful if the system can explain **why it believes something happened**.

This data contract creates that audit trail before scoring or LLM interpretation begins, making it possible to inspect the evidence, challenge assumptions, debug incorrect outputs, and measure false positives later in the pipeline.

## Next implementation step

Create the first Granola evidence dataset using this contract, beginning with:

1. funding
2. GTM hiring
3. leadership change

Those records will become the input for the project's first validation and scoring logic.
