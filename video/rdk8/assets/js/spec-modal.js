// Opens a row's detail <template> in the shared dialog.
(function () {
  const modal = document.getElementById('spec-modal');
  const body = document.getElementById('spec-modal-body');
  if (!modal || !body) return;

  let lastFocused = null;

  const close = () => {
    modal.hidden = true;
    modal.classList.remove('open');
    body.innerHTML = '';
    if (lastFocused) lastFocused.focus();
  };

  const open = (template) => {
    body.innerHTML = '';
    body.appendChild(template.content.cloneNode(true));
    modal.hidden = false;
    modal.classList.add('open');
    modal.querySelector('.spec-modal-close').focus();
  };

  document.addEventListener('click', (event) => {
    const trigger = event.target.closest('a.spec-modal-trigger');
    if (trigger) {
      const template = document.getElementById(trigger.getAttribute('href').slice(1));
      if (!template) return;
      event.preventDefault();
      lastFocused = trigger;
      open(template);
      return;
    }
    if (event.target.closest('[data-modal-close]')) close();
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && !modal.hidden) close();
  });
})();
