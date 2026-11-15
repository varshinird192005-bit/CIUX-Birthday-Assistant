# Version 1 — Deterministic Rule-Based Birthday Assistant

**Goal:** make the supplied spreadsheet conversational using explicit keyword and phrase rules.

## Run on Windows (PowerShell)
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000. If PowerShell blocks activation, use `.venv\Scripts\python.exe` to install/run.

## Try
- What are the upcoming birthdays?
- How many birthdays are there next month?
- Is there any birthday tomorrow?
- When is my wife's birthday?
- Any nephew birthdays in September?
- When is Rahul Patil's birthday?

V1 intentionally uses rules only. It does not use an LLM. Inspect the Rule Trace and record paraphrases it cannot understand. Dataset facts come from `data/people.xlsx`.
