# Granola Signal Intelligence Engine

A GTM Engineering portfolio project that turns public company signals into validated, traceable account intelligence and deterministic CRM actions.

> **Portfolio case study:** Granola is used as a real-world SaaS example. This project is independent and is not affiliated with or endorsed by Granola.

## The problem

Revenue teams have access to more company data than ever, but more data does not automatically produce better timing.

A funding announcement, a new GTM leader, several open sales roles, or a geographic expansion may each be mildly interesting on their own. The more useful question is:

**What happens when multiple signals cluster around the same account, and what should the GTM team do about it?**

This project builds a signal intelligence pipeline designed to answer that question while preserving the evidence behind every conclusion.

## Architecture

The current engine processes two independent signal families: **GTM hiring** and **funding**.

```text
Hiring source → collect → normalize ─┐
                                    ├→ canonical signals
Funding source → normalize ─────────┘
                                           ↓
                                      merge signals
                                           ↓
                                  validate + score
                                           ↓
                                       cluster
                                           ↓
                                  account hypothesis
                                           ↓
                                  recommended CRM action
```

The full pipeline can be run from the project root with:

```bash
python -m src.pipeline.run_pipeline
```

The runner executes each stage sequentially and stops if a stage fails, preventing downstream stages from silently operating on stale or invalid output.

## What is implemented

The current version includes:

- public careers-page collection with deduplication
- signal-specific normalization for hiring and funding data
- deterministic signal IDs
- a shared canonical signal layer
- cross-signal merging
- source, schema, entity, timestamp, URL, and duplicate validation
- transparent signal scoring
- GTM hiring capability classification
- account-level signal clustering
- deterministic account hypothesis generation
- deterministic CRM action recommendation
- evidence lineage through `supporting_signal_ids`
- automated tests for core signal-engine business rules

The current Granola dataset produces:

```text
8 validated evidence records
├── 7 GTM hiring signals
└── 1 funding signal

2 independent signal families
├── funding
└── gtm_hiring
```

## Signal model

A central design principle is that **evidence volume is not the same as signal diversity**.

Seven related hiring records provide substantial evidence about one signal family: GTM hiring.

A funding event introduces a second independent signal family.

The engine therefore tracks these separately:

```json
{
  "hiring_evidence_count": 7,
  "total_evidence_count": 8,
  "signal_families": [
    "funding",
    "gtm_hiring"
  ]
}
```

This prevents additional evidence records from artificially appearing to represent independent types of evidence.

Funding can strengthen the account-level commercial hypothesis, but it does not inflate the strength or breadth of the hiring cluster.

## GTM capability model

Hiring signals are mapped into commercial capabilities rather than treated as interchangeable job openings.

The current ontology is:

| Hiring evidence | GTM capability |
|---|---|
| Sales Development Representative | `pipeline_generation` |
| Account Executive | `revenue_conversion` |
| Customer Success | `customer_success` |
| Revenue Operations | `commercial_infrastructure` |

When all four required capabilities are represented, the engine can classify the account as a:

```text
full_funnel_gtm_buildout
```

The current Granola evidence produces:

```json
{
  "commercial_infrastructure": 1,
  "pipeline_generation": 2,
  "customer_success": 1,
  "revenue_conversion": 3
}
```

This capability model is deliberately explicit. It represents a GTM interpretation encoded as inspectable business logic rather than hidden inside an opaque model.

## Validation and scoring

Raw collection is kept separate from interpretation.

Collectors observe facts. Normalization converts source-specific records into canonical signals. Validation then determines whether those records are suitable for downstream reasoning.

Current validation includes:

- required-field checks
- allowed signal types
- allowed source types
- URL validation
- timestamp validation
- entity matching
- duplicate detection
- source-confidence assignment
- freshness calculation

Validated signals receive a deterministic score based on:

```text
Signal Score =
    Source Confidence
    × Recency
    × GTM Relevance
```

Scoring components remain visible rather than being hidden behind an unexplained priority number.

The current weights and cluster thresholds are **transparent heuristics**, not a trained predictive model. They are intended to become measurable and tunable as outcome data becomes available.

## Signal clustering

Individual events are useful, but the account-level pattern is more important.

For GTM hiring, cluster strength currently considers:

1. **Capability breadth**  
   How many required GTM capabilities are represented?

2. **Hiring evidence count**  
   How much validated evidence supports the hiring pattern?

The current rules classify a cluster as `strong`, `moderate`, or `weak`.

Granola currently produces:

```json
{
  "cluster_type": "full_funnel_gtm_buildout",
  "cluster_strength": "strong",
  "signal_families": [
    "funding",
    "gtm_hiring"
  ],
  "hiring_evidence_count": 7,
  "total_evidence_count": 8
}
```

Funding is represented at the account level but does not increase hiring capability breadth or hiring cluster strength.

## From evidence to action

