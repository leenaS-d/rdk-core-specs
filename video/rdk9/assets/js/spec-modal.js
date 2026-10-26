/*
 If not stated otherwise in this file or this component's LICENSE file the
 following copyright and licenses apply:

 Copyright 2026 RDK Management

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

 http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
*/

// Opens a row's detail <template> in the shared dialog.
(function () {
  const modal = document.getElementById('spec-modal');
  const body = document.getElementById('spec-modal-body');
  const dialog = modal && modal.querySelector('.spec-modal-dialog');
  if (!modal || !body || !dialog) return;

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
    const heading = body.querySelector('h1, h2, h3');
    if (heading) {
      heading.id = 'spec-modal-title';
      dialog.setAttribute('aria-labelledby', heading.id);
      dialog.removeAttribute('aria-label');
    } else {
      dialog.removeAttribute('aria-labelledby');
      dialog.setAttribute('aria-label', 'Specification details');
    }
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
    if (modal.hidden) return;
    if (event.key === 'Escape') {
      close();
      return;
    }
    if (event.key !== 'Tab') return;

    const focusable = Array.from(dialog.querySelectorAll('a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'))
      .filter((element) => element.getClientRects().length);
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (!first || !last) return;

    if (event.shiftKey && (document.activeElement === first || !dialog.contains(document.activeElement))) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && (document.activeElement === last || !dialog.contains(document.activeElement))) {
      event.preventDefault();
      first.focus();
    }
  });
})();
