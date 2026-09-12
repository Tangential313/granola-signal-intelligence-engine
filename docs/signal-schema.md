# Signal Schema

The Signal Intelligence Engine uses a canonical signal schema to separate raw source records from downstream GTM interpretation.

The goal is to preserve three things:

1. **Evidence integrity**  
   What was actually observed from the source?

2. **Consistent downstream processing**  
   Can different signal types pass through the same validation and scoring layer?

3. **Traceability**  
   Can a hypothesis or CRM action be traced back to the evidence that produced it?

## Canonical signal record

A normalized signal is represented as a JSON object.

Example:

```json
{
  "signal_id": "sig_f076e552c96c",
  "company": "Granola",
  "signal_type": "gtm_hiring",
  "source_url": "https://www.granola.ai/jobs/revenue-operations-lead",
  "source_type": "company_careers",
  "observed_at": "2026-09-10T00:00:00+00:00",
  "published_at": null,
  "evidence_text": "Granola is recruiting Revenue Operations Lead - US in San Francisco Office.",
  "entity": "Granola",
  "role_title": "Revenue Operations Lead - US",
  "location": "San Francisco Office"
}
```

## Core fields

These fields form the shared canonical layer.

| Field | Type | Description |
|---|---|---|
| `signal_id` | string | Deterministic identifier for the normalized evidence record |
| `company` | string | Company associated with the signal |
| `signal_type` | string | Category of observed event |
| `source_url` | string | Public source URL supporting the record |
| `source_type` | string | Type of source used |
| `observed_at` | ISO 8601 timestamp | When the engine observed the evidence |
| `published_at` | ISO 8601 timestamp or `null` | When the underlying event or source was published, if known |
| `evidence_text` | string | Concise factual description of the observed evidence |
| `entity` | string | Entity named by the source and used for entity matching |

## Signal IDs

Each canonical signal receives a deterministic `signal_id`.

For hiring records, the current identity is derived from:

```text
company
+ role title
+ location
+ source URL
```

The resulting string is hashed and shortened into a value such as:

```text
sig_f076e552c96c
```

This ensures that two roles sharing the same source URL can still remain distinct if other identifying fields differ.

For example:

```text
Sales Development Representative
London
```

and:

```text
Sales Development Representative
San Francisco
```

may share the same careers-page URL while remaining separate signal records.

Signal IDs are deterministic within the current identity rules, but they should not be treated as permanent external entity IDs. If identifying source fields change, the resulting signal ID may also change.

## Current signal types

The implemented engine currently supports:

```text
gtm_hiring
funding
```

The validation layer also reserves support for:

```text
leadership_change
```

Future signal families may include:

```text
geographic_expansion
product_expansion
technology_change
```

These future types are not yet implemented collectors or normalizers.

## Source types

Current allowed source types include:

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

The source type contributes to source-confidence scoring.

Examples:

```text
company_careers       → high-confidence first-party hiring evidence
company_newsroom      → high-confidence first-party company evidence
regulatory_filing     → high-confidence formal disclosure
news                  → supporting third-party evidence
professional_profile  → supporting individual or leadership evidence
```

## Signal-specific fields

Not every signal family should be forced into the same shape.

The canonical schema therefore contains a shared core plus signal-specific fields.

### GTM hiring

Hiring signals currently include:

```json
{
  "role_title": "Account Executive, Enterprise",
  "location": "San Francisco Office"
}
```

These structured fields are intentionally retained rather than forcing downstream logic to parse natural-language `evidence_text`.

The clustering layer uses `role_title` to map hiring evidence into GTM capabilities.

### Funding

Funding records currently rely on the shared canonical fields:

```json
{
  "signal_type": "funding",
  "source_type": "company_newsroom",
  "published_at": "2026-03-25T00:00:00+00:00",
  "evidence_text": "Granola announced a $125M Series C at a $1.5B valuation, led by Index Ventures."
}
```

Funding-specific structured metadata such as round size, round type, valuation, or lead investor may be added later.

The current implementation deliberately avoids inventing fields until downstream logic needs them.

## Observed, derived, and generated data

The engine separates data into three conceptual layers.

### 1. Observed fields

