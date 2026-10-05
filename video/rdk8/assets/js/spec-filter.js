// Filters a server-rendered spec table from its toolbar.
// Rows stay in the DOM so the page works without JS; this only hides them.
(function () {
  document.querySelectorAll('[data-filter-for]').forEach((toolbar) => {
    const table = document.getElementById(toolbar.dataset.filterFor);
    if (!table) return;

    const search = toolbar.querySelector('[data-filter-search]');
    const selects = Array.from(toolbar.querySelectorAll('[data-filter-column]'));
    const rows = Array.from(table.querySelectorAll('tbody tr'));

    const apply = () => {
      const query = (search ? search.value : '').trim().toLowerCase();
      let visible = 0;
      rows.forEach((row) => {
        const cells = row.querySelectorAll('td');
        const matchesQuery = !query || row.textContent.toLowerCase().includes(query);
        const matchesFilters = selects.every((select) => {
          if (!select.value) return true;
          const cell = cells[Number(select.dataset.filterColumn)];
          return cell && cell.textContent.trim() === select.value;
        });
        const show = matchesQuery && matchesFilters;
        row.hidden = !show;
        if (show) visible += 1;
      });

      let empty = table.querySelector('tr[data-empty-row]');
      if (!visible) {
        if (!empty) {
          empty = document.createElement('tr');
          empty.setAttribute('data-empty-row', '');
          const cell = document.createElement('td');
          cell.colSpan = table.querySelectorAll('thead th').length || 1;
          cell.className = 'empty';
          cell.textContent = 'No matching records.';
          empty.appendChild(cell);
          table.querySelector('tbody').appendChild(empty);
        }
        empty.hidden = false;
      } else if (empty) {
        empty.hidden = true;
      }
    };

    if (search) search.addEventListener('input', apply);
    selects.forEach((select) => select.addEventListener('change', apply));
    apply();
  });
})();
