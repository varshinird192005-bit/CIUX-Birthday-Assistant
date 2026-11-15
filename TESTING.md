# TESTING.md — 40 Utterance Evaluation

## 1. Testing Overview

The Birthday Assistant was evaluated using 40 test utterances divided into four categories:

- 10 Direct queries
- 10 Paraphrased queries
- 10 Contextual or multi-turn queries
- 10 Ambiguous or unsupported queries

The tests evaluate intent recognition, entity extraction, dialogue context, clarification handling, spreadsheet data retrieval, and unsupported requests.

The tests should be run against each version (V1–V5) where applicable. Actual responses must be recorded. A test must not be marked PASS until its result has been manually verified against the expected behaviour and the source workbook.

## 2. Forty-Utterance Evaluation Table

| # | Category | Test utterance / sequence | Expected behaviour | Observed result | PASS/FAIL |
|---:|---|---|---|---|---|
| 1 | Direct | Any nephew birthdays in September? | Return nephew rows with September DOBs. | Not manually verified | Pending |
| 2 | Direct | How many birthdays are there next month? | Return a count for next month. | Not manually verified | Pending |
| 3 | Direct | Is there any birthday tomorrow? | Return tomorrow matches or a no-match response. | Not manually verified | Pending |
| 4 | Direct | When is my wife's birthday? | Return spouse record or clarification if multiple records match. | Not manually verified | Pending |
| 5 | Direct | Who has birthdays this week? | Return birthdays in the current week, where supported. | Not manually verified | Pending |
| 6 | Direct | When is Rahul Patil’s birthday? | Return Rahul Patil's DOB from the workbook. | Not manually verified | Pending |
| 7 | Direct | Where does Rahul Patil stay? | Return Rahul Patil's place from the workbook. | Not manually verified | Pending |
| 8 | Direct | Show birthdays in October. | Return October birthday rows. | Not manually verified | Pending |
| 9 | Direct | Show upcoming birthdays. | Return upcoming birthday results. | Not manually verified | Pending |
| 10 | Direct | Count niece birthdays in September. | Return count matching relationship and month. | Not manually verified | Pending |
| 11 | Paraphrase | Do I need to wish any nephew during September? | Same data result as nephew birthdays in September. | Not manually verified | Pending |
| 12 | Paraphrase | Are there any nephews celebrating in September? | Same result as direct query. | Not manually verified | Pending |
| 13 | Paraphrase | List the September birthdays of my nephews. | Same result as direct query. | Not manually verified | Pending |
| 14 | Paraphrase | Tell me the birthday date for Rahul Patil. | Return Rahul Patil's DOB. | Not manually verified | Pending |
| 15 | Paraphrase | Which city is Rahul Patil living in? | Return Rahul Patil's place. | Not manually verified | Pending |
| 16 | Paraphrase | Give me the birthdays coming soon. | Return upcoming birthday results or explain unsupported phrasing. | Not manually verified | Pending |
| 17 | Paraphrase | How many people celebrate next month? | Return next-month birthday count. | Not manually verified | Pending |
| 18 | Paraphrase | Are there birthday celebrations the day after today? | Recognize tomorrow if supported; otherwise report limitation. | Not manually verified | Pending |
| 19 | Paraphrase | Show me everyone born in December. | Return December birthday rows. | Not manually verified | Pending |
| 20 | Paraphrase | I want to know the number of nieces in March. | Return March niece count. | Not manually verified | Pending |
| 21 | Context / multi-turn | Any nephew birthdays in September? → What about October? | Carry relationship=nephew and change month to October (V3+). | Not manually verified | Pending |
| 22 | Context / multi-turn | Birthdays in September → What about October? | Carry birthday-search intent and replace month. | Not manually verified | Pending |
| 23 | Context / multi-turn | Any niece birthdays in June? → What about July? | Carry niece relationship and change month. | Not manually verified | Pending |
| 24 | Context / multi-turn | Count nephew birthdays in August → What about September? | Carry relationship and count intent if implemented. | Not manually verified | Pending |
| 25 | Context / multi-turn | When is my nephew’s birthday? → Nikhil | Ask which nephew, then resolve the supplied name or ask for a full name if ambiguous. | Not manually verified | Pending |
| 26 | Context / multi-turn | Birthdays in April → What about May? | Use previous birthday-search context. | Not manually verified | Pending |
| 27 | Context / multi-turn | Any birthdays in November? → Count them. | Carry November and count matching rows. | Not manually verified | Pending |
| 28 | Context / multi-turn | Any nephew birthdays in September? → Reset conversation → What about October? | After reset, do not reuse September/nephew context. | Not manually verified | Pending |
| 29 | Context / multi-turn | Who has birthdays in July? → Where does Rahul stay? | New named-person place query should not be polluted by old month. | Not manually verified | Pending |
| 30 | Context / multi-turn | Any birthdays next month? → What about September? | Explicit month should replace relative month. | Not manually verified | Pending |
| 31 | Ambiguous / unsupported | When is my nephew’s birthday? | Ask which nephew when multiple records match. | Not manually verified | Pending |
| 32 | Ambiguous / unsupported | When is Nikhil’s birthday? | If nickname matches multiple records, ask for full name. | Not manually verified | Pending |
| 33 | Ambiguous / unsupported | Who is the kindest person? | State that this is unsupported by the dataset. | Not manually verified | Pending |
| 34 | Ambiguous / unsupported | Tell me the phone number of Rahul. | Do not invent or disclose unavailable fields. | Not manually verified | Pending |
| 35 | Ambiguous / unsupported | Any birthdays on 31 February? | Reject invalid date or return no valid date; never fabricate. | Not manually verified | Pending |
| 36 | Ambiguous / unsupported | What is my neighbour’s favourite food? | Explain that this information is unsupported. | Not manually verified | Pending |
| 37 | Ambiguous / unsupported | Find the birthday of an unknown person named Zorina. | Say no matching person is in the dataset. | Not manually verified | Pending |
| 38 | Ambiguous / unsupported | What about October? | Without prior context, ask what category or query is intended. | Not manually verified | Pending |
| 39 | Ambiguous / unsupported | Show me all private addresses. | Do not claim the dataset contains street addresses. | Not manually verified | Pending |
| 40 | Ambiguous / unsupported | Tell me the birthday of the first nephew. | Ask for a specific person; do not arbitrarily choose one. | Not manually verified | Pending |

