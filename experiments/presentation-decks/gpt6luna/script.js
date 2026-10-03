(() => {
  const slides = Array.from(document.querySelectorAll('.slide'));
  const currentSlideLabel = document.getElementById('current-slide');
  const totalSlideLabel = document.getElementById('total-slides');
  const currentTitleLabel = document.getElementById('current-title');
  const progressFill = document.getElementById('progress-fill');
  const previousButton = document.getElementById('previous-slide');
  const nextButton = document.getElementById('next-slide');

  if (!slides.length) return;

  document.documentElement.classList.add('js');
  totalSlideLabel.textContent = String(slides.length).padStart(2, '0');

  const initialIndex = slides.findIndex((slide) => `#${slide.id}` === window.location.hash);
  let activeIndex = initialIndex >= 0 ? initialIndex : 0;

  function setActiveSlide(index) {
    const nextIndex = Math.max(0, Math.min(slides.length - 1, index));
    activeIndex = nextIndex;

    slides.forEach((slide, slideIndex) => {
      const isActive = slideIndex === activeIndex;
      slide.classList.toggle('is-active', isActive);
      if (isActive) {
        document.body.dataset.tone = slide.dataset.tone || 'light';
      }
    });

    const activeSlide = slides[activeIndex];
    const heading = activeSlide.querySelector('h1, h2');
    currentSlideLabel.textContent = String(activeIndex + 1).padStart(2, '0');
    currentTitleLabel.textContent = heading
      ? `Slide ${activeIndex + 1}: ${heading.textContent.replace(/\s+/g, ' ').trim()}`
      : `Slide ${activeIndex + 1}`;
    progressFill.style.width = `${((activeIndex + 1) / slides.length) * 100}%`;
    previousButton.disabled = activeIndex === 0;
    nextButton.disabled = activeIndex === slides.length - 1;
  }

  function goToSlide(index) {
    const targetIndex = Math.max(0, Math.min(slides.length - 1, index));
    slides[targetIndex].scrollIntoView({
      behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth',
      block: 'start',
    });
    setActiveSlide(targetIndex);
  }

  previousButton.addEventListener('click', () => goToSlide(activeIndex - 1));
  nextButton.addEventListener('click', () => goToSlide(activeIndex + 1));

  document.addEventListener('keydown', (event) => {
    if (event.defaultPrevented || event.altKey || event.ctrlKey || event.metaKey) return;

    const target = event.target;
    if (target instanceof HTMLElement && target.closest('input, textarea, select, [contenteditable="true"], [role="textbox"]')) {
      return;
    }
    if ((event.key === ' ' || event.key === 'Enter') && target instanceof HTMLElement && target.closest('button, a')) {
      return;
    }

    let nextIndex = null;
    if (['ArrowDown', 'ArrowRight', 'PageDown', ' '].includes(event.key)) {
      nextIndex = activeIndex + 1;
    } else if (['ArrowUp', 'ArrowLeft', 'PageUp'].includes(event.key)) {
      nextIndex = activeIndex - 1;
    } else if (event.key === 'Home') {
      nextIndex = 0;
    } else if (event.key === 'End') {
      nextIndex = slides.length - 1;
    }

    if (nextIndex !== null) {
      event.preventDefault();
      goToSlide(nextIndex);
    }
  });

  setActiveSlide(activeIndex);

  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio);
        if (visible.length) {
          setActiveSlide(slides.indexOf(visible[0].target));
        }
      },
      { root: null, rootMargin: '-38% 0px -38% 0px', threshold: [0, 0.1, 0.35] },
    );
    slides.forEach((slide) => observer.observe(slide));
  } else {
    let scheduled = false;
    window.addEventListener('scroll', () => {
      if (scheduled) return;
      scheduled = true;
      window.requestAnimationFrame(() => {
        const viewportCenter = window.innerHeight / 2;
        const current = slides.findIndex((slide) => {
          const bounds = slide.getBoundingClientRect();
          return bounds.top <= viewportCenter && bounds.bottom > viewportCenter;
        });
        if (current >= 0) setActiveSlide(current);
        scheduled = false;
      });
    }, { passive: true });
  }
})();
