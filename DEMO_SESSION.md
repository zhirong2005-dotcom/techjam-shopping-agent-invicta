# Demonstrated Multi-Turn Session

## Purpose

This transcript is a reproducible example from public development sample `public_0007`. It demonstrates the Browsing route, a structured clarification, and a rank-1 conversion on the second turn.

The evaluator target is shown here only for reporting. It is not provided to the agent during the conversation.

## Session metadata

| Field | Value |
|---|---|
| Scenario | Browsing |
| Coarse category | Tees & Blouses Tunics |
| Target `parent_asin` | `B08PF98BV4` |
| Target title | RITERA Plus Size Tops for Women Off the Shoulder Cold Shoulder Tops Short Sleeve Shirts Summer Blouses Sexy Tunics Tee XL-5XL |
| Final hit turn | 2 |
| Final target rank | 1 |

Aggregate profile supplied at `reset()`:

```json
{
  "average_prior_rating": 5.0,
  "preference_tags": ["material", "fit"],
  "purchase_frequency": "3-4 prior purchases",
  "rating_style": "usually positive",
  "summary": "Prior purchases emphasize material, fit; ratings are usually positive."
}
```

## Turn 1

**Customer**

> I'm looking for Tees & Blouses Tunics, but I'm still exploring.

**Agent structured response**

```json
{
  "message": "Anything else that matters?",
  "ask_attribute": "other",
  "recommendations": [
    {"parent_asin": "B0B4BRW7JT"},
    {"parent_asin": "B07TVDN6JH"}
  ],
  "usage": {
    "prompt_tokens": 12,
    "completion_tokens": 4
  }
}
```

**Evaluation outcome:** no target hit. The agent asks `other`, allowing the customer policy to reveal up to two remaining constraints.

## Turn 2

**Customer**

> For that, what matters is: polyester; 75% Polyester, 20% Rayon, 5% Spandex.

**Agent structured response**

```json
{
  "message": "Anything else that matters?",
  "ask_attribute": "other",
  "recommendations": [
    {"parent_asin": "B08PF98BV4"}
  ],
  "usage": {
    "prompt_tokens": 12,
    "completion_tokens": 4
  }
}
```

**Evaluation outcome:** the target is returned at rank 1 on turn 2, ending the session successfully.

## What the example demonstrates

- The vague opening is routed through the exact coarse-category prior.
- The agent makes bounded early recommendations instead of returning ten weak guesses.
- `ask_attribute: "other"` elicits two informative constraints in one customer reply.
- The material disclosures are recovered as ordered constraints.
- Exact ordered-prefix retrieval places the target first on the next turn.
