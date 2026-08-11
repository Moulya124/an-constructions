/**
 * include.js
 * Fetches partials/header.html and partials/footer.html and injects them
 * into any element with [data-include="header"] / [data-include="footer"].
 *
 * NOTE: fetch() of local files requires a real HTTP server (Live Server,
 * `npx serve`, etc.) — it will not work opening index.html directly via
 * file:// due to browser CORS restrictions on fetch.
 */
(function () {
  async function loadInclude(el) {
    const name = el.getAttribute('data-include');
    const path = `/partials/${name}.html`;
    try {
      const res = await fetch(path);
      if (!res.ok) throw new Error(`Failed to load ${path}: ${res.status}`);
      el.innerHTML = await res.text();
    } catch (err) {
      console.error(err);
      el.innerHTML = `<!-- could not load ${name} partial -->`;
    }
  }

  function highlightActiveNav() {
    const current = document.body.getAttribute('data-page');
    if (!current) return;
    document.querySelectorAll('nav.links a[data-nav]').forEach((link) => {
      if (link.getAttribute('data-nav') === current) {
        link.classList.add('active');
      }
    });
  }

  function initMobileNav() {
    const toggle = document.getElementById('nav-toggle');
    const links = document.getElementById('nav-links');
    if (!toggle || !links) return;

    toggle.addEventListener('click', (e) => {
      e.stopPropagation();
      const isOpen = links.classList.toggle('open');
      toggle.setAttribute('aria-expanded', String(isOpen));
    });

    document.addEventListener('click', (e) => {
      if (links.classList.contains('open') && !links.contains(e.target) && !toggle.contains(e.target)) {
        links.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });

    links.querySelectorAll('a').forEach((link) => {
      link.addEventListener('click', () => {
        links.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  document.addEventListener('DOMContentLoaded', async () => {
    const includes = Array.from(document.querySelectorAll('[data-include]'));
    await Promise.all(includes.map(loadInclude));
    highlightActiveNav();
    initMobileNav();
  });
})();
