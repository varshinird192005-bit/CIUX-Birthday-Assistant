
import os
import calendar
import logging

from flask import Flask, render_template, request, jsonify, session

from service import load_people, execute
from nlu import parse as rule_parse
from dialogue import enrich_with_context, update_state
from llm_nlu import parse_with_llm


# ==================================================
# 1. APPLICATION CONFIGURATION
# ==================================================

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

app.secret_key = os.getenv(
    "FLASK_SECRET",
    "local-development-secret-change-me"
)

PEOPLE = load_people()
# Free mode is enabled by default.
# Set USE_OPENAI=true later to activate the LLM.
USE_OPENAI = os.getenv("USE_OPENAI", "false").lower() == "true"


# ==================================================
# 2. NORMALIZE AND GROUND LLM OUTPUT
# ==================================================

def normalize(parsed):

    if not isinstance(parsed, dict):
        raise ValueError("Invalid parser output.")

    entities = parsed.setdefault("entities", {})

    if not isinstance(entities, dict):
        raise ValueError("Invalid entities.")

    # Validate person name against Excel
    if entities.get("person_name"):

        person_name = str(entities["person_name"]).strip()

        matches = PEOPLE[
            PEOPLE["Name"].astype(str).str.casefold()
            == person_name.casefold()
        ]

        if len(matches) == 1:

            entities["person_id"] = str(
                matches.iloc[0]["Person_ID"]
            )

            entities["person_name"] = str(
                matches.iloc[0]["Name"]
            )

        else:
            entities.pop("person_id", None)

    # Normalize relationship
    if entities.get("relationship"):

        valid_relationships = {
            str(value).strip().casefold(): str(value).strip()
            for value in PEOPLE["Relationship"].dropna().unique()
        }

        relationship = str(
            entities["relationship"]
        ).strip().casefold()

        if relationship in valid_relationships:

            entities["relationship"] = (
                valid_relationships[relationship]
            )

    # Normalize month
    if entities.get("month") is not None:

        month = entities["month"]

        if isinstance(month, int):

            if not 1 <= month <= 12:
                entities.pop("month", None)

        else:

            month_names = {
                name.lower(): number
                for number, name in enumerate(calendar.month_name)
                if name
            }

            month_number = month_names.get(
                str(month).strip().lower()
            )

            if month_number is None:
                entities.pop("month", None)
            else:
                entities["month"] = month_number

    return parsed


# ==================================================
# 3. HOME PAGE
# ==================================================

@app.get("/")
def index():

    return render_template(
        "index.html",
        record_count=len(PEOPLE)
    )


# ==================================================
# 4. CHAT ENDPOINT
# ==================================================

