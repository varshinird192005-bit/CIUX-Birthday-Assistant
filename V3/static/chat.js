
const chat = document.getElementById('chat');
const form = document.getElementById('chat-form');
const question = document.getElementById('question');

const intentBox = document.getElementById('nlu-intent');
const entitiesBox = document.getElementById('nlu-entities');

// Display chat messages
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

// Update NLU information
function updateNLU(debug) {
    if (!debug) return;

    if (intentBox) {
        intentBox.textContent = debug.intent || 'Unknown';
    }

    if (entitiesBox) {
        entitiesBox.textContent = JSON.stringify(
            debug.entities || {},
            null,
            2
        );
    }
}

// Send a question
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

        addMessage(
            data.answer || 'No answer returned.',
            'bot'
        );

        // Display detected intent and entities
        updateNLU(data.debug);

    } catch (error) {
        addMessage('Error: ' + error.message, 'bot');

    } finally {
        question.disabled = false;
        question.focus();
    }
}

// Handle message submission
form.addEventListener('submit', function(event) {
    event.preventDefault();
    ask(question.value);
});

// Handle example question buttons
document.querySelectorAll('.chip[data-q]').forEach(button => {
    button.addEventListener('click', function() {
        ask(button.dataset.q);
    });
});

// Reset conversation
const resetButton = document.createElement('button');

resetButton.textContent = 'Reset Conversation';
resetButton.className = 'chip reset-button';
resetButton.type = 'button';

resetButton.addEventListener('click', async function() {
    try {
        const response = await fetch('/reset', {
            method: 'POST'
        });

        if (!response.ok) {
            throw new Error('Could not reset conversation.');
        }

        addMessage(
            'Conversation context cleared. You can start a new conversation!',
            'bot'
        );

        if (intentBox) {
            intentBox.textContent = 'Waiting for your question...';
        }

        if (entitiesBox) {
            entitiesBox.textContent = 'No entities extracted yet.';
        }

    } catch (error) {
        addMessage('Reset error: ' + error.message, 'bot');
    }
});

// Add reset button to the example questions section
const chips = document.querySelector('.chips');

if (chips) {
    chips.appendChild(resetButton);
}

// Welcome message
addMessage(
    'Hello! I am the Birthday Assistant. Ask me about birthdays, relationships or places.',
    'bot'
);

