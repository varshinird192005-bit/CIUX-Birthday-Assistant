# Privacy and Security Note — CIUX Birthday Assistant

## 1. Dataset Information

The supplied `people.xlsx` workbook contains fictional teaching records created for educational purposes.

The application reads the following information from the workbook:

- Names
- Nicknames
- Dates of birth
- Places of stay
- Relationship information

This information is used to answer birthday-related and location-related questions.

## 2. Data Protection

If the application is adapted for real people, the following precautions should be followed:

1. Collect only the minimum information required.
2. Obtain appropriate permission before using personal information.
3. Restrict access to the Excel workbook.
4. Avoid collecting phone numbers and street addresses unless they are essential.
5. Never publish real personal information in a public GitHub repository.
6. Define clear data retention, backup and deletion practices.

## 3. API Keys and Credentials

API keys and credentials must be protected.

- Store API keys in environment variables.
- Do not commit API keys, `.env` files or passwords to GitHub.
- Do not publish logs containing personal information.
- Keep credentials separate from application source code.

## 4. LLM Data Protection

When an LLM is configured, it should receive the user's query for semantic parsing only.

The LLM should not be treated as the source of factual birthday information. Factual answers must be retrieved from the local structured Excel dataset.

The complete personal dataset should not be sent to the LLM.

## 5. Deployment Security

Before deploying the application for real users, implement:

- User authentication.
- HTTPS for secure communication.
- Restricted access to stored data.
- Secure API key management.
- Appropriate data backup and deletion procedures.

## 6. Conclusion

Privacy and security are important when developing conversational applications that handle personal information. This project uses fictional teaching records. Any future real-world implementation must protect personal data, secure credentials and prevent unauthorized access.