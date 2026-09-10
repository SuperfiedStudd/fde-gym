# Assessment bundles

Assessment Mode uses a deliberately small, candidate-safe bundle:

```text
assessment.json
prompt.md
resources/
  orders.csv
  context.md
```

`assessment.json` contains:

```json
{
  "id": "support-triage",
  "title": "Support queue triage",
  "duration_minutes": 45,
  "difficulty": "intermediate",
  "focus": ["data diagnosis", "product judgment"],
  "resources": [
    {
      "path": "tickets.csv",
      "label": "Ticket export",
      "description": "An anonymized snapshot of the current queue."
    }
  ]
}
```

Resource paths are filenames relative to `resources/`; nested paths, absolute paths, and `..` are rejected. Every listed resource must exist. The bundle may contain only candidate-facing material. Keep answer keys, hidden findings, rubrics, and interviewer notes outside this repository and out of coding-agent prompts.

`assessment/current/` is ignored local session state. Load a tracked example with:

```bash
python scripts/assessment/load.py assessment/examples/customer-support-triage
```
