
const chat = document.getElementById('chat');
const form = document.getElementById('chat-form');
const question = document.getElementById('question');
const trace = document.getElementById('trace');

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
        const answer = data.answer || 'No answer returned.';

        addMessage(answer, 'bot');
       if (trace) {
    trace.textContent = (data.trace || []).join('\n');
}

        // Read the response aloud when enabled
        const speakBack = document.getElementById('speak-back');

        if (speakBack && speakBack.checked && 'speechSynthesis' in window) {
            window.speechSynthesis.cancel();

            const utterance = new SpeechSynthesisUtterance(answer);
            utterance.lang = 'en-IN';

            window.speechSynthesis.speak(utterance);
        }

    } catch (error) {
        addMessage('Error: ' + error.message, 'bot');

    } finally {
        question.disabled = false;
        question.focus();
    }
}

// Normal text submission
form.addEventListener('submit', function(event) {
    event.preventDefault();
    ask(question.value);
});

// Example question buttons
document.querySelectorAll('.chip[data-q]').forEach(button => {
    button.addEventListener('click', function() {
        ask(button.dataset.q);
    });
});

// Microphone speech recognition
const mic = document.getElementById('speak-button');

if (mic) {
    mic.addEventListener('click', function() {

        const SpeechRecognition =
            window.SpeechRecognition ||
            window.webkitSpeechRecognition;

        if (!SpeechRecognition) {
            addMessage(
                'Speech recognition is not supported. Please use Google Chrome or Microsoft Edge.',
                'bot'
            );
            return;
        }

        const recognition = new SpeechRecognition();

        recognition.lang = 'en-IN';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        recognition.onstart = function() {
            addMessage('Listening... Please speak now.', 'bot');
            mic.disabled = true;
        };

        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;

            // Show recognized speech in the input box
            question.value = transcript;

            // Send the recognized question to the same backend
            ask(transcript);
        };

        recognition.onerror = function(event) {
            addMessage('Voice input error: ' + event.error, 'bot');
        };

        recognition.onend = function() {
            mic.disabled = false;
        };

        try {
            recognition.start();
        } catch (error) {
            addMessage('Could not start microphone: ' + error.message, 'bot');
            mic.disabled = false;
        }
    });
}

// Reset conversation button
const reset = document.createElement('button');

reset.textContent = 'Reset conversation';
reset.className = 'chip';
reset.type = 'button';

reset.addEventListener('click', async function() {
    try {
        const response = await fetch('/api/reset', {
            method: 'POST'
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
        }

        addMessage('Conversation context cleared.', 'bot');
        if (trace) {
    trace.textContent = 'Context reset.';
}

    } catch (error) {
        addMessage('Could not reset conversation: ' + error.message, 'bot');
    }
});

document.querySelector('.chips')?.appendChild(reset);

// Welcome message
addMessage(
    'Hello! I am the Birthday Assistant V5. You can type or speak your questions.',
    'bot'
);
