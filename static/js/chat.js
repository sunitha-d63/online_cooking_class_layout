let currentIndex = 0;

document.addEventListener('DOMContentLoaded', () => {
  const modal = document.getElementById('chatModal');
  const input = document.getElementById('chatInput');
  const container = modal.querySelector('.modal-body');

  modal.addEventListener('shown.bs.modal', () => {
    container.innerHTML = '';     
    currentIndex = 0;          
    addMessage(defaultReplies[currentIndex]); 
    currentIndex++;
    input.focus();
  });

  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && input.value.trim()) {
      addMessage({ sender: 'U', text: input.value.trim() });
      input.value = '';
      if (currentIndex < defaultReplies.length) {
        addMessage(defaultReplies[currentIndex]);
        currentIndex++;
      }
      input.focus();
    }
  });
});

function addMessage(msg) {
  const container = document.querySelector('#chatModal .modal-body');
  const html = `
    <div class="d-flex align-items-start mb-2">
      <span class="bg-danger text-white rounded-circle d-flex align-items-center justify-content-center me-2" style="width:24px; height:24px; font-size:0.75rem;">
        ${msg.sender}
      </span>
      <div class="bg-white rounded-pill px-3 py-2">${msg.text}</div>
    </div>`;
  container.insertAdjacentHTML('beforeend', html);
}
