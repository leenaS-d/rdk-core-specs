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

(function () {
  const escapeHtml = (value) => {
    const node = document.createElement('div');
    node.textContent = value === null || value === undefined ? '' : String(value);
    return node.innerHTML;
  };

  const stripReleasePath = (value) => String(value).replace(/\/releases\/tag\/[^/]+\/?$/, '');

  const renderCell = (value, column) => {
    if (column.kind === 'link') {
      const url = column.strip ? stripReleasePath(value) : value;
      return `<td><a href="${escapeHtml(url)}" target="_blank" rel="noopener">${escapeHtml(url)}</a></td>`;
    }
    if (column.kind === 'pill') {
      return `<td><span class="pill">${escapeHtml(value)}</span></td>`;
    }
    if (column.kind === 'pill-variant') {
      const variant = String(value).toLowerCase() === 'optional' ? 'optional' : 'core';
      return `<td><span class="pill ${variant}">${escapeHtml(value)}</span></td>`;
    }
    return `<td>${escapeHtml(value)}</td>`;
  };

  document.querySelectorAll('script[type="application/json"][data-table]').forEach((node) => {
    const config = JSON.parse(node.textContent);
    const body = document.getElementById(`${config.id}-rows`);
    if (!body) return;
    const search = document.getElementById(`${config.id}-search`);
    const selects = Array.from(document.querySelectorAll('[data-filter-column]'));

    const render = () => {
      const query = search ? search.value.toLowerCase() : '';
      const rows = config.rows.filter((row) => {
        if (query && !row.join(' ').toLowerCase().includes(query)) return false;
        return selects.every((select) => !select.value || row[Number(select.dataset.filterColumn)] === select.value);
      });
      body.innerHTML = rows.length
        ? rows.map((row) => `<tr>${row.map((value, index) => renderCell(value, config.columns[index])).join('')}</tr>`).join('')
        : `<tr><td class="empty" colspan="${config.columns.length}">${escapeHtml(config.empty)}</td></tr>`;
    };

    if (search) search.addEventListener('input', render);
    selects.forEach((select) => select.addEventListener('input', render));
    render();
  });
})();
