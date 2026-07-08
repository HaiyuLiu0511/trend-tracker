# Architecture — Company Research

> **Layer:** 4 — Decision Support
> **Status:** Concept frozen, implementation pending

---

## Data Inputs

- Company list (from Layer 2 — Research Terminal)
- Industry Framework (from Layer 3 — Industry Research)
- Company financial data, news, announcements

## Analysis Structure

```
Company Research
├── Industry Context (reference to Layer 3 Framework)
├── Company Fundamentals
├── Competitive Position
├── Financial Analysis
├── Valuation
├── Risk Assessment
├── Investment Recommendation (Buy/Hold/Sell + rationale)
└── Evidence Chain
```

## Cross-Layer Interface

**Input from Layer 2-3:**
- Company list (from Research Terminal)
- Industry Framework (from Industry Research)

**Output to Layer 5:**
- Company analysis results
- Investment recommendations

**Feedback to Layer 3:**
- New findings feed back to Industry Framework
