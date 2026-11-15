
from flask import Flask, render_template, request, jsonify

from service import load_people, execute
from nlu import parse

app = Flask(__name__)

# Load the Excel dataset
PEOPLE = load_people()


@app.get('/')
def index():
    return render_template(
        'index.html',
        record_count=len(PEOPLE)
    )


@app.post('/chat')
def chat():
    msg = (request.get_json(silent=True) or {}).get('message', '')

    # Step 1: Identify intent and entities
    parsed = parse(msg, PEOPLE)

    # Step 2: Execute the query and generate the answer
    answer = execute(parsed, PEOPLE)

    # Step 3: Return answer and NLU debugging information
    return jsonify(
        answer=answer,
        debug=parsed,
        trace=[
            f"Intent: {parsed['intent']}",
            f"Entities: {parsed['entities']}"
        ]
    )


@app.get('/api/health')
def health():
    return jsonify(
        status='ok',
        records=len(PEOPLE),
        version='V2'
    )


if __name__ == '__main__':
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True
    )
