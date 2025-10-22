## **1. Purpose**

Build a reasoning workflow that transforms **raw data or product attributes** into **strategic market insight**.
The system must **quantify market potential**, **analyze structural dynamics**, and **derive actionable investment or entry decisions**.
All outputs must integrate both **quantitative metrics** and **strategic interpretation** (cause → effect → implication).
The length of output is not limited by the example
---

## **2. Workflow Overview**

| Step | Dimension                      | Core Business Question                                        | Decision Output                                            |
| ---- | ------------------------------ | ------------------------------------------------------------- | ---------------------------------------------------------- |
| 1    | Market Size & Growth           | How big and fast is the monetizable market?                   | TAM/SAM/SOM, CAGR, revenue pools, growth sustainability    |
| 2    | Market Structure & Competition | Where does control sit and how do players capture value?      | Concentration metrics, power dynamics, entry modes         |
| 3    | Demand & Drivers               | What drives demand, how stable is it, and what limits growth? | Quantified drivers/inhibitors, elasticity, sustainability  |
| 4    | Value Chain & Ecosystem        | Where are the profit pools and leverage points?               | Profit distribution, ROI nodes, integration priorities     |
| 5    | Trends, Risks & Scenarios      | What external forces reshape the opportunity?                 | Trend map, risk matrix, scenario playbook                  |
| 6    | Strategic Synthesis            | What to do, when, and under what assumptions?                 | Market attractiveness, opportunity zone, execution roadmap |

---

## **3. Step 1 — Market Size & Growth**

**Objective:** Quantify and interpret the commercial growth logic, not just static market numbers.

**Reasoning Flow:**

1. Define **market boundary** precisely (industry × use-case × geography).
2. Calculate **TAM/SAM/SOM** and CAGR (3–7 yr horizon).
3. Evaluate **revenue concentration** (top 10 share) and **growth sustainability** (driver dependency index).
4. Distinguish **data monetization** (data→insight) vs **service monetization** (insight→solution).
5. Identify top 3 **sub-segments by ROI and barrier asymmetry**.
6. State **key assumptions** and **sensitivity factors** (pricing elasticity, regulation, adoption speed).

**Output Schema:**

```json
{
  "market_size_and_growth": {
    "period": "2022–2028",
    "tam_usd": 2300000000,
    "sam_usd": 870000000,
    "som_usd": 160000000,
    "cagr": "18%",
    "growth_sustainability": "High (driver-linked >70%)",
    "data_monetization_value": "$60M",
    "service_monetization_value": "$100M",
    "top_segments": [
      {"segment": "AI analytics SaaS", "roi_rank": 1, "barrier": "medium"},
      {"segment": "Predictive API services", "roi_rank": 2, "barrier": "low"}
    ],
    "key_assumptions": ["Regulatory climate remains stable", "Data acquisition cost growth <5%"]
  }
}
```

---

## **4. Step 2 — Market Structure & Competition**

**Objective:** Reveal who controls access to customers, capital, and data — and how rivalry shapes profitability.

**Reasoning Flow:**

1. Map **value layers** (upstream→downstream).
2. Compute **HHI/CR5** and interpret vs industry benchmarks.
3. Identify **control nodes** (who owns distribution, network effects, data).
4. Assess **entry barriers**, **switching costs**, and **platform dependency**.
5. Evaluate **strategic options**: enter via partnership, acquisition, or niche specialization.

**Output Schema:**

```json
{
  "market_structure_and_competition": {
    "hhi": 0.42,
    "control_nodes": ["Booking platforms", "API aggregators"],
    "major_players": [
      {"name": "Company A", "share": 35, "model": "Data marketplace"},
      {"name": "Company B", "share": 22, "model": "Vertical SaaS"}
    ],
    "entry_barriers": ["Regulatory license", "Data network effects"],
    "competitive_pressure": "High rivalry; buyer power medium; supplier power low",
    "recommended_entry_mode": "Strategic partnership with midstream platform"
  }
}
```

---

## **5. Step 3 — Demand & Drivers**

**Objective:** Quantify what sustains demand, when, and with what magnitude; clarify elasticity and risk of reversal.

**Reasoning Flow:**

1. Identify 3–5 key growth drivers and quantify effect (+/– %).
2. Add **time horizon** and **probability of persistence**.
3. Quantify inhibitors with measurable drag factors.
4. Rank **net demand strength = Σ(impact×probability) – inhibitors**.
5. Define **dominant driver** and its dependency risks.