Observed fields describe evidence captured from the source.

Examples:

```text
company
signal_type
source_url
source_type
observed_at
published_at
evidence_text
entity
role_title
location
```

These fields should remain factual and source-grounded.

For example:

```text
Granola announced a $125M Series C.
```

is an observed fact.

This would not be appropriate in the observed layer:

```text
Granola raised funding in order to accelerate GTM expansion.
```

unless the source explicitly stated that causal relationship.

### 2. Derived fields

Derived fields are produced by deterministic engine logic.

Examples include:

```text
validation_status
validation_reason
signal_score
cluster_type
cluster_strength
capability_counts
hiring_evidence_count
total_evidence_count
signal_families
supporting_signal_ids
```

Freshness, recency weighting, source confidence, and GTM relevance are currently calculated or looked up during scoring but are not persisted as separate fields in the validated signal record.

These fields are reproducible from the underlying evidence and business rules.

Example:

```json
{
  "validation_status": "validated",
  "signal_score": 0.76
}
```

### 3. Generated or interpreted fields


These fields represent account-level commercial interpretation.

Examples include:

```text
hypothesis
hypothesis_confidence
recommended_crm_action
```

The current implementation produces these using deterministic rules.

A future LLM layer may generate contextual explanations or messaging downstream of validated evidence, but it will not replace the observed source-of-truth layer.

## Validation status

The schema supports the following validation states:

```text
pending
validated
needs_review
rejected
```

The current automated pipeline primarily produces:

```text
validated
rejected
```

A signal should not participate in downstream scoring and clustering unless it passes validation.

## Minimum viable canonical signal

Before validation, a canonical signal should contain, at minimum:

```text
signal_id
company
signal_type
source_url
source_type
observed_at
evidence_text
entity
```

`published_at` may be `null` when the source does not provide a publication date.

Additional fields depend on the signal family.

For GTM hiring, downstream capability classification also requires:

```text
role_title
```

After processing, the canonical record also receives:

```text
validation_status
validation_reason
signal_score
```

`signal_score` is only added when the signal validates successfully.

## Account-level artifacts

Canonical signals are not duplicated wholesale into every downstream output.

Instead, account-level artifacts maintain lineage using signal IDs.

### Cluster

Example:

```json
{
  "company": "Granola",
  "cluster_type": "full_funnel_gtm_buildout",
  "cluster_strength": "strong",
  "signal_families": [
    "funding",
    "gtm_hiring"
  ],
  "hiring_evidence_count": 7,
  "total_evidence_count": 8,
  "supporting_signal_ids": [
    "sig_f076e552c96c",
    "sig_d34ab1120586"
  ]
}
```

### Hypothesis

Example:

```json
{
  "company": "Granola",
  "hypothesis": "Granola shows a strong full-funnel GTM hiring buildout alongside a funding signal, suggesting active commercial expansion rather than isolated recruitment.",
  "supporting_signal_ids": [
    "sig_f076e552c96c",
    "sig_d34ab1120586"
  ]
}
```

### CRM action

Example:

```json
{
  "company": "Granola",
  "recommended_crm_action": "Prioritize this account for strategic outreach focused on GTM infrastructure, segmentation, routing, forecasting, and scalable commercial operations.",
  "supporting_signal_ids": [
    "sig_f076e552c96c",
    "sig_d34ab1120586"
  ]
}
```

The intended lineage is:

```text
source URL
    ↓
canonical signal
    ↓
validated signal
    ↓
cluster
    ↓
hypothesis
    ↓
CRM action
```

## Evidence records vs signal families

The schema distinguishes between:

```text
evidence records
```

and:

```text
independent signal families
```

For the current Granola example:

```text
7 hiring records
1 funding record
```

produces:

```text
8 total evidence records
2 signal families
```

This distinction prevents repeated evidence from one family from being mistaken for independent corroboration.

## Design principle

The schema is deliberately conservative.

The engine should preserve factual evidence first and add interpretation later.

The working rule is:

```text
observe → normalize → validate → derive → interpret → act
```

instead of:

```text
scrape → guess
```

That separation is the foundation for traceable, testable GTM signal intelligence.