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
  text = text.trim();
  if (!text) return;
  addMessage(text, 'user');
  question.value = '';
  question.disabled = true;
  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({message: text})
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    addMessage(data.answer || 'No answer returned.', 'bot');
    trace.textContent = (data.trace || []).map((x, i) => `${i + 1}. ${x}`).join('\n');
  } catch (error) {
    addMessage(`Error: ${error.message}`, 'bot');
  } finally {
    question.disabled = false;
    question.focus();
  }
}

form.addEventListener('submit', e => {
  e.preventDefault();
  ask(question.value);
});

document.querySelectorAll('.chip').forEach(button => {
  button.addEventListener('click', () => ask(button.dataset.q));
});

addMessage("Hello! Welcome to Birthday Assistant. How can I help you today?", 'bot');
