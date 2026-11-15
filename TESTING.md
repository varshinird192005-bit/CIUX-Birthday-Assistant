# TESTING.md — 40 utterance evaluation

The manual requires at least 40 utterances: 10 direct, 10 paraphrased, 10 contextual/multi-turn and 10 ambiguous or unsupported. Run these against each version where applicable. Record the actual observed response; do not mark PASS until you have tested it.

| # | Category | Test utterance / sequence | Expected behaviour | Observed result (fill after run) | PASS/FAIL |
|---:|---|---|---|---|---|
| 1 | Direct | Any nephew birthdays in September? | Return nephew rows with September DOBs. | _Not tested_ | _Pending_ |
| 2 | Direct | How many birthdays are there next month? | Return a count for next month. | _Not tested_ | _Pending_ |
| 3 | Direct | Is there any birthday tomorrow? | Return tomorrow matches or a no-match response. | _Not tested_ | _Pending_ |
| 4 | Direct | When is my wife's birthday? | Return spouse record or a clarification if multiple. | _Not tested_ | _Pending_ |
| 5 | Direct | Who has birthdays this week? | Return birthdays in the current week (V1 may only support documented rules). | _Not tested_ | _Pending_ |
| 6 | Direct | When is Rahul Patil’s birthday? | Return Rahul Patil DOB from workbook. | _Not tested_ | _Pending_ |
| 7 | Direct | Where does Rahul Patil stay? | Return Rahul Patil place from workbook. | _Not tested_ | _Pending_ |
| 8 | Direct | Show birthdays in October. | Return October birthday rows. | _Not tested_ | _Pending_ |
| 9 | Direct | Show upcoming birthdays. | Return upcoming window results. | _Not tested_ | _Pending_ |
| 10 | Direct | Count niece birthdays in September. | Return count matching relationship and month. | _Not tested_ | _Pending_ |
| 11 | Paraphrase | Do I need to wish any nephew during September? | Same data result as nephew birthdays in September. | _Not tested_ | _Pending_ |
| 12 | Paraphrase | Are there any nephews celebrating in September? | Same result as direct query. | _Not tested_ | _Pending_ |
| 13 | Paraphrase | List the September birthdays of my nephews. | Same result as direct query. | _Not tested_ | _Pending_ |
| 14 | Paraphrase | Tell me the birthday date for Rahul Patil. | Return Rahul Patil DOB. | _Not tested_ | _Pending_ |
| 15 | Paraphrase | Which city is Rahul Patil living in? | Return Rahul Patil place. | _Not tested_ | _Pending_ |
| 16 | Paraphrase | Give me the birthdays coming soon. | Return upcoming birthday results or explain unsupported phrasing. | _Not tested_ | _Pending_ |
| 17 | Paraphrase | How many people celebrate next month? | Return next-month birthday count. | _Not tested_ | _Pending_ |
| 18 | Paraphrase | Are there birthday celebrations the day after today? | Recognize tomorrow if supported; otherwise report limitation. | _Not tested_ | _Pending_ |
| 19 | Paraphrase | Show me everyone born in December. | Return December birthday rows. | _Not tested_ | _Pending_ |
| 20 | Paraphrase | I want to know the number of nieces in March. | Return March niece count. | _Not tested_ | _Pending_ |
| 21 | Context / multi-turn | Any nephew birthdays in September? → What about October? | Carry relationship=nephew and change month to October (V3+). | _Not tested_ | _Pending_ |
| 22 | Context / multi-turn | Birthdays in September → What about October? | Carry birthday-search intent and replace month. | _Not tested_ | _Pending_ |
| 23 | Context / multi-turn | Any niece birthdays in June? → What about July? | Carry niece relationship and change month. | _Not tested_ | _Pending_ |
| 24 | Context / multi-turn | Count nephew birthdays in August → What about September? | Carry relationship and count intent if implemented. | _Not tested_ | _Pending_ |
| 25 | Context / multi-turn | When is my nephew’s birthday? → Nikhil | Ask which nephew, then resolve the supplied name. | _Not tested_ | _Pending_ |
| 26 | Context / multi-turn | Birthdays in April → What about May? | Use previous birthday-search context. | _Not tested_ | _Pending_ |
| 27 | Context / multi-turn | Any birthdays in November? → Count them. | Carry November and count matching rows. | _Not tested_ | _Pending_ |
| 28 | Context / multi-turn | Any nephew birthdays in September? → Reset conversation → What about October? | After reset, do not reuse September/nephew context. | _Not tested_ | _Pending_ |
| 29 | Context / multi-turn | Who has birthdays in July? → Where does Rahul stay? | New named-person place query should not be polluted by old month. | _Not tested_ | _Pending_ |
| 30 | Context / multi-turn | Any birthdays next month? → What about September? | Explicit month should replace relative month. | _Not tested_ | _Pending_ |
| 31 | Ambiguous / unsupported | When is my nephew’s birthday? | Ask which nephew when multiple records match. | _Not tested_ | _Pending_ |
| 32 | Ambiguous / unsupported | When is Nikhil’s birthday? | If nickname matches multiple records, ask for full name. | _Not tested_ | _Pending_ |
| 33 | Ambiguous / unsupported | Who is the kindest person? | State that this is unsupported by the dataset. | _Not tested_ | _Pending_ |
| 34 | Ambiguous / unsupported | Tell me the phone number of Rahul. | Do not invent or disclose unavailable fields. | _Not tested_ | _Pending_ |
| 35 | Ambiguous / unsupported | Any birthdays on 31 February? | Reject invalid date / return no valid date; never fabricate. | _Not tested_ | _Pending_ |
| 36 | Ambiguous / unsupported | What is my neighbour’s favourite food? | Explain unsupported information. | _Not tested_ | _Pending_ |
| 37 | Ambiguous / unsupported | Find the birthday of an unknown person named Zorina. | Say no matching person is in the dataset. | _Not tested_ | _Pending_ |
| 38 | Ambiguous / unsupported | What about October? | Without prior context, ask what category/query is intended. | _Not tested_ | _Pending_ |
| 39 | Ambiguous / unsupported | Show me all private addresses. | Do not claim the dataset contains street addresses. | _Not tested_ | _Pending_ |
| 40 | Ambiguous / unsupported | Tell me the birthday of the first nephew. | Ask for a specific person; do not arbitrarily choose one. | _Not tested_ | _Pending_ |

## Evaluation metrics to calculate after testing
- **Intent accuracy:** correctly identified intents / total labeled utterances.
- **Entity accuracy:** correctly extracted entity values / expected entity values.
- **Task success:** valid questions answered with the correct spreadsheet result / total valid questions.
- **Clarification success:** ambiguous turns that receive a useful clarification / ambiguous turns tested.
- **Grounded factuality:** returned DOB/place/relationship values that exactly match the workbook.
- **Latency:** approximate time from Send to displayed response.
- **Voice recognition success (V5):** correctly transcribed spoken utterances / spoken utterances tested.
- **User experience:** short peer test on clarity, error recovery, trust and ease of use.

## Engineering log template
| Version | Question tried | Expected result | Observed result | Reason for failure | Fix made |
|---|---|---|---|---|---|
| V1 | | | | | |
| V2 | | | | | |
| V3 | | | | | |
| V4 | | | | | |
| V5 | | | | | |
