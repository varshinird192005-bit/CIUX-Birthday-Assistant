# Privacy and security note

The supplied `people.xlsx` contains fictional teaching records. The application reads names, nicknames, dates of birth, places of stay and relationship fields from this workbook. The data is used to answer birthday and location questions.

If the project is adapted to real people, use only the minimum necessary information, obtain appropriate permission, restrict access to the workbook, avoid collecting phone numbers or street addresses unless essential, and do not publish the workbook to a public repository. Do not commit API keys, `.env` files, credentials, logs containing personal information or real datasets. Store API keys in environment variables. Use authentication and HTTPS before any real deployment. Define retention, backup and deletion practices.

The LLM (when configured) should receive the user's query for semantic parsing only; factual answers must be retrieved from the local structured dataset. Do not send the entire personal dataset to the LLM.
