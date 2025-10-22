# Audience Analysis Workflow — McKinsey Dimensions

## 1. Purpose

This workflow defines the structured reasoning process for analyzing audiences after market assessment.  
It identifies **who the target segments are**, **what problems they care about**, and **which questions are worth solving and commercializing**.  
The output is organized by `segments`, ensuring that every audience group has its own set of valued business questions.
The length of output is not limited by the example
---

## 2. Workflow Overview

| Step | Dimension | Key Question | Core Output |
|------|------------|---------------|--------------|
| 1 | Segmentation | Who are the distinct customer groups? | Segment Profiles |
| 2 | Valued Questions (Pain Points) | What problems or questions matter most to each group? | Problem → Question Mapping |
| 3 | Motivation & Decision Logic | Why do they care and how do they make decisions? | Decision Pathway |
| 4 | Value Perception | How do they define value and success? | Value Map |
| 5 | Willingness to Pay | Can they pay and how much are they willing to invest? | Budget Tier |
| 6 | Relationship & Channel | How do they prefer to interact and maintain engagement? | Channel & Retention Mode |

---

## 3. Step 1 — Segmentation

### Objective

Define and classify audience segments that share similar roles, goals, or contexts.

### Reasoning Flow

1. Identify segmentation basis (industry, company size, region, behavior, role).  
2. Group audiences into clear segment archetypes.  
3. Create a concise profile for each segment.  

### Example Schema

```json
{
  "segment_name": "Data Innovators",
  "profile": {
    "industry": "Tech",
    "company_size": "mid-market",
    "region": "Global",
    "roles": ["Head of Data", "Product Analytics Lead"]
  }
}
````

---

## 4. Step 2 — Valued Questions (Pain Points)

### Objective

Identify and reframe pain points into specific, data-answerable questions that hold measurable business or monetization value.
Questions must focus on facts that can be derived directly from datasets (e.g., rankings, trends, correlations, or forecasts).

### Reasoning Flow

1. Gather 5–10 recurring data-related questions from each audience or segment.

2. Transform vague pain points into quantitative, fact-based questions that data can answer.

3. For each question, specify its business meaning, type of analytical problem, monetization potential, and decision value.

### Example Schema

```json
{
  "valued_questions": [
    {
      "question": "Which U.S. cities have the highest median home prices in 2024?",
      "mapped_pain_point": "Investors need to identify premium real-estate zones.",
      "problem_type": "Market Comparison / Pricing Insight",
      "monetization_path": ["data_api", "market_report"],
      "decision_value": "High"
    }
  ]
}
```

---

## 5. Step 3 — Motivation & Decision Logic

### Objective

Understand why the audience cares and how they decide to adopt solutions.

### Reasoning Flow

1. Identify drivers behind action (efficiency, compliance, innovation).
2. Map decision-makers and influencers.
3. Describe the decision process (awareness → trial → adoption).

### Example Schema

```json
{
  "motivation_logic": {
    "motives": ["Efficiency", "Innovation"],
    "decision_roles": ["Head of Data", "CTO"],
    "decision_journey": ["Explore", "Evaluate", "Approve", "Adopt"]
  }
}
```

---

## 6. Step 4 — Value Perception

### Objective

Capture how each audience defines “value” and what metrics matter most.

### Reasoning Flow

1. Identify the primary KPIs or outcomes they seek.
2. Rank perceived value drivers.
3. Align value definition with potential solution impact.

### Example Schema

```json
{
  "value_perception": {
    "key_drivers": ["Speed", "Reliability", "ROI"],
    "ranking": {"Speed": 1, "Reliability": 2, "ROI": 3}
  }
}
```

---

## 7. Step 5 — Willingness to Pay

### Objective

Assess financial capacity and pricing sensitivity for each segment.

### Reasoning Flow

1. Estimate budget range and procurement model.
2. Evaluate frequency of purchase or renewal.
3. Classify payment potential by tier.

### Example Schema

```json
{
  "willingness_to_pay": {
    "tier": "high",
    "budget_range_usd": "30000-50000"
  }
}
```

---

## 8. Step 6 — Relationship & Channel

### Objective

Determine preferred communication and delivery channels.

### Reasoning Flow

1. Identify preferred interaction mode (chat, dashboard, API).
2. Define service depth (self-serve, managed, partnership).
3. Evaluate retention or renewal probability.

### Example Schema

```json
{
  "relationship_channel": {
    "preferred_channel": "Insight dashboard",
    "relationship_type": "subscription-based"
  }
}
```

---

## 9. Step 7 — Segment-Level Integration

Each segment’s insights should be organized as a complete, isolated block. Each value should follow the Schema requirements.

### Example Segment Output

```json
{
  "segment_name": "Policy Analysts",
  "profile": { ... },
  "valued_questions": [ ... ],
  "motivation_logic": { ... },
  "value_perception": { ... },
  "willingness_to_pay": { ... },
  "relationship_channel": { ... }
}
```

---

## 10. Step 8 — Overall Summary

### Objective

Synthesize insights across all segments to guide focus and prioritization.

### Example Summary Schema

```json
{
  "summary": {
    "primary_focus_segment": "Data Innovators",
    "top_valued_questions": [
      "How can we automate data-to-insight workflows to reduce time-to-decision?",
      "What early indicators predict environmental risk in the next 6 months?"
    ],
    "insight": "High-paying segments show strong demand for automation and predictive analytics."
  }
}
```
