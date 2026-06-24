# Interview story bank

Copy this template after every completed mission. Keep the first version factual; polish the narrative only after the evidence is recorded.

---

## Mission: `<mission-id>` — `<title>`

### Problem

What was failing, who or what was affected, and what signal exposed it?

### Root cause

What specific code, configuration, data, concurrency, or system interaction caused the behavior? What evidence ruled out alternatives?

### Fix

What did you change? Name the invariant or contract restored.

### Tests added

Which unit, integration, concurrency, load, contract, or operational checks prove the repair?

### Tradeoffs

What did you optimize for? What complexity, latency, throughput, cost, or compatibility did you accept?

### Production risk

How would you deploy, monitor, roll back, or limit blast radius? What residual risk remains?

### What I would say in an interview

Write a 90-second version using context → investigation → decision → result → learning. Then list the technical details you can expand if asked.

### Follow-up questions I should be ready for

- Why this solution instead of the strongest alternative?
- What changes at 10× load or with multiple regions?
- What did the tests not prove?
- Which signal would detect recurrence fastest?

