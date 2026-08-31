# Technical Report

## 1. Executive summary

This submission is a deterministic, fully offline, multi-turn product-retrieval agent for the TechJam Conversational E-Commerce Search Challenge. It combines an in-memory SQLite FTS5 index with exact category, disclosure, ordered-constraint, and intent-signature indexes. A stateful reranker uses only catalog-visible fields, the customer's disclosed constraints, and the permitted aggregate user profile.

No LLM, embedding model, external service, private labels, or network access is used during official scoring. The resulting system has zero model cost and can run under a network-disabled evaluator.

On the supplied 200-session public development set, the final verified version achieved HitRate@10 of 1.0000, MRR of 0.9700, MTTC of 1.7900, and a recommended technical score of 0.9752. These results are development measurements and do not guarantee the private-set score.

## 2. Scope compliance and design choices

The implementation follows the supplied scope boundaries.

### In-scope: intent detection and Buying/Browsing routing

The opening message is routed into operational Buying, Vague/Browsing, or Intent Override behavior, with Boundary-specific handling when a customer explicitly has no preference. The routing logic is intentionally lightweight and deterministic because the inputs are specified as pre-cleaned text.

### In-scope: heterogeneous retrieval routing

Candidate generation combines multiple local retrieval routes, including phrase retrieval, category-and-attribute retrieval, broad OR retrieval, and exact indexed disclosure routes. Route-specific weights and turn-specific recommendation truncation change the path according to the amount and quality of evidence available.

The agent also retains prior recommendations and, after an explicit no-preference response, explores a deterministic deeper segment of the ranked pool rather than repeating the same neighborhood.

### In-scope: runtime-adaptive memory

Each session stores only retrieval-relevant state: disclosed category/details, classified attributes, literal phrases, active ordered constraints, override state, asked/exhausted attributes, previously recommended IDs, and safe aggregate profile terms. This gives the reranker a compact, evolving context without retaining private or hidden evaluation data.

### In-scope: local ranking / decision-path compression

The ranking stage is implemented as a deterministic scoring function over candidate products. Strong evidence such as exact disclosures, literal phrases, complete attribute satisfaction, and category agreement dominates weaker popularity and profile signals. No full-parameter fine-tuning is performed.

### Out of scope exclusions respected

- No UI/UX component is required.
- No foundational LLM is trained or fully fine-tuned.
- No heavy external vector database is deployed.
- No multimodal information is used.
- The catalog remains read-only.
- No synthetic product identifiers are injected.
- The agent does not intentionally exceed the 10-turn session limit.

## 3. Agent architecture

### 3.1 Catalog indexing

At construction time, the agent reads the frozen JSONL catalog and builds an in-memory SQLite FTS5 table over:

- title;
- categories;
- features;
- details;
- store; and
- description.

It also creates Python-side structures for:

- parsed price, average rating, and rating count;
- normalized title and category text;
- category-to-product membership;
- product material/color signatures;
- normalized product constraint sequences derived solely from catalog fields;
- ordered constraint-prefix lookup;
- opening-intent and disclosure-payload lookup; and
- category-specific constraint vocabularies.

This design pays a one-time startup cost so later turns can use exact dictionary lookups, cached FTS queries, or small reranking pools.

### 3.2 Conversation state

Each session stores only information needed for retrieval and dialogue control:

- category and detail terms;
- classified material, color, size, style, use-case, and budget values;
- literal disclosure phrases and payloads;
- ordered active constraints;
- the replaceable preference used by Intent Override sessions;
- asked and exhausted attributes;
- previously recommended product IDs;
- Boundary deferral state; and
- safe aggregate profile terms.

The agent is not provided direct customer identifiers, raw purchase history, private reviews, hidden intent cards, or ground-truth labels, and it does not reference any such fields.

### 3.3 Scenario routing

The opening message is classified into one of three operational routes:

1. **Buying:** a hard constraint is disclosed immediately.
2. **Vague/Browsing:** only a coarse category is available initially.
3. **Intent:** an initial preference may later be replaced.

Boundary behavior is detected from an explicit lack-of-preference reply. Intent Override behavior is handled surgically: the replaceable constraint is removed, affected attribute values are cleared, unaffected constraints remain active, and pre-override recommendations can be reconsidered after the replacement arrives.

### 3.4 Candidate generation

The broad-recall route issues several FTS5 searches and combines them using reciprocal-rank-style fusion:

- exact phrase queries for literal disclosures;
- phrase queries for short informative clauses;
- category AND queries;
- category-plus-attribute queries;
- category OR queries; and
- combined detail and attribute queries.

Exact routes bypass broad FTS search when disclosed information maps directly to precomputed indexes:

- exact category candidates for vague openings;
- ordered constraint-prefix candidates for stable Buying/Browsing disclosures; and
- signature intersections for post-override intent evidence.

### 3.5 Reranking

The reranker emphasizes disclosed requirements rather than incidental corpus frequency. Main signals include:

- exact payload and ordered-constraint agreement;
- literal multi-word phrase matches;
- classified attribute matches;
- complete satisfaction of all disclosed attribute values;
- exact category membership and category-term overlap;
- bounded detail/profile overlap;
- price proximity when a budget is present; and
- small popularity and rating-quality tie-breaks.

When several products share the same exact ordered prefix, the tie-break uses transformed review strength and metadata completeness rather than letting raw review count dominate. For vague category openings, popularity remains the principal prior while small title/profile signals resolve close candidates.

