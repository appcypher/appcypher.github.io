(() => {
  const root = document.documentElement;
  const MOON = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a8.5 8.5 0 1 0 10.5 10.5z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>';
  const SUN = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M4.9 19.1L7 17M17 7l2.1-2.1" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>';

  // Theme toggle. The current theme is already applied by the inline script in <head>, so there is no flash.
  const button = document.getElementById('theme-toggle');
  if (button) {
    const update = () => {
      const dark = root.dataset.theme !== 'light';
      button.querySelector('.tog-icon').innerHTML = dark ? MOON : SUN;
      button.querySelector('.tog-label').textContent = dark ? 'dark' : 'light';
      button.setAttribute('aria-label', `Switch to ${dark ? 'light' : 'dark'} theme`);
      const meta = document.querySelector('meta[name="theme-color"]');
      if (meta) meta.content = dark ? '#17160f' : '#d2c79d';
    };
    button.hidden = false;
    update();
    button.addEventListener('click', () => {
      root.dataset.theme = root.dataset.theme === 'light' ? 'dark' : 'light';
      // Storage may be unavailable in private or restricted browser contexts.
      try { localStorage.setItem('cypher-theme', root.dataset.theme); } catch {}
      update();
    });
  }

  // Mobile nav.
  const menu = document.getElementById('menu-toggle');
  const rail = document.getElementById('rail');
  if (menu && rail) {
    menu.addEventListener('click', () => {
      const open = rail.classList.toggle('open');
      menu.setAttribute('aria-expanded', String(open));
    });
  }

  // Prose conventions that plain Markdown can't express.
  const prose = document.querySelector('.prose');
  if (!prose) return;

  // A blockquote whose text starts with "note:" becomes a sticky note.
  prose.querySelectorAll('blockquote').forEach((q) => {
    const p = q.querySelector('p');
    if (p && /^note:\s*/i.test(p.textContent)) {
      q.classList.add('note');
      const first = p.firstChild;
      if (first && first.nodeType === Node.TEXT_NODE) first.textContent = first.textContent.replace(/^note:\s*/i, '');
    }
  });

  // :key: / :alice: tokens become inline glyphs. The sprite is fetched only when a page uses one.
  const re = /:([a-z][a-z0-9-]*):/g;
  const walker = document.createTreeWalker(prose, NodeFilter.SHOW_TEXT, {
    acceptNode: (n) => (n.parentElement.closest('code, pre, .bubble, .aside') ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT),
  });
  const nodes = [];
  while (walker.nextNode()) if (re.test(walker.currentNode.textContent)) nodes.push(walker.currentNode);
  if (!nodes.length) return;
  fetch(document.body.dataset.glyphs).then((r) => r.text()).then((svgText) => {
    const holder = document.createElement('div');
    holder.hidden = true;
    holder.innerHTML = svgText;
    document.body.appendChild(holder);
    const glyphs = new Set(Array.from(holder.querySelectorAll('symbol[id^="g-"]')).map((s) => s.id.slice(2)));
    nodes.forEach((node) => {
      const frag = document.createDocumentFragment();
      let last = 0;
      node.textContent.replace(re, (m, name, i) => {
        if (!glyphs.has(name)) return m;
        frag.appendChild(document.createTextNode(node.textContent.slice(last, i)));
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('class', 'glyph');
        svg.setAttribute('aria-label', name);
        svg.setAttribute('role', 'img');
        const use = document.createElementNS('http://www.w3.org/2000/svg', 'use');
        use.setAttribute('href', `#g-${name}`);
        svg.appendChild(use);
        frag.appendChild(svg);
        last = i + m.length;
        return m;
      });
      frag.appendChild(document.createTextNode(node.textContent.slice(last)));
      node.parentNode.replaceChild(frag, node);
    });
  }).catch(() => {});
})();
