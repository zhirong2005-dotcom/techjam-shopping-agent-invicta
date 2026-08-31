# Conversational E-Commerce Search Agent

A lightweight, fully offline conversational product retrieval agent developed for the **TechJam Conversational E-Commerce Search Challenge**.

The system is designed to identify evolving shopping intent across multi-turn conversations, maintain structured customer preference state, retrieve candidates from a frozen 50,000-product catalog, and rank the most relevant products as early and accurately as possible.

On the competition's **200-session public development set**, the agent achieved:

| Metric          |     Result |
| --------------- | ---------: |
| HitRate@10      | **1.0000** |
| MRR             | **0.9700** |
| MTTC            | **1.7900** |
| Efficiency      | **0.9210** |
| Technical Score | **0.9752** |

> **Note:** These results are from the public development set. Performance on the organizer's private evaluation set may differ.

---

## Project Overview

Conversational product search is different from traditional one-shot search.

A customer may begin with a vague request, gradually reveal preferences, change their mind halfway through a conversation, or indicate that they have no preference for a requested attribute.

This project addresses that problem with a stateful retrieval agent that:

* distinguishes between exploratory and higher-confidence shopping behavior;
* extracts product constraints from conversation turns;
* remembers previously disclosed preferences;
* handles intent changes without discarding still-valid constraints;
* retrieves candidates through multiple search routes;
* reranks products according to disclosed requirements;
* determines when additional clarification is useful; and
* returns ranked product recommendations through the required backend API.

The objective is not only to retrieve the correct product within the top 10, but to find it **as early and as highly ranked as possible**.

---

## How It Works

The agent uses a multi-stage conversational retrieval pipeline.

### 1. Intent and Conversation-State Analysis

Incoming messages are analyzed to determine the current interaction state.

The agent handles the competition's main conversational behaviors:

* **Buying** — the customer provides an important requirement early.
* **Browsing** — the customer begins with limited information and is still exploring.
* **Intent Override** — an earlier preference is replaced later in the conversation.
* **Boundary** — the customer may indicate that they have no preference for a requested attribute.

This routing influences both retrieval and clarification behavior.

### 2. Constraint Extraction

The agent extracts useful shopping signals from customer messages, including:

* material;
* color;
* size;
* style;
* budget;
* use case; and
* catalog-specific feature constraints.

It also preserves multi-word literal constraints when exact wording provides useful product evidence.

### 3. Adaptive Session Memory

Each conversation maintains isolated runtime state.

The session memory tracks information such as:

* active constraints;
* ordered disclosed preferences;
* previously requested attributes;
* attributes for which the customer has no additional preference;
* previous recommendations;
* intent overrides; and
* permitted aggregate user-profile preference signals.

This allows later turns to build on earlier information instead of treating every message as an independent query.

### 4. Candidate Retrieval

The catalog is indexed at initialization using **SQLite FTS5**.

The agent combines several lightweight retrieval routes, including:

* category retrieval;
* literal phrase retrieval;
* attribute-based retrieval;
* combined constraint queries;
* ordered-constraint indexes; and
* exact disclosure/signature indexes.

Candidate results from different retrieval paths can then be combined before reranking.

### 5. Constraint-Aware Reranking

Candidate products are scored against the information the customer has actually disclosed.

The reranker considers signals such as:

* exact constraint matches;
* literal phrase matches;
* attribute coverage;
* category agreement;
* budget proximity;
* bounded profile overlap; and
* lightweight rating/review priors for resolving otherwise similar candidates.

Constraint satisfaction is intentionally given substantially more importance than generic popularity.

### 6. Clarify or Recommend

The agent dynamically determines whether to:

* return an early high-confidence recommendation; or
* request another useful attribute from the customer.

This helps balance early conversion against ranking confidence.

---

## Architecture

```text
Customer Message
       |
       v
Intent / State Analysis
       |
       v
Constraint Extraction
       |
       v
Adaptive Session Memory
       |
       v
Retrieval Routing
       |
       v
SQLite FTS5 Candidate Generation
       |
       v
Constraint-Aware Reranking
       |
       v
Clarify or Recommend
       |
       v
Ranked Product Recommendations
```

The entire runtime pipeline executes locally.

No external vector database, hosted model, or network API is required.

---

## Scope Alignment

The implementation is designed around the permitted hackathon scope.

### Intent Detection and Routing

The system uses conversation-state and message-pattern analysis to route Buying, Browsing, Intent Override, and Boundary behavior.

### Heterogeneous Retrieval

Multiple FTS5 and structured retrieval routes are used with route-specific weighting, result truncation, and stateful handling of previously recommended products.

### Adaptive Memory

Each session maintains runtime state for disclosed constraints, asked attributes, exhausted preferences, recommendation history, and intent replacement.

### Local Ranking

Ranking and decision logic are implemented locally without full-parameter model training or external LLM inference.

### Lightweight In-Memory Search

