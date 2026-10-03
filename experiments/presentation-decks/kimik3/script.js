/* Deck navigation: scroll-snap + keyboard + progress HUD */
(function () {
  const deck    = document.querySelector('.deck');
  const slides  = Array.from(deck.querySelectorAll('.slide'));
  const counter = document.querySelector('[data-counter]');
  const bar     = document.querySelector('[data-progress]');
  const hint    = document.querySelector('[data-hint]');
  const reduce  = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let current = -1;

  function setActive(i) {
    if (i === current) return;
    current = i;
    slides.forEach((s, idx) => s.classList.toggle('active', idx === i));
    counter.textContent = String(i + 1).padStart(2, '0') + ' / ' + String(slides.length).padStart(2, '0');
    bar.style.width = (slides.length > 1 ? (i / (slides.length - 1)) * 100 : 100) + '%';
    hint.classList.toggle('hidden', i !== 0);
    history.replaceState(null, '', '#' + (i + 1));
  }

  const io = new IntersectionObserver((entries) => {
    entries.forEach((en) => {
      if (en.isIntersecting) setActive(slides.indexOf(en.target));
    });
  }, { root: deck, threshold: 0.55 });
  slides.forEach((s) => io.observe(s));

  function goTo(i) {
    const n = Math.max(0, Math.min(slides.length - 1, i));
    deck.scrollTo({ top: slides[n].offsetTop, behavior: reduce ? 'auto' : 'smooth' });
  }

  window.addEventListener('keydown', (e) => {
    if (e.target.closest('a, button, input, textarea, select')) return;
    switch (e.key) {
      case 'ArrowDown':
      case 'PageDown':
        e.preventDefault(); goTo(current + 1); break;
      case 'ArrowUp':
      case 'PageUp':
        e.preventDefault(); goTo(current - 1); break;
      case ' ':
        e.preventDefault(); goTo(e.shiftKey ? current - 1 : current + 1); break;
      case 'Home':
        e.preventDefault(); goTo(0); break;
      case 'End':
        e.preventDefault(); goTo(slides.length - 1); break;
    }
  });

  // Deep link on load (#1 … #12)
  const h = parseInt(location.hash.replace('#', ''), 10);
  const start = h >= 1 && h <= slides.length ? h - 1 : 0;
  deck.scrollTo({ top: slides[start].offsetTop, behavior: 'auto' });
  setActive(start);
})();
