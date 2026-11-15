
const chat = document.getElementById('chat');
const form = document.getElementById('chat-form');
const question = document.getElementById('question');

const intentBox = document.getElementById('nlu-intent');
const entitiesBox = document.getElementById('nlu-entities');

function addMessage(text, role) {
    const row = document.createElement('div');
    row.className = `message ${role}`;

    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    bubble.textContent = text;

    row.appendChild(bubble);
    chat.appendChild(row);
    chat.scrollTop = chat.scrollHeight;
}

function updateNLU(debug) {
    if (!debug) return;

    // Display detected intent
    intentBox.textContent = debug.intent || 'Unknown';

    // Display extracted entities
    const entities = debug.entities || {};

    if (Object.keys(entities).length === 0) {
        entitiesBox.textContent = 'No entities extracted.';
    } else {
        entitiesBox.textContent = JSON.stringify(entities, null, 2);
    }
}

async function ask(text) {
    text = (text || '').trim();

    if (!text) return;

    addMessage(text, 'user');

    question.value = '';
    question.disabled = true;

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: text
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        addMessage(data.answer || 'No answer returned.', 'bot');

        // Update the live NLU panel
        updateNLU(data.debug);

    } catch (error) {
        addMessage('Error: ' + error.message, 'bot');

    } finally {
        question.disabled = false;
        question.focus();
    }
}

// Handle form submission
form.addEventListener('submit', function (event) {
    event.preventDefault();
    ask(question.value);
});

// Handle example question buttons
document.querySelectorAll('.chip[data-q]').forEach(button => {
    button.addEventListener('click', function () {
        ask(button.dataset.q);
    });
});

// Welcome message
addMessage(
    'Hello! Welcome to Birthday Assistant. How can I help you today?',
    'bot'
);
