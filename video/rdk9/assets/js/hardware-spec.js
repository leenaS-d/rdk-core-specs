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

/* Opens the matching Markdown section in the hardware specification dialog. */
(function () {
  const content = document.querySelector('.hardware-spec');
  const modal = document.getElementById('hardware-spec-modal');
  const body = document.getElementById('hardware-spec-modal-body');
  if (!content || !modal || !body) return;

  const isHeading = (element) => /^H[1-6]$/.test(element.tagName);
  const sourceSections = Array.from(content.children);
  const referenceSections = {
    'Memory (RAM)': 'Reference memory measurements',
    'Storage (Flash)': 'Reference',
  };
  const matrixStart = sourceSections.findIndex((element) =>
    isHeading(element) && element.textContent.trim() === 'Hardware Compatibility Baseline Specification Matrix'
  );
  const matrixEnd = sourceSections.findIndex((element, index) => index > matrixStart && isHeading(element));
  if (matrixStart >= 0 && matrixEnd >= 0) {
    sourceSections.forEach((element, index) => {
      if (index >= matrixEnd) {
        element.classList.add('hardware-hidden-source');
      }
    });
  }

  /* Find the heading that introduces a given anchor id (walks backwards to the
     nearest preceding heading, same rule used when opening a modal). */
  const findHeadingFor = (anchorId) => {
    const anchor = document.getElementById(anchorId);
    if (!anchor) return null;
    let node = anchor.parentElement;
    while (node && !isHeading(node)) node = node.previousElementSibling;
    return node;
  };

  /* Each matrix row's "View Details" link marks the start of a real top-level
     section. Some sections (e.g. Network Connectivity) contain their own
     sub-headings (Wi-Fi, Ethernet, ...) at the same heading level, so the
     modal must only stop at one of these known section-start headings -
     not at every heading it happens to encounter. */
  const sectionHeadings = new Set();
  if (matrixStart >= 0 && matrixEnd >= 0) {
    sourceSections.slice(matrixStart, matrixEnd).forEach((section) => {
      section.querySelectorAll('a[href^="#"]').forEach((link) => {
        if (link.textContent.trim().toLowerCase() !== 'view details') return;
        const heading = findHeadingFor(decodeURIComponent(link.hash.slice(1)));
        if (heading) sectionHeadings.add(heading);
      });
    });
  }

  let lastFocused = null;

  const close = () => {
    modal.hidden = true;
    modal.classList.remove('open');
    body.innerHTML = '';
    if (lastFocused) lastFocused.focus();
  };

  const appendReferences = (sectionHeading) => {
    const referenceHeading = referenceSections[sectionHeading.textContent.trim()];
    if (!referenceHeading) return;

    const start = sourceSections.findIndex((element) =>
      isHeading(element) && element.textContent.trim().toLowerCase() === referenceHeading.toLowerCase()
    );
    if (start < 0) return;
    const nextHeading = sourceSections.findIndex((element, index) => index > start && isHeading(element));
    const end = nextHeading < 0 ? sourceSections.length : nextHeading;
    const list = sourceSections.slice(start + 1, end).find((element) => element.tagName === 'UL');
    if (!list) return;

    const headingClone = sourceSections[start].cloneNode(true);
    headingClone.classList.remove('hardware-hidden-source');
    body.appendChild(headingClone);

    Array.from(list.children).forEach((item) => {
      const reference = item.querySelector('a[href^="#"]');
      if (!reference) return;

      const targetId = decodeURIComponent(reference.hash.slice(1));
      const targetAnchor = document.getElementById(targetId);
      if (!targetAnchor) return;
      const targetIndex = sourceSections.findIndex((element) => element.contains(targetAnchor));
      if (targetIndex < 0) return;
      let appendixStart = targetIndex;
      while (appendixStart >= 0 && !isHeading(sourceSections[appendixStart])) appendixStart -= 1;
      if (appendixStart < 0) return;
      const appendixHeading = sourceSections[appendixStart];
      const appendixNext = sourceSections.findIndex((element, index) => index > appendixStart && isHeading(element));
      const appendixEnd = appendixNext < 0 ? sourceSections.length : appendixNext;

      const details = document.createElement('details');
      details.className = 'hardware-appendix-reference';
      const summary = document.createElement('summary');
      summary.textContent = reference.textContent.trim();
      summary.addEventListener('click', () => {
        if (!details.open) {
          body.querySelectorAll('.hardware-appendix-reference[open]').forEach((other) => {
            if (other !== details) other.open = false;
          });
        }
      });
      details.appendChild(summary);

      const appendixContent = document.createElement('div');
      appendixContent.className = 'hardware-appendix-content';
      for (let index = appendixStart; index < appendixEnd; index += 1) {
        if (sourceSections[index].tagName === 'HR') continue;
        const clone = sourceSections[index].cloneNode(true);
        clone.classList.remove('hardware-hidden-source');
        if (clone.id) clone.removeAttribute('id');
        clone.querySelectorAll('[id]').forEach((element) => element.removeAttribute('id'));
        appendixContent.appendChild(clone);
      }
      details.appendChild(appendixContent);
      body.appendChild(details);
    });
  };

  const open = (trigger, target) => {
    let heading = target.parentElement;
    while (heading && !isHeading(heading)) heading = heading.previousElementSibling;
    if (!heading) return;

    const isRegulatorySection = heading.textContent.trim() === 'Regulatory and Certification Requirements';
    const referenceHeading = referenceSections[heading.textContent.trim()];
    body.innerHTML = '';
    let current = heading;
    while (current && (current === heading || !sectionHeadings.has(current))) {
      if (isRegulatorySection && current !== heading && isHeading(current) &&
        /^Appendix\b/i.test(current.textContent.trim())) {
        break;
      }

      const next = current.nextElementSibling;
      const isReferenceHeading = referenceHeading && isHeading(current) &&
        current.textContent.trim().toLowerCase() === referenceHeading.toLowerCase();
      const isReferenceList = referenceHeading && current.tagName === 'UL' &&
        current.previousElementSibling &&
        isHeading(current.previousElementSibling) &&
        current.previousElementSibling.textContent.trim().toLowerCase() === referenceHeading.toLowerCase();
      if (!(isReferenceHeading || isReferenceList)) {
        const clone = current.cloneNode(true);
        clone.classList.remove('hardware-hidden-source');
        body.appendChild(clone);
      }
      current = next;
    }
    appendReferences(heading);
    body.querySelectorAll('[id]').forEach((element) => element.removeAttribute('id'));
    const title = body.querySelector('h1, h2, h3, h4, h5, h6');
    if (title) title.id = 'hardware-spec-modal-title';
    const dialog = modal.querySelector('[role="dialog"]');
    if (title) {
      dialog.setAttribute('aria-labelledby', title.id);
      dialog.removeAttribute('aria-label');
    }

    lastFocused = trigger;
    modal.hidden = false;
    modal.classList.add('open');
    modal.querySelector('.spec-modal-close').focus();
  };

  document.addEventListener('click', (event) => {
    const trigger = event.target.closest('.hardware-spec a[href^="#"]');
    if (trigger && trigger.textContent.trim().toLowerCase() === 'view details') {
      const target = document.getElementById(decodeURIComponent(trigger.hash.slice(1)));
      if (!target) return;
      event.preventDefault();
      open(trigger, target);
      return;
    }
    if (event.target.closest('[data-hardware-modal-close]')) close();
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && !modal.hidden) close();
  });
})();
