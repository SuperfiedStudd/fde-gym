# ClaimOps API

`requirements-source.in` is the reviewed direct-dependency source. `requirements.txt` is the generated production lock consumed by Docker, and `requirements-dev.txt` layers test/lint tools on top.

Regenerate the lock from `apps/api/` with:

```bash
pip-compile --output-file requirements.txt --strip-extras requirements-source.in
```

Run the API from the repository root with:

```bash
uvicorn app.main:app --app-dir apps/api --reload --port 8000
```

