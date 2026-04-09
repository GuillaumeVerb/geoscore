# Recommendations mapping

## Goal
Turn many low-level triggered rules into a small, useful set of recommendations.

## Product rule
The top of the report should show 3 to 5 recommendations maximum.

## Why mapping is necessary
Without mapping:
- reports become noisy
- users get too many micro-fixes
- related issues create repetitive advice

With mapping:
- recommendations become clearer
- prioritization improves
- reports feel more productized

---

## Recommendation model

Each recommendation should define:
- key
- title
- explanation
- impact_scope
- priority
- effort
- expected_gain
- triggering_rule_codes

Example fields:
- key: REWRITE_HERO
- title: Rewrite the hero section
- explanation: Clarify what the product is, for whom, and why it matters in the first visible block.
- impact_scope: geo
- effort: medium
- expected_gain: higher clarity and extractability

---

## Mapping groups

### REWRITE_HERO
#### Purpose
Improve first-impression clarity.

#### Typical triggering rules
- HERO_TOO_GENERIC
- HERO_MISSING_AUDIENCE
- HERO_MISSING_PROBLEM
- HERO_MISSING_OUTCOME
- VALUE_PROP_UNCLEAR
- AUDIENCE_UNCLEAR
- OUTCOME_UNCLEAR

#### Suggested output
Rewrite the hero section to clearly state what the product is, who it is for, and what outcome it enables.

---

### CLARIFY_OFFER_POSITIONING
#### Purpose
Make the offer type and use cases explicit.

#### Triggering rules
- OFFER_TYPE_UNCLEAR
- PRODUCT_SCOPE_UNCLEAR
- USE_CASES_UNCLEAR
- TOPIC_CLARITY_WEAK
- MAIN_TOPIC_BURIED

#### Suggested output
Clarify the nature of the offer, its scope, and the main use cases so the page is easier to understand and classify.

---

### IMPROVE_HEADING_STRUCTURE
#### Purpose
Make the page easier to scan, parse, and understand.

#### Triggering rules
- H1_MISSING
- MULTIPLE_H1
- H1_TOO_GENERIC
- H2_MISSING_ON_LONG_PAGE
- HEADING_HIERARCHY_INCONSISTENT
- HEADINGS_TOO_GENERIC
- SECTIONS_NOT_SELF_EXPLANATORY

#### Suggested output
Improve the heading structure so the page is easier to scan for users and easier to parse for search systems.

---

### ADD_FAQ_OR_QA_BLOCK
#### Purpose
Improve answerability and extractability.

#### Triggering rules
- NO_FAQ_OR_QA_STRUCTURE
- USER_QUESTIONS_UNANSWERED
- KEY_DETAILS_BURIED
- ANSWERS_FOR_WHOM_MISSING
- ANSWERS_HOW_IT_WORKS_MISSING

#### Suggested output
Add a compact FAQ or Q&A block that answers the main user questions directly.

---

### ADD_EXAMPLES_AND_EVIDENCE
#### Purpose
Make the page more concrete and citation-ready.

#### Triggering rules
- NO_EXAMPLES_DETECTED
- NO_NUMBERS_OR_EVIDENCE
- TOO_FEW_PRECISE_STATEMENTS
- SEMANTIC_CITABILITY_WEAK

#### Suggested output
Add examples, numbers, and precise claims so the page becomes more concrete and easier to cite or paraphrase.

---

### ADD_TRUST_SIGNALS
#### Purpose
Strengthen entity trust and legitimacy.

#### Triggering rules
- BRAND_ENTITY_UNCLEAR
- COMPANY_IDENTITY_WEAK
- NO_CONTACT_SIGNAL
- NO_TESTIMONIAL_OR_PROOF
- NO_AUTHOR_OR_TEAM_SIGNAL_ON_RELEVANT_PAGE
- SEMANTIC_ENTITY_TRUST_WEAK

#### Suggested output
Add trust signals such as company identity, contact information, proof elements, testimonials, or team signals.

---

### STRENGTHEN_INTERNAL_LINKING
#### Purpose
Improve discoverability and path clarity.

#### Triggering rules
- INTERNAL_LINKS_TOO_FEW
- NAVIGATION_SIGNALS_WEAK
- CTA_INCOHERENT

#### Suggested output
Strengthen internal linking and make the next user path clearer across key sections and pages.

---

### FIX_TECHNICAL_SEO_BASICS
#### Purpose
Resolve foundational technical blockers.

#### Triggering rules
- TITLE_MISSING
- META_DESCRIPTION_MISSING
- CANONICAL_MISSING
- CANONICAL_INVALID
- NOINDEX_DETECTED
- ROBOTS_DIRECTIVE_UNCLEAR
- ALT_COVERAGE_VERY_LOW
- SCHEMA_MISSING

#### Suggested output
Fix the core technical signals that help search systems correctly interpret and index the page.

---

### IMPROVE_RENDER_AND_ACCESSIBILITY
#### Purpose
Address render/extraction blockers.

#### Triggering rules
- RENDER_FAILED
- CONTENT_TOO_THIN_AFTER_RENDER
- PAGE_HEAVILY_DYNAMIC
- CONF_RENDER_PARTIAL
- CONF_BLOCKED_OR_PROTECTED

#### Suggested output
Improve page rendering or accessibility so the content can be reliably read and evaluated.

---

### ENRICH_PAGE_SUBSTANCE
#### Purpose
Increase information density and usefulness.

#### Triggering rules
- CONTENT_TOO_THIN_FOR_PAGE_TYPE
- CONTENT_MODERATELY_THIN
- OVERLY_PROMOTIONAL_COPY
- REPETITIVE_COPY
- USER_INTENT_POORLY_SERVED

#### Suggested output
Enrich the page with more useful, concrete information that better matches likely user intent.

---

## Prioritization model

### Priority 1
Severe clarity, technical, or render blockers.

### Priority 2
Structural or trust weaknesses that strongly affect interpretation.

### Priority 3
Enhancements that improve citation readiness or depth.

### Priority 4+
Smaller improvements.

---

## Deduplication rules
If multiple rules trigger the same recommendation family:
- show one recommendation
- merge evidence internally
- raise priority if multiple severe issues contribute

Example:
If HERO_TOO_GENERIC + HERO_MISSING_AUDIENCE + VALUE_PROP_UNCLEAR all fire, show only REWRITE_HERO once.

---

## Effort model
- low
- medium
- high

### Examples
- Add canonical: low
- Rewrite hero section: medium
- Add trust block with proof: medium
- Rework rendering strategy: high

---

## Expected gain examples
- higher clarity
- better answerability
- stronger trust signals
- better technical interpretation
- improved citation readiness

---

## Final report recommendation composition
Recommended shape:
1. most important blocker
2. strongest clarity/structure fix
3. strongest trust/evidence fix
4. optional technical fix
5. optional enrichment fix