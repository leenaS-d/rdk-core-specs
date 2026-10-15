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

// Floating site-wide search chatbox. Lazily fetches assets/data/search-index.json
// (generated at build time by build.py) and does a simple client-side keyword
// match, same approach as the RDK-B Core Broadband search chatbox.
(function () {
  const toggle = document.getElementById('chatbox-toggle');
  const panel = document.getElementById('chatbox-panel');
  const closeBtn = document.getElementById('chatbox-close');
  const form = document.getElementById('chatbox-form');
  const input = document.getElementById('chatbox-input');
  const body = document.getElementById('chatbox-body');
  if (!toggle || !panel || !form || !input || !body) return;

  let searchDocs = null;

  function esc(value) {
    const node = document.createElement('div');
    node.textContent = value ?? '';
    return node.innerHTML;
  }

  function score(doc, terms) {
    const title = doc.title.toLowerCase();
    const text = doc.text.toLowerCase();
    let total = 0;
    for (const term of terms) {
      if (title.includes(term)) total += 10;
      if (text.includes(term)) total += 2;
    }
    return total;
  }

  function renderResults(query, terms) {
    const scored = searchDocs
      .map((doc) => ({ doc, s: score(doc, terms) }))
      .filter((entry) => entry.s > 0)
      .sort((a, b) => b.s - a.s);

    if (!scored.length) {
      body.innerHTML = '<div class="chatbox-welcome">No matches for "' + esc(query) +
        '". Try a different term — module names, method names, or words like "intent" or "component" work well.</div>';
      return;
    }

    const best = scored[0].doc;
    const rest = scored.slice(1, 6);

    let html = '<div class="chatbox-answer">' +
      '<div class="cb-cat">' + esc(best.category) + '</div>' +
      '<div class="cb-title">' + esc(best.title) + '</div>' +
      '<div class="cb-text">' + esc(best.text) + '</div>' +
      '</div>';

    if (rest.length) {
      html += '<div class="chatbox-related">Related</div>';
      html += rest.map((entry) =>
        '<a class="chatbox-result" href="' + esc(entry.doc.url) + '">' +
        '<div class="cb-r-title">' + esc(entry.doc.title) + '</div>' +
        '<div class="cb-r-cat">' + esc(entry.doc.category) + '</div>' +
        '</a>'
      ).join('');
    }
    body.innerHTML = html;
  }

  function runSearch(query) {
    const terms = query.toLowerCase().split(/\s+/).filter(Boolean);
    if (!terms.length) return;

    if (!searchDocs) {
      body.innerHTML = '<div class="chatbox-welcome">Loading search index…</div>';
      fetch('assets/data/search-index.json', { cache: 'no-store' })
        .then((response) => {
          if (!response.ok) throw new Error('HTTP ' + response.status);
          return response.json();
        })
        .then((data) => {
          searchDocs = data.docs;
          renderResults(query, terms);
        })
        .catch((err) => {
          body.innerHTML = '<div class="chatbox-welcome">Could not load the search index (' + esc(err.message) + ').</div>';
        });
      return;
    }
    renderResults(query, terms);
  }

  toggle.addEventListener('click', () => {
    panel.classList.toggle('open');
    if (panel.classList.contains('open')) input.focus();
  });
  if (closeBtn) closeBtn.addEventListener('click', () => panel.classList.remove('open'));
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    if (input.value.trim()) runSearch(input.value.trim());
  });
})();
