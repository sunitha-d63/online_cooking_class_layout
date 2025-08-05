const defaultReplies = [
  { id: 'bot-1', sender: 'Bot', text: 'Hello! How can I assist you today?' },
  { id: 'bot-2', sender: 'Bot', text: 'We offer several premium courses for all skill levels.' },
  { id: 'bot-3', sender: 'Bot', text: 'Feel free to explore "View Courses" anytime.' }
];
let messages = JSON.parse(localStorage.getItem('chatMessages') || '[]');
const msgsEl = document.getElementById('msgs');
const inp    = document.getElementById('inp');
const sendBtn      = document.getElementById('sendBtn');
const toggleBtn    = document.getElementById('chatToggle');
const closeBtn     = document.getElementById('closeChat');
const chatOverlay  = document.getElementById('chatOverlay');
function renderMsg(msg) {
  const bubble = document.createElement('div');
  bubble.className = 'd-flex ' +
    (msg.sender === 'You' ? 'justify-content-end' : 'justify-content-start');
  bubble.innerHTML = `
    <div class="p-2 m-1 rounded ${
      msg.sender === 'You'
        ? 'bg-primary text-white text-end'
        : 'bg-light text-dark'
    }">
      <small><em>${msg.sender}:</em></small><br>${msg.text}
    </div>`;
  msgsEl.appendChild(bubble);
}
function refreshMsgs() {
  msgsEl.innerHTML = '';
  messages.forEach(renderMsg);
  msgsEl.scrollTop = msgsEl.scrollHeight;
}
function clearChat() {
  localStorage.removeItem('chatMessages');
  messages = [];
  msgsEl.innerHTML = '';
}
function sendMsg() {
  const text = inp.value.trim();
  if (!text) return;
  const userMsg = { id: `u-${Date.now()}`, sender: 'You', text };
  messages.push(userMsg);
  localStorage.setItem('chatMessages', JSON.stringify(messages));
  renderMsg(userMsg);
  inp.value = '';
  msgsEl.scrollTop = msgsEl.scrollHeight;
  const nextIndex = messages.filter(m => m.sender === 'Bot').length;
  if (nextIndex < defaultReplies.length) {
    setTimeout(() => {
      const botMsg = defaultReplies[nextIndex];
      messages.push(botMsg);
      localStorage.setItem('chatMessages', JSON.stringify(messages));
      renderMsg(botMsg);
      msgsEl.scrollTop = msgsEl.scrollHeight;
    }, 800);
  }
}

toggleBtn.addEventListener('click', () => {
  if (!chatOverlay.classList.contains('d-none')) {
    return;
  }
  clearChat();
  messages = [ defaultReplies[0] ];
  localStorage.setItem('chatMessages', JSON.stringify(messages));
  refreshMsgs();
  chatOverlay.classList.remove('d-none');
  msgsEl.scrollTop = msgsEl.scrollHeight;
  inp.focus();
});
closeBtn.addEventListener('click', () => {
  chatOverlay.classList.add('d-none');
  clearChat();
});
sendBtn.addEventListener('click', sendMsg);
inp.addEventListener('keydown', e => e.key === 'Enter' && sendMsg());
if (messages.length === 0) {
  messages = [ defaultReplies[0] ];
  localStorage.setItem('chatMessages', JSON.stringify(messages));
}
refreshMsgs();
