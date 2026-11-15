
import os
import json
import logging

from openai import OpenAI

logging.basicConfig(level=logging.INFO)

SYSTEM = """
You are an NLU parser for a birthday assistant.

Your task is ONLY to understand the user's question
and convert it into structured JSON.

Return JSON only with these two keys:
- intent
- entities

Allowed intents:
birthday_search
count_birthdays
upcoming_birthdays
person_place
unknown

Allowed entities:
person_name
relationship
month
relative_date
relative_month
place

Rules:
1. Never answer factual questions.
2. Never invent birthdays, dates or names.
3. Extract only information explicitly mentioned
   or clearly implied.
4. Use null when an entity is not present.
5. Return an empty entities object when no entities
   are found.
6. If unrelated to birthdays, use unknown.
"""

ALLOWED_INTENTS = {
    "birthday_search",
    "count_birthdays",
    "upcoming_birthdays",
    "person_place",
    "unknown"
}

ALLOWED_ENTITIES = {
    "person_name",
    "relationship",
    "month",
    "relative_date",
    "relative_month",
    "place"
}


def parse_with_llm(message):

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OpenAI API key is not configured.")

    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = client.responses.create(
            model="gpt-5.4-mini",
            instructions=SYSTEM,
            input=message
        )

        output = response.output_text
        result = json.loads(output)

        if not isinstance(result, dict):
            raise ValueError("Invalid LLM response.")

        intent = result.get("intent")
        entities = result.get("entities")

        if intent not in ALLOWED_INTENTS:
            raise ValueError("Invalid intent returned.")

        if not isinstance(entities, dict):
            raise ValueError("Invalid entities returned.")

        entities = {
            key: value
            for key, value in entities.items()
            if key in ALLOWED_ENTITIES and value is not None
        }

        return {
            "intent": intent,
            "entities": entities
        }

    except Exception as exc:
        logging.exception("LLM parsing failed")
        raise
