# V4 — Birthday Assistant

This folder is a standalone version of the same progressive project. It uses the supplied synthetic `data/people.xlsx` workbook as the factual source.

## Windows setup
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000. Run one version at a time because all versions use port 5000.

## Learning focus
Uses an optional OpenAI model as a semantic parser only. It must return a constrained JSON structure; names and entities are validated against the spreadsheet. If the API is absent or fails, the rule parser is used.

Set credentials in PowerShell (never hard-code them):
```powershell
$env:OPENAI_API_KEY="your-key"
$env:OPENAI_MODEL="gpt-4.1-mini"
```
The API is optional; without a key, the app uses fallback NLU. API model availability and account access depend on your OpenAI account.