## 3. Automated 40-Test Evaluation Results

The automated evaluation was executed using the `run_40_tests.py` script.

The following results were generated:

| Version | PASS | FAIL | REVIEW |
|---|---:|---:|---:|
| V1 | 3 | 0 | 37 |
| V2 | 3 | 0 | 37 |
| V3 | 6 | 0 | 34 |
| V4 | 6 | 0 | 34 |
| V5 | 6 | 0 | 34 |
| **Total** | **24** | **0** | **176** |

### Interpretation

- **PASS:** The automated runner identified the response as matching its success criteria.
- **FAIL:** The automated runner identified a failure.
- **REVIEW:** The response requires manual inspection and verification.

No automated failures were reported in this execution. However, REVIEW results must not be treated as successful tests without manual verification.

The evaluation reports were saved in:

- `test_results.csv`
- `test_results.md`

## 4. Evaluation Metrics

The following metrics are used to evaluate the Birthday Assistant:

1. **Intent Accuracy:** Correctly identified intents divided by total labeled utterances.
2. **Entity Accuracy:** Correctly extracted entity values divided by expected entity values.
3. **Task Success:** Valid questions answered with the correct spreadsheet result divided by total valid questions.
4. **Clarification Success:** Ambiguous turns receiving useful clarification divided by ambiguous turns tested.
5. **Grounded Factuality:** Returned DOB, place, and relationship values that exactly match the workbook.
6. **Latency:** Approximate time from sending a question to displaying the response.
7. **Voice Recognition Success (V5):** Correctly transcribed spoken utterances divided by spoken utterances tested.
8. **User Experience:** Peer evaluation of clarity, error recovery, trust, and ease of use.

The metric values should be calculated after the required manual verification. They are not reported as measured results in this document.

## 5. Engineering Log

Use this table to record problems found during testing and the fixes made.

| Version | Question tried | Expected result | Observed result | Reason for failure | Fix made |
|---|---|---|---|---|---|
| V1 | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded |
| V2 | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded |
| V3 | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded |
| V4 | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded |
| V5 | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded |

## 6. Automated Pytest Execution Summary

Automated unit and application tests were executed using pytest.

| Version | Test Command | Passed | Failed |
|---|---|---:|---:|
| V1 | `python -m pytest tests/ -v` | 6 | 0 |
| V2 | `python -m pytest tests/ -v` | 3 | 0 |
| V3 | `python -m pytest tests/ -v` | 3 | 0 |
| V4 | `python -m pytest tests/ -v` | 3 | 0 |
| V5 | `python -m pytest tests/ -v` | 3 | 0 |
| **Total** | | **18** | **0** |

All 18 collected automated pytest tests passed in the recorded execution.

The pytest results are separate from the 40-utterance conversational evaluation.

## 7. Testing Conclusion

The Birthday Assistant V1–V5 applications were executed using the automated 40-utterance evaluation script.

The latest execution reported 24 PASS, 0 FAIL, and 176 REVIEW results across the five versions. All five versions completed the automated evaluation, including V4 in free rule-based mode without requiring an OpenAI API key.

Additionally, 18 pytest tests passed across the five versions in the recorded pytest execution.
The REVIEW cases require further manual verification against the expected behaviour and the Excel dataset. The 40 conversational test cases must only be marked PASS or FAIL after their observed responses have been checked.

This testing process helps evaluate the correctness of the assistant, its ability to understand different user queries, its handling of conversation context, and its ability to avoid unsupported or incorrect answers.