The search index uses in-memory SQLite FTS5 rather than an external industrial vector database.

### Text-Only Processing

The solution operates entirely on text conversations and structured product metadata.

There is no multimodal pipeline or required UI.

The implementation also assumes the challenge's clean-input conditions, treats the catalog as read-only, and does not inject synthetic product identifiers.

---

## Repository Structure

```text
.
├── agent.py
├── README.md
├── REPORT.md
├── DEMO_SESSION.md
├── requirements.txt
└── run_public_eval.py
```

| File                 | Purpose                                                         |
| -------------------- | --------------------------------------------------------------- |
| `agent.py`           | Main conversational retrieval agent exporting `Agent`           |
| `README.md`          | Project overview, setup, results, and reproduction instructions |
| `REPORT.md`          | Detailed methodology, evaluation, cost, and limitations         |
| `DEMO_SESSION.md`    | Example multi-turn conversation                                 |
| `requirements.txt`   | Dependency declaration                                          |
| `run_public_eval.py` | Helper for reproducing public evaluation results                |

---

## Tools and Technologies

### Runtime

* Python
* SQLite
* SQLite FTS5
* Python standard library

### Core Python Modules

The final agent primarily uses:

* `sqlite3`
* `json`
* `re`
* `math`
* `collections`
* `pathlib`

### External APIs

**None are required at runtime.**

The submitted agent:

* does not call an external LLM;
* does not use an embedding API;
* does not require an API key;
* does not require network access; and
* does not depend on an external database service.

All inference, retrieval, state management, and ranking are performed locally.

### Development Tools

* Visual Studio Code
* Git and GitHub
* ChatGPT for Debugging


---

## Dataset

The project uses the competition-provided frozen **50,000-product `Clothing_Shoes_and_Jewelry` catalog**, derived from **Amazon Reviews 2023**.

The product catalog contains structured fields such as:

* product identifier (`parent_asin`);
* title;
* features;
* description;
* price;
* categories;
* details;
* average rating;
* rating count; and
* store.

Development evaluation was performed using the competition's **200-session public development set**.

The competition dataset itself is **not redistributed through this repository**.

Place the organizer-provided catalog at:

```text
data/catalog.jsonl
```

or provide its path explicitly when constructing the agent.

---

## Runtime Requirements

* CPython 3.10 or newer
* Verified locally on CPython 3.13.5
* Python standard library only
* `sqlite3` compiled with FTS5 support
* Local access to the organizer-provided `catalog.jsonl`
* No network connection required
* No API credentials required
* No environment variables required

The default catalog path is:

```text
data/catalog.jsonl
```

A custom catalog location can also be supplied:

```python
from agent import Agent

agent = Agent("/absolute/path/to/catalog.jsonl")
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/zhirong2005-dotcom/techjam-shopping-agent-invicta
cd techjam-shopping-agent-invicta
```

Optionally create a virtual environment:

```bash
python -m venv .venv
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install the dependency manifest:

```bash
python -m pip install -r requirements.txt
```

The current implementation has no required third-party Python dependencies.

---

## Verify Your Environment

Check that the agent compiles:

```bash
python -m py_compile agent.py
```

Verify that your Python installation supports SQLite FTS5:

```bash
python -c "import sqlite3; c=sqlite3.connect(':memory:'); c.execute('CREATE VIRTUAL TABLE t USING fts5(x)'); print('SQLite FTS5: OK')"
```

Expected output:

```text
SQLite FTS5: OK
```

---

## Agent Interface

`agent.py` exports the required `Agent` class:

```python
class Agent:
    def reset(self, session_id: str, user_profile: dict) -> None:
        ...

    def respond(
        self,
        session_id: str,
        user_message: str,
        turn: int,
        top_k: int,
    ) -> dict:
        ...
```

A response follows the required structure:

```python
{
    "message": "Anything else that matters?",
    "ask_attribute": "other",
    "recommendations": [
        {"parent_asin": "B000..."}
    ],
    "usage": {
        "prompt_tokens": 12,
        "completion_tokens": 4
    }
}
```

Recommendations are returned in ranked order.

---

## Reproducing the Public Evaluation

The competition-provided `local_evaluator.py` expects the agent at `starter.agent`.

The included `run_public_eval.py` helper temporarily stages the repository's `agent.py` in the expected structure without modifying the organizer's evaluator.

Run:

```bash
python run_public_eval.py \
  --evaluator /path/to/local_evaluator.py \
  --catalog /path/to/catalog.jsonl \
  --dataset /path/to/public_set.jsonl \
  --output public_results.json
