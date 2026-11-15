# CIUX Birthday Assistant — V1 to V5

**GM University · UE24CS3540 — Conversational Interfaces and UX · Academic Year 2026–27**

This educational project follows the supplied Birthday Assistant manual progressively: deterministic rules → intent/entities → dialogue state/clarification → optional LLM-assisted NLU with grounding → voice. Each `V1`…`V5` folder is independently runnable and contains its own copy of the same synthetic workbook.

## Start here (Windows + VS Code)
1. Extract this ZIP.
2. Open the extracted `CIUX_Birthday_Assistant_V1_to_V5` folder in VS Code.
3. Open one version folder (start with `V1`) as the working folder, or `cd V1` in the terminal.
4. In that folder run:
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```
5. Visit http://127.0.0.1:5000. Stop the server with Ctrl+C before starting another version.

If activation is blocked, use `..\.venv\Scripts\python.exe`? Prefer create/activate the environment separately inside each version. Alternatively run `.venv\Scripts\python.exe -m pip install -r requirements.txt` and `.venv\Scripts\python.exe app.py`.

## Version map
- **V1:** keyword/phrase rules, Pandas and Excel, response templates; no LLM.
- **V2:** intent/entity parser separated from query service.
- **V3:** session dialogue context, clarification and reset.
- **V4:** optional OpenAI semantic parser; validated structure, grounded Excel facts and rule fallback.
- **V5:** microphone input and speech output through browser APIs; same backend.

## Submission files
- `TESTING.md`: 40 test utterance plan divided into 10 direct, 10 paraphrase, 10 contextual and 10 ambiguous/unsupported cases. Fill observed result and PASS/FAIL after actually running them.
- `REFLECTION.md`: draft reflection aligned to the manual; personalize it with your real observations before submission.
- `ARCHITECTURE.md`: final architecture diagram in Mermaid.
- `PRIVACY.md`: privacy note.
- `screenshots/`: add one real successful screenshot or a short video link for each version.

## Important honesty / completion notes
This is a complete implementation starter, not evidence that you have personally run and evaluated every feature. Run each version, capture screenshots, complete actual PASS/FAIL observations and revise the reflection based on what you observe. V4 LLM functionality requires a valid API key and model access; V4 still works with rule fallback without one. V5 speech recognition is browser-dependent.

## Privacy and GitHub
The included workbook is synthetic. Never commit a real personal contacts/birthday workbook, API keys, `.env`, `.venv`, `__pycache__` or local secrets. See `.gitignore` and `PRIVACY.md`.
