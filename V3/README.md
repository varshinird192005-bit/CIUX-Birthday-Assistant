# V3 — Birthday Assistant

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
Adds Flask session-based dialogue state, carries forward omitted month/relationship context, asks clarification for relationship-only singular questions, and offers Reset conversation.
