
import os

from flask import Flask, render_template, request, jsonify, session

from service import load_people, execute
from nlu import parse
from dialogue import enrich_with_context, update_state


app = Flask(__name__)

# Flask session configuration
app.secret_key = os.getenv(
    'FLASK_SECRET',
    'local-development-secret-change-me'
)

# Load Excel dataset
PEOPLE = load_people()


@app.get('/')
def index():
    return render_template(
        'index.html',
        record_count=len(PEOPLE)
    )


@app.post('/chat')
def chat():

    # Get the user's question
    msg = (request.get_json(silent=True) or {}).get('message', '').strip()

    # Retrieve previous conversation state
    state = session.get('dialogue_state', {})

    # Step 1: Parse the user's message
    parsed = parse(msg, PEOPLE)

    # Step 2: Add previous conversation context
    parsed = enrich_with_context(parsed, state)

    entities = parsed.get('entities', {})

    # Debugging information in terminal
    print("\n========== V3 DIALOGUE DEBUG ==========")
    print("User Message:", msg)
    print("Previous State:", state)
    print("Current Parsed:", parsed)

    # Step 3: Handle empty or unknown questions
    if not msg or parsed.get('intent') == 'unknown':
        answer = (
            "Sorry, I didn't understand. "
            "Please ask me about birthdays, people or relationships."
        )

    # Step 4: Handle ambiguous nicknames
    elif entities.get('ambiguous_nickname'):

        names = ', '.join(entities['ambiguous_nickname'])

        answer = (
            f"I found multiple people with that nickname: "
            f"{names}. Please use a full name."
        )

    # Step 5: Handle ambiguous relationship questions
    elif (
        entities.get('relationship')
        and not entities.get('person_id')
        and 'when is my' in msg.lower()
    ):

        matches = PEOPLE[
            PEOPLE.Relationship.str.casefold()
            == str(entities['relationship']).casefold()
        ]

        if len(matches) > 1:

            names = ', '.join(matches.Name.head(8).tolist())

            answer = (
                f"I found {len(matches)} people recorded as "
                f"{entities['relationship']}: {names}. "
                f"Which one do you mean?"
            )

        else:
            answer = execute(parsed, PEOPLE)

    else:
        # Step 6: Execute the birthday query
        answer = execute(parsed, PEOPLE)

    # Step 7: Update conversation state
    new_state = update_state(parsed, state)

    session['dialogue_state'] = new_state

    # Ensure Flask saves the updated session
    session.modified = True

    print("Updated State:", new_state)
    print("======================================\n")

    # Step 8: Return answer and debugging information
    return jsonify(
        answer=answer,
        debug=parsed,
        trace=[
            f"Intent: {parsed['intent']}",
            f"Entities/context: {entities}",
            f"Previous state: {state}",
            f"Updated state: {new_state}"
        ],
        state=new_state
    )


# Reset conversation endpoint
@app.post('/reset')
def reset():

    session.pop('dialogue_state', None)
    session.modified = True

    return jsonify(
        ok=True,
        message='Conversation context cleared.'
    )


# Health check endpoint
@app.get('/api/health')
def health():

    return jsonify(
        status='ok',
        records=len(PEOPLE),
        version='V3'
    )


if __name__ == '__main__':
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True
    )
