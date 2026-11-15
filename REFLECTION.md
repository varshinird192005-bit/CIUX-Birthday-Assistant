# Two-page learning reflection — draft to personalize

> **Important:** This is a structured draft based on the manual's intended learning progression. Replace or edit statements so they accurately describe what you personally observed while running the project. Do not claim a test passed unless you ran it.

## Reflection on the evolution from V1 to V5

**Version 1 — Deterministic rules.** V1 connects a browser chat interface to Flask, a rule parser, Pandas and the Excel workbook. It is transparent because each supported phrase maps to an explicit rule. This makes it relatively easy to inspect and debug. Its main limitation is language variation: a question can be meaningful to a person but fail when it does not contain a phrase anticipated by the programmer. The parser, filtering and response logic can also become difficult to maintain when many conditions are added. This motivates separating language understanding from data querying in V2.

**Version 2 — Intent and entity recognition.** V2 represents a user's request as an intent and a set of entities. For example, “Count nephew birthdays in September” can be represented as `count_birthdays` with `relationship=Nephew` and `month=9`. Separating the NLU parser from the query service makes the system easier to test: first inspect whether the utterance was interpreted correctly, then inspect whether the spreadsheet query returned the correct rows. However, each request is still treated independently. A follow-up such as “What about October?” is incomplete without the previous turn. This motivates dialogue state in V3.

**Version 3 — Dialogue state and clarification.** V3 stores useful context, such as the previous relationship or month, in a Flask session. It can interpret a follow-up by carrying forward an omitted entity, and it can ask a clarification question when a relationship-only question matches several people. This is safer than silently selecting the first row. Context must be used carefully: stale context can cause a new question to be filtered incorrectly, so the reset action and explicit new entities are important. This version demonstrates that conversation meaning can span multiple turns.

**Version 4 — LLM-assisted NLU with grounding.** V4 optionally uses a language model to interpret paraphrases and return a constrained intent/entity structure. The LLM is not permitted to answer factual birthday questions. The application validates names and other entities against the supplied spreadsheet and sends the validated structure to the same query service. If the API is unavailable or its output is invalid, the rule-based parser provides a fallback. Better language coverage does not automatically guarantee factual accuracy: factual reliability comes from grounding the final answer in the structured workbook. API availability, latency and cost are additional practical considerations.

**Version 5 — Voice interface.** V5 adds browser speech recognition to convert spoken input into text and speech synthesis to read the response aloud. The recognized text is sent through the same backend used by typed questions, so voice is an additional interaction channel rather than a new source of facts. Recognition mistakes can occur with names, dates and Indian place names. It is therefore important to inspect the transcript before concluding that the NLU or data query is wrong. Keeping the text transcript and visible answer supports accessibility and debugging.

## Final reflection

The system first becomes more conversational in V3, when it can retain context and clarify ambiguity across turns. The LLM in V4 can improve the range of natural-language expressions that the system understands, but it does not replace the spreadsheet as the source of truth and cannot guarantee that every interpretation is correct. Dialogue state is useful when a follow-up omits information, but dangerous when old context is reused after the user's topic has changed; context should be explicit, limited and resettable.

Failures can occur at different layers. A language-understanding failure means the intent or entity was extracted incorrectly. A dialogue failure means previous context was incorrectly carried forward or clarification was not requested. A data-model failure means the required fact is missing, inconsistent or ambiguous in the workbook. A response failure means correct rows were retrieved but explained incorrectly. Testing each layer separately makes debugging more systematic.

If deployed with real family information, the application would require access control, secure secret management, HTTPS, data minimization, restricted file permissions, secure backups and a clear retention/deletion policy. Real contact or birthday data must not be published in a public Git repository. API keys must be stored in environment variables and excluded from version control.

## Personal observations to add before submission

- One V1 wording that failed: **[write your actual test]**
- One V2 intent/entity result you inspected: **[paste actual output]**
- One V3 follow-up and clarification result: **[write actual result]**
- V4 API/fallback test result: **[state whether API was configured and tested]**
- V5 speech recognition test result: **[state browser, permission and transcript result]**
- Overall testing result and key limitation: **[summarize your completed TESTING.md]**