**Output Schema:**

```json
{
  "demand_and_drivers": {
    "drivers": [
      {"driver": "AI adoption", "impact": 0.9, "probability": 0.8, "net_effect": "+25%", "horizon": "short"},
      {"driver": "ESG compliance", "impact": 0.6, "probability": 0.7, "net_effect": "+12%", "horizon": "mid"}
    ],
    "inhibitors": [
      {"factor": "High acquisition cost", "impact": -0.4},
      {"factor": "Policy uncertainty", "impact": -0.3}
    ],
    "dominant_driver": "AI-driven automation (high persistence)"
  }
}
```

---

## **6. Step 4 — Value Chain & Ecosystem**

**Objective:** Locate the highest-margin nodes and integration leverage across the chain.

**Reasoning Flow:**

1. Map **profit distribution** (EBITDA basis).
2. Evaluate **margin drivers** (scale, data, IP, switching costs).
3. Highlight **synergy opportunities** via vertical/horizontal integration.
4. Score each opportunity = (ROI × barrier asymmetry × strategic fit).

**Output Schema:**

```json
{
  "value_chain_and_ecosystem": {
    "profit_distribution": {"upstream": "20%", "midstream": "50%", "downstream": "30%"},
    "margin_drivers": ["Data ownership", "API lock-in"],
    "integration_opportunities": [
      {"target": "Midstream API aggregators", "roi_score": 8.7, "priority": "high"},
      {"target": "Downstream SaaS resellers", "roi_score": 6.3, "priority": "medium"}
    ]
  }
}
```

---

## **7. Step 5 — Trends, Risks & Scenarios**

**Objective:** Convert uncertainty into strategic readiness.

**Reasoning Flow:**

1. Identify top trends and assign **quantified impact index**.
2. Develop **risk matrix** (Probability × Impact).
3. Simulate **best/base/worst-case scenarios** for 3-year horizon.
4. Output **response priorities** (Prevent / Adapt / Exploit).

**Output Schema:**

```json
{
  "trends_and_risks": {
    "emerging_trends": [
      {"trend": "AI regulation tightening", "impact_index": 0.8},
      {"trend": "Open-data economy", "impact_index": 0.6}
    ],
    "risk_matrix": [
      {"event": "Regulatory delay", "prob": 0.7, "impact": 0.8, "type": "external"},
      {"event": "Price compression", "prob": 0.5, "impact": 0.6, "type": "market"}
    ],
    "scenarios": {
      "best_case": "Rapid AI adoption → +30% market expansion",
      "base_case": "Steady 12% CAGR, moderate risk",
      "worst_case": "Regulatory freeze → –10% growth"
    },
    "response_plan": ["Invest in compliance tech", "Diversify into B2B API services"]
  }
}
```

---

## **8. Step 6 — Strategic Synthesis**

**Objective:** Translate findings into a decision-ready strategy statement.

**Reasoning Flow:**

1. Assess **market attractiveness** = (Growth × Profitability × Risk).
2. Define **opportunity zone** (segment × position × timing).
3. Outline **execution roadmap** (short/mid/long term).
4. Include **key assumptions**, **trigger indicators**, and **decision checkpoints**.

**Output Schema:**

```json
{
  "strategic_summary": {
    "market_attractiveness": "High-growth, medium-risk, strong midstream margin",
    "opportunity_zone": "Midstream API intelligence & compliance automation",
    "strategy_timeline": {
      "short_term": "Build compliance data connectors",
      "mid_term": "Monetize predictive analytics API",
      "long_term": "Form ecosystem alliances for multi-dataset integration"
    },
    "decision_triggers": ["Regulatory clarity index > 0.7", "API adoption > 60% of target TAM"]
  }
}
```

## **9. Step 8 — Overall Summary**

**Objective**: Provide a one-screen executive summary integrating quantitative scale, structural logic, and strategic recommendation.

### Example Summary Schema

```json
{
  "summary": {
    "headline": "A $2.3B high-growth data service market with dominant midstream profit pools and rising AI-driven monetization potential.",
    "core_insight": "Value capture is shifting from ownership to integration — firms controlling midstream APIs and compliance automation will dominate ROI.",
    "risk_outlook": "Regulatory uncertainty is the single largest downside risk; diversification into B2B and compliance tech mitigates exposure.",
    "strategic_call": "Prioritize entry via partnership and data integration; short-term focus on compliance connectors, long-term on predictive analytics ecosystems."
  }
}
```
