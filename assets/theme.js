(() => {
  const root = document.documentElement;
  const button = document.getElementById('theme-toggle');
  // Storage may be unavailable in private or restricted browser contexts.
  try { if (localStorage.getItem('cypher-theme') === 'light') root.dataset.theme = 'light'; } catch {}
  function update() {
    const next = root.dataset.theme === 'dark' ? 'light' : 'dark';
    button.textContent = next === 'light' ? 'Light' : 'Dark';
    button.setAttribute('aria-label', `Switch to ${next} theme`);
  }
  button.hidden = false;
  update();
  button.addEventListener('click', () => {
    root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
    try { localStorage.setItem('cypher-theme', root.dataset.theme); } catch {}
    update();
  });
})();