```

On Windows PowerShell, the same command can be entered on one line:

```powershell
python run_public_eval.py --evaluator C:\path\to\local_evaluator.py --catalog C:\path\to\catalog.jsonl --dataset C:\path\to\public_set.jsonl --output public_results.json
```

---

## Public Development Results

The most recent clean evaluation on the supplied **200-session public development set** produced:

| Metric                      |       Result |
| --------------------------- | -----------: |
| HitRate@10                  | **1.000000** |
| MRR                         | **0.970000** |
| MTTC                        | **1.790000** |
| Efficiency                  | **0.921000** |
| Recommended Technical Score | **0.975200** |

### Results by Scenario

| Scenario        |   HitRate@10 |          MRR |         MTTC |
| --------------- | -----------: | -----------: | -----------: |
| Buying          | **1.000000** | **0.987500** | **1.337500** |
| Browsing        | **1.000000** | **0.937500** | **1.487500** |
| Intent Override | **1.000000** | **1.000000** | **3.600000** |
| Boundary        | **1.000000** | **1.000000** | **2.400000** |

These numbers represent **public-development performance only**.

The organizer's private evaluation contains unseen sessions, so private-set performance may differ.

---

## Efficiency and Cost

The final runtime does not use an external LLM or paid API.

Therefore:

* **External inference API cost:** $0.00
* **API credentials:** None
* **Network dependency:** None
* **External model inference:** None

The primary runtime work consists of:

1. loading the static catalog;
2. constructing the in-memory FTS5 and structured indexes;
3. performing lightweight retrieval queries; and
4. applying deterministic local reranking.

---

## Catalog Behavior

During initialization, the agent reads the catalog and constructs:

* an in-memory SQLite FTS5 index;
* normalized product metadata maps;
* category indexes;
* ordered-constraint indexes;
* exact disclosure/signature indexes; and
* a bounded query cache.

The source catalog is treated as **read-only**.

The agent does not modify product records or inject synthetic ASINs.

---

## Example Conversation

A complete example is available in [`DEMO_SESSION.md`](DEMO_SESSION.md).

At a high level, an interaction follows this pattern:

```text
Customer
"I'm looking for a product, but I'm still exploring."

        ↓

Agent
Returns initial candidates and asks for additional useful information.

        ↓

Customer
Reveals one or more product constraints.

        ↓

Agent
Updates session state, reruns retrieval and reranking,
and returns a more targeted recommendation.
```

This demonstrates how the agent progressively compresses a vague shopping request into a precise ranked result.

---

## Limitations

The reported performance was obtained on the competition's **200-session public development set**.

The organizer's private evaluation contains unseen sessions, so public-set performance does not guarantee equivalent private-set performance.

Additional limitations include:

* The system assumes clean text inputs according to the hackathon's allowed assumptions.
* It does not currently implement spelling correction or noisy-input normalization.
* Retrieval operates against a static product catalog.
* The system is text-only and does not process product images.
* Some conversational strategies were optimized using the public simulator and may be less effective under substantially different dialogue patterns.
* The system relies on SQLite FTS5 availability in the runtime Python environment.
* Ranking is deterministic and locally engineered rather than learned from large-scale conversational relevance data.

The primary technical uncertainty is therefore **generalization to unseen private conversations**, rather than public-set retrieval recall.

---

## What We Would Improve With More Time

Future improvements could include:

* more general intent classification with less dependence on known conversational patterns;
* improved confidence estimation for deciding when to recommend versus clarify;
* semantic retrieval or lightweight learned reranking while preserving offline execution;
* stronger robustness to paraphrased and less structured customer language;
* more systematic personalization using permitted aggregate profile information;
* additional ablation testing to measure the contribution of each retrieval and ranking component; and
* broader evaluation against unseen conversation styles.

The goal would be to preserve the current system's low latency and zero external inference cost while improving robustness and private-set generalization.

---

## Troubleshooting

### `sqlite3.OperationalError: no such module: fts5`

Use a Python/SQLite build with FTS5 enabled.

Run:

```bash
python -c "import sqlite3; c=sqlite3.connect(':memory:'); c.execute('CREATE VIRTUAL TABLE t USING fts5(x)'); print('SQLite FTS5: OK')"
```

before evaluation.

### `FileNotFoundError` for `data/catalog.jsonl`

Place the organizer-provided catalog at:

```text
data/catalog.jsonl
```

or instantiate `Agent` using the actual catalog path.

### Evaluator cannot import `starter.agent`

Use:

```text
run_public_eval.py
```

The helper stages the root `agent.py` in the layout expected by the supplied public evaluator.

---

## Team Contributions

Our team worked together in designed and implemented the conversational state management and retrieval architecture
Zhi Rong worked on the constraint extraction, ranking logic, evaluation workflow
Wei Da focused on optimization and testing to make sure that there was effective work done 
Yu Fei worked on the project documentation

---

## Acknowledgements

This project was developed for the **TechJam Conversational E-Commerce Search Challenge**.

The competition catalog is derived from the **Amazon Reviews 2023** dataset from McAuley Lab at UCSD, using the `Clothing_Shoes_and_Jewelry` category.

The underlying dataset remains subject to its applicable terms and attribution requirements.

---

## License

No license is currently specified for this repository.

The competition dataset is not included in this repository and remains subject to its original terms and the competition's data-use requirements.