The pipeline maintains a deliberate separation between:

1. **Observed facts**  
   What the public source actually says.

2. **Derived fields**  
   Deterministic transformations such as capability classification, validation status, recency, score, and cluster strength.

3. **Account hypotheses**  
   Commercial interpretations supported by the validated evidence.

4. **Recommended actions**  
   The GTM response suggested by the resulting account state.

For the current Granola evidence, the engine generates the hypothesis:

> Granola shows a strong full-funnel GTM hiring buildout alongside a funding signal, suggesting active commercial expansion rather than isolated recruitment.

The resulting CRM recommendation is:

> Prioritize this account for strategic outreach focused on GTM infrastructure, segmentation, routing, forecasting, and scalable commercial operations.

Both outputs are currently produced by deterministic rules.

## Evidence lineage

Every normalized signal receives a deterministic `signal_id`.

Those IDs survive the complete pipeline:

```text
SOURCE URL
    ↓
CANONICAL SIGNAL
    ↓
VALIDATED SIGNAL
    ↓
CLUSTER
    ↓
HYPOTHESIS
    ↓
CRM ACTION
```

The cluster, hypothesis, and final action contain `supporting_signal_ids`, allowing a downstream recommendation to be traced back to the evidence that produced it.

The goal is simple:

**No recommendation without receipts.**

## Rule-based logic vs LLMs

The current decision layer is intentionally deterministic.

Rule-based logic currently owns:

- validation
- signal scoring
- GTM capability classification
- cluster strength
- signal-family detection
- hypothesis class
- recommended action class

An LLM is not used as the source of truth and is not given a raw careers page and asked to decide what matters.

A future LLM layer may operate **after** deterministic evidence processing for tasks such as:

- contextual explanation
- account research synthesis
- message personalization
- stakeholder-specific summaries
- natural-language CRM notes

This keeps repeatable and measurable decisions auditable while reserving generative models for tasks where flexible language and contextual reasoning add value.

## Testing

Core business rules are covered with automated tests using `pytest`.

Current test suite:

```text
8 passed
```

Tests currently protect invariants including:

- identical job URLs in different locations receive different signal IDs
- GTM roles map to expected commercial capabilities
- funding signals pass validation
- unrelated capabilities cannot inflate GTM capability breadth
- full capability breadth plus sufficient hiring evidence produces a strong cluster
- signal families are distinct and deduplicated
- partial capability coverage remains partial
- funding evidence cannot accidentally become a hiring capability

Run the suite with:

```bash
python -m pytest -q
```

## Repository structure

```text
granola-signal-intelligence-engine/
├── README.md
├── data/
│   ├── raw/
│   │   ├── granola_jobs.json
│   │   └── granola_funding.json
│   └── processed/
│       ├── granola_signals.json
│       ├── granola_funding_signals.json
│       ├── granola_all_signals.json
│       ├── granola_validated_signals.json
│       ├── granola_cluster.json
│       ├── granola_hypothesis.json
│       └── granola_action.json
├── src/
│   ├── collectors/
│   ├── normalization/
│   ├── validation/
│   ├── pipeline/
│   ├── clustering/
│   ├── hypothesis/
│   └── action/
├── docs/
└── tests/
    └── test_signal_engine.py
```

## Measurement

The current project demonstrates signal detection through CRM action. The next major system layer is outcome measurement.

Candidate metrics include:

- signal-to-action rate
- signal-to-meeting conversion
- signal-to-opportunity conversion
- false-positive rate
- time from signal detection to GTM action
- stage progression
- pipeline influenced
- revenue influenced

Over time, these outcomes could be used to evaluate whether the rules actually predict commercial relevance and to tune signal weights and thresholds accordingly.

The intended feedback loop is:

```text
signal
  ↓
account priority
  ↓
GTM action
  ↓
meeting
  ↓
opportunity
  ↓
revenue outcome
  ↓
rule evaluation / tuning
```

## Future signal families

The architecture is designed to support additional signal types without changing the underlying evidence model.

Potential next families include:

- leadership changes
- geographic expansion
- product expansion
- technology-stack changes

These are future extensions rather than currently implemented capabilities.

## Project status

### Current milestone: deterministic cross-signal engine

Completed:

- careers-page collector
- hiring normalization
- funding normalization
- canonical signal merge
- validation and scoring
- GTM capability classification
- cross-signal clustering
- deterministic hypothesis generation
- CRM action recommendation
- evidence lineage
- automated business-rule tests
- one-command pipeline runner

Next:

- align the canonical signal schema documentation with the implementation
- add dependency/setup documentation
- expand edge-case testing
- add a third independent signal family
- introduce LLM enrichment downstream of validated evidence
- design the outcome-measurement layer

---

Built by **Aanu Oduyemi-Rose
** as a GTM Engineering / Revenue Operations portfolio project.
