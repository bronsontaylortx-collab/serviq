# ServIQ V0.5 — Runnable Web App

This is the first end-to-end local web prototype.

## Run
1. Install Python 3.
2. In this folder run: `pip install -r requirements.txt`
3. Run: `python app.py`
4. Open `http://127.0.0.1:5000`

## What works
- Paste/edit a synthetic transcript
- Select the initial mortgage-servicing scorecard
- Analyze the call
- See server-calculated QA score
- See per-question PASS/FAIL, confidence, human-review routing, and critical-failure status

## Current limitation
V0.5 intentionally uses local deterministic heuristics so it runs without an API key. The next deployment step replaces `evaluate()` with the provider-neutral AI adapter and structured model output from V0.4.

Use synthetic or explicitly authorized data only.
