// Scroll reveal — skipped entirely when the user prefers reduced motion.
(function () {
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var items = document.querySelectorAll('.reveal');
  if (reduced || !('IntersectionObserver' in window)) {
    items.forEach(function (el) { el.classList.add('visible'); });
    return;
  }
  var observer = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    },
    { rootMargin: '0px 0px -8% 0px', threshold: 0.05 }
  );
  items.forEach(function (el) { observer.observe(el); });
})();

// Touch devices get no hover — play each card's terminal motion as it
// scrolls into view instead (replays on re-entry).
(function () {
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var noHover = window.matchMedia('(hover: none)').matches;
  var cards = document.querySelectorAll('.proj');
  if (reduced || !noHover || !cards.length || !('IntersectionObserver' in window)) return;
  var observer = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('play');
        } else {
          entry.target.classList.remove('play');
        }
      });
    },
    { rootMargin: '-10% 0px -10% 0px', threshold: 0.3 }
  );
  cards.forEach(function (c) { observer.observe(c); });
})();

// Colophon year
document.querySelectorAll('[data-year]').forEach(function (el) {
  el.textContent = new Date().getFullYear();
});