### 3.6 Clarification strategy

The agent asks the structured `other` attribute first because a customer can provide multiple remaining constraints in one reply. It then falls back through material, color, budget, size, style, use case, feature, and brand while avoiding attributes already asked or explicitly exhausted.

Recommendation list length is deliberately capped by route and turn. Early high-confidence guesses improve MTTC, while narrower lists preserve stronger reciprocal-rank performance. Boundary refusal still permits an unseen category probe, after which later constraint-based ranking remains available.

### 3.7 Reliability behavior

`respond()` catches unexpected runtime errors and returns a valid schema-compatible response rather than terminating the entire session. FTS query failures return an empty candidate list and allow fallback behavior. A bounded ordered dictionary limits FTS cache growth.

## 4. Model choice and external services

### Model

No learned model is used. The system is a deterministic retrieval-and-reranking program based on:

- SQLite FTS5/BM25;
- regular-expression and token normalization;
- exact and prefix indexes;
- hand-designed scoring; and
- finite conversation state.

### Network and credentials

- Network required: **No**
- API credentials required: **No**
- External service required: **No**
- Offline fallback: **Not applicable; offline operation is the primary mode**

### Estimated model cost

**USD 0.00** for the full public evaluation and for official execution, because no language model or paid external service is invoked.

## 5. Public development results

The final agent was evaluated from a clean staged package against the supplied catalog and 200 public sessions.

### Overall

| Metric | Result |
|---|---:|
| Sample count | 200 |
| HitRate@10 | 1.000000 |
| MRR | 0.970000 |
| MTTC | 1.790000 |
| Efficiency | 0.921000 |
| Recommended technical score | 0.975200 |

### By scenario

| Scenario | Sessions | HitRate@10 | MRR | MTTC |
|---|---:|---:|---:|---:|
| Boundary | 10 | 1.000000 | 1.000000 | 2.400000 |
| Browsing | 80 | 1.000000 | 0.937500 | 1.487500 |
| Buying | 80 | 1.000000 | 0.987500 | 1.337500 |
| Intent Override | 30 | 1.000000 | 1.000000 | 3.600000 |

Intent Override sessions cannot validly convert until the replacement intent is sent on turn 3 or 4, so their MTTC reflects a protocol-imposed delay rather than a retrieval miss.

## 6. Latency and token disclosure

Measurements were taken in the supplied container using CPython 3.13.5 and the 200 public sessions. Official hardware and timings may differ.

### Latency

| Measurement | Result |
|---|---:|
| Agent initialization and index build | 17.215 s |
| Public evaluation after initialization | 15.453 s |
| `respond()` calls | 358 |
| Mean `respond()` latency | 42.948 ms |
| Median `respond()` latency | 0.509 ms |
| 95th-percentile `respond()` latency | 228.843 ms |
| Maximum observed `respond()` latency | 727.590 ms |
| Mean `reset()` latency | 0.026 ms |

The mean is higher than the median because the run mixes very fast exact-index/cache turns with slower cold FTS search turns.

### Reported token usage

| Category | Tokens |
|---|---:|
| Prompt | 4,738 |
| Completion | 1,380 |
| Total | 6,118 |

These are deterministic word-token counts reported for feasibility. They are **not billable LLM tokens**, because no LLM is called.

## 7. Limitations and private-set risks

1. **Template sensitivity.** Exact disclosure and ordered-prefix routes benefit from structured simulator wording. Novel paraphrases can fall back to broader FTS retrieval and may rank less precisely.
2. **Public-set tuning risk.** Turn caps and tie-break weights were validated on 200 public sessions. They may not be optimal on the unseen 800-session private set.
3. **English-focused parsing.** Attribute classification and phrase handling use English tokenization and regular expressions.
4. **FTS5 dependency.** The runtime's SQLite build must include FTS5.
5. **Startup cost.** The complete catalog index takes approximately 17 seconds to build in the measured environment.
6. **Memory footprint.** The implementation keeps normalized product text and several indexes in memory; memory usage was not formally profiled.
7. **No semantic encoder.** The agent does not use embeddings or a learned paraphrase model, limiting robustness to highly novel language.
8. **Catalog-specific priors.** Popularity, rating, price completeness, and title/category tie-breaks may behave differently under a shifted catalog distribution.

## 8. Reproducibility

Runtime requirement:

```text
CPython 3.10+ with sqlite3 FTS5 support
```

There are no third-party dependencies. From this submission directory, run:

```bash
python -m pip install -r requirements.txt
python -m py_compile agent.py
python run_public_eval.py \
  --evaluator /path/to/local_evaluator.py \
  --catalog /path/to/catalog.jsonl \
  --dataset /path/to/public_set.jsonl \
  --output public_results.json
```

No environment variables are required.

## 9. Demonstrated session

A complete multi-turn example is provided in `DEMO_SESSION.md`. It demonstrates a valid customer clarification flow with ranked recommendations, including a target at rank 1 after additional constraints are disclosed.

## 10. Team contributions

The registered team jointly completed problem analysis, intent routing, retrieval architecture, conversation-state design, ranking implementation, local evaluation, regression checking, and submission documentation. Individual legal names and any more granular role attribution should match the team's official hackathon registration record.

## 11. Data use and privacy

The agent uses only participant-visible catalog fields and the supplied safe aggregate user profile. It does not access direct user identifiers, timestamps, free-text reviews, private intent cards, private evaluation labels, account credentials, or external customer data. The catalog is read-only and is not modified.
