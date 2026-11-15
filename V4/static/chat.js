
const chat = document.getElementById('chat');
const form = document.getElementById('chat-form');
const question = document.getElementById('question');
const trace = document.getElementById('trace');

// Display messages in chat
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

// Determine which parser was used
function getParserStatus(data) {
    const messages = data.trace || [];

    if (messages.some(item => item.includes('Free mode active'))) {
        return 'Free mode – Rule-based parser used';
    }

    if (messages.some(item => item.includes('LLM successfully processed'))) {
        return 'LLM successfully processed the question';
    }

    if (messages.some(item => item.includes('fallback used'))) {
        return 'Rule-based fallback used';
    }

    return 'Parser status unavailable';
}

// Send question to Flask backend
async function ask(text) {
    text = (text || '').trim();

    if (!text) return;

    addMessage(text, 'user');

    question.value = '';
    question.disabled = true;

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: text })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        // Display assistant answer
        addMessage(data.answer || 'No answer returned.', 'bot');

        // Display trace information
        trace.textContent = (data.trace || []).join('\n');

        // Display NLU interpretation
        const debug = data.debug || {};

        document.getElementById('nlu-intent').textContent =
            debug.intent || 'Not available';

        document.getElementById('nlu-entities').textContent =
            JSON.stringify(debug.entities || {}, null, 2);

        // Display correct parser status
        document.getElementById('parser-status').textContent =
            getParserStatus(data);

        // Optional speech output
        const speak = document.getElementById('speak-back');

        if (
            speak &&
            speak.checked &&
            'speechSynthesis' in window
        ) {
            speechSynthesis.cancel();

            const utterance = new SpeechSynthesisUtterance(
                data.answer || ''
            );

            speechSynthesis.speak(utterance);
        }

    } catch (error) {
        addMessage('Error: ' + error.message, 'bot');

    } finally {
        question.disabled = false;
        question.focus();
    }
}

// Submit question
form.addEventListener('submit', event => {
    event.preventDefault();
    ask(question.value);
});

// Example question buttons
document.querySelectorAll('.chip[data-q]').forEach(button => {
    button.addEventListener('click', () => {
        ask(button.dataset.q);
    });
});

// Reset conversation
let reset = document.getElementById('reset-button');

if (!reset) {
    reset = document.createElement('button');
    reset.id = 'reset-button';
    reset.textContent = 'Reset conversation';
    reset.className = 'chip';
    reset.type = 'button';

    document.querySelector('.chips')?.appendChild(reset);
}

reset.addEventListener('click', async () => {
    try {
        const response = await fetch('/api/reset', {
            method: 'POST'
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        speechSynthesis?.cancel?.();

        addMessage('Conversation context cleared.', 'bot');

        trace.textContent = '';

        document.getElementById('nlu-intent').textContent =
            'Waiting for your question...';

        document.getElementById('nlu-entities').textContent =
            'No entities extracted yet.';

        document.getElementById('parser-status').textContent =
            'Conversation context reset.';

    } catch (error) {
        addMessage('Could not reset conversation: ' + error.message, 'bot');
    }
});

// Welcome message
addMessage(
    'Hello! I am the Birthday Assistant. Ask me about birthdays, relationships or places.',
    'bot'
);