@app.post("/api/chat")
def chat():

    data = request.get_json(silent=True) or {}

    message = str(data.get("message", "")).strip()

    if not message:

        return jsonify(
            answer="Please enter a question.",
            trace=[],
            debug={
                "intent": "unknown",
                "entities": {}
            }
        ), 400

    state = session.get("dialogue_state", {})

    parsed = None
    trace = []

    # ----------------------------------------------
    # STEP 1: LLM PARSING
    # ----------------------------------------------

    if USE_OPENAI and os.getenv("OPENAI_API_KEY"):

        try:

            print("\n========== V4 LLM DEBUG ==========")
            print("User question:", message)
            print("Calling OpenAI LLM...")

            parsed = parse_with_llm(message)

            parsed = normalize(parsed)

            print("LLM SUCCESS!")
            print("Parsed result:", parsed)

            trace.append(
                "LLM successfully processed the question."
            )

        except Exception as error:

            print("\n========== LLM ERROR DETAILS ==========")
            print("Error type:", type(error).__name__)
            print(
                "Error message:",
                getattr(error, "message", str(error))
            )
            print("Error body:", getattr(error, "body", None))

            if hasattr(error, "response"):
                print("HTTP response:", error.response.text)

            print("Switching to rule-based fallback...")

            parsed = rule_parse(message, PEOPLE)

            print("Fallback result:", parsed)

            trace.append(
                "LLM unavailable or invalid; "
                f"rule-based fallback used ({type(error).__name__})."
            )
    else:

        print("\n========== FREE MODE ==========")
        print("OpenAI LLM is disabled.")
        print("Using rule-based parser.")

        parsed = rule_parse(message, PEOPLE)

        trace.append(
            "Free mode active: rule-based parser used. "
            "OpenAI LLM is available for future activation."
        )

    # ----------------------------------------------
    # STEP 2: VALIDATE PARSER OUTPUT
    # ----------------------------------------------

    if not isinstance(parsed, dict):

        parsed = rule_parse(message, PEOPLE)

        trace.append(
            "Invalid parser structure; rule-based fallback used."
        )

    parsed.setdefault("intent", "unknown")
    parsed.setdefault("entities", {})

    # ----------------------------------------------
    # STEP 3: ADD DIALOGUE CONTEXT
    # ----------------------------------------------

    parsed = enrich_with_context(parsed, state)

    entities = parsed.get("entities", {})

    print("Final intent:", parsed.get("intent"))
    print("Final entities:", entities)

    # ----------------------------------------------
    # STEP 4: HANDLE AMBIGUOUS NICKNAMES
    # ----------------------------------------------

    if entities.get("ambiguous_nickname"):

        names = entities["ambiguous_nickname"]

        answer = (
            "I found multiple people with that nickname: "
            + ", ".join(names)
            + ". Please use a full name."
        )

    # ----------------------------------------------
    # STEP 5: HANDLE RELATIONSHIP AMBIGUITY
    # ----------------------------------------------

    elif (
        entities.get("relationship")
        and not entities.get("person_id")
        and "when is my" in message.casefold()
    ):

        matches = PEOPLE[
            PEOPLE["Relationship"].astype(str).str.casefold()
            == str(entities["relationship"]).casefold()
        ]

        if len(matches) > 1:

            names = ", ".join(
                matches["Name"].head(8).astype(str)
            )

            answer = (
                f"I found {len(matches)} people recorded as "
                f"{entities['relationship']}: {names}. "
                "Which one do you mean?"
            )

        else:

            answer = execute(parsed, PEOPLE)

    # ----------------------------------------------
    # STEP 6: EXECUTE EXCEL QUERY
    # ----------------------------------------------

    else:

        answer = execute(parsed, PEOPLE)

    # ----------------------------------------------
    # STEP 7: UPDATE DIALOGUE STATE
    # ----------------------------------------------

    session["dialogue_state"] = update_state(
        parsed,
        state
    )

    session.modified = True

    # ----------------------------------------------
    # STEP 8: PREPARE DEBUG INFORMATION
    # ----------------------------------------------

    trace.extend([
        f"Intent: {parsed.get('intent', 'unknown')}",
        f"Entities/context: {entities}",
        "Query service reads data/people.xlsx."
    ])

    # ----------------------------------------------
    # STEP 9: RETURN RESPONSE
    # ----------------------------------------------

    return jsonify(
        answer=answer,
        trace=trace,
        state=session["dialogue_state"],
        debug=parsed
    )


# ==================================================
# 5. RESET CONVERSATION
# ==================================================

@app.post("/api/reset")
def reset():

    session.pop("dialogue_state", None)

    print("Conversation context reset.")

    return jsonify(
        ok=True,
        message="Conversation context cleared."
    )


# ==================================================
# 6. HEALTH CHECK
# ==================================================

@app.get("/api/health")
def health():

    return jsonify(
        status="ok",
        records=len(PEOPLE),
        version="V4",
        openai_configured=bool(os.getenv("OPENAI_API_KEY"))
    )


# ==================================================
# 7. RUN APPLICATION
# ==================================================

if __name__ == "__main__":

    print("\n===================================")
    print("       BIRTHDAY ASSISTANT V4")
    print("===================================")

    print("Excel records:", len(PEOPLE))

    print(
        "OpenAI API key configured:",
        bool(os.getenv("OPENAI_API_KEY"))
    )

    print("Server: http://127.0.0.1:5000")
    print("===================================\n")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
