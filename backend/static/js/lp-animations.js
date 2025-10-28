(function () {
  const init = () => {
    const elements = document.querySelectorAll('[data-lp-anim]');
    if (!elements.length) {
      return;
    }

    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    const assignDelay = (el, index) => {
      if (el.style.getPropertyValue('--lp-anim-delay')) {
        return;
      }
      const explicit = el.dataset.lpAnimDelay;
      if (explicit) {
        el.style.setProperty('--lp-anim-delay', `${explicit}`.endsWith('ms') ? explicit : `${explicit}ms`);
        return;
      }
      const step = Number(el.dataset.lpAnimStep || 120);
      const seq = Number(el.dataset.lpAnimSeq ?? index);
      if (!Number.isNaN(seq)) {
        el.style.setProperty('--lp-anim-delay', `${Math.max(0, seq) * step}ms`);
      }
    };

    elements.forEach(assignDelay);

    if (prefersReduced) {
      elements.forEach((el) => el.classList.add('is-visible'));
      return;
    }

    const reveal = (el) => {
      if (el.classList.contains('is-visible')) {
        return;
      }
      requestAnimationFrame(() => el.classList.add('is-visible'));
    };

    if (!('IntersectionObserver' in window)) {
      elements.forEach((el, index) => {
        const delay = parseInt(el.style.getPropertyValue('--lp-anim-delay') || '0', 10);
        setTimeout(() => reveal(el), delay || index * 120);
      });
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            reveal(entry.target);
            observer.unobserve(entry.target);
          }
        });
      },
      {
        rootMargin: '0px 0px -10% 0px',
        threshold: 0.15
      }
    );

    elements.forEach((el) => {
      observer.observe(el);
      const rect = el.getBoundingClientRect();
      if (rect.top < window.innerHeight * 0.8) {
        reveal(el);
      }
    });
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
