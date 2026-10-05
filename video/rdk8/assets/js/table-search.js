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
      const variant = String(value).toLowerCase() === 'non-core' ? 'non-core' : 'core';
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
