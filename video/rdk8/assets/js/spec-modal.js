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
