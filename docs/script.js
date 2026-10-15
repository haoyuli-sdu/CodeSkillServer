const tabs = document.querySelectorAll('.result-tab');
const panels = document.querySelectorAll('.result-panel');

tabs.forEach((tab) => {
  tab.addEventListener('click', () => {
    tabs.forEach((item) => {
      item.classList.remove('active');
      item.setAttribute('aria-selected', 'false');
    });
    panels.forEach((panel) => panel.classList.remove('active'));
    tab.classList.add('active');
    tab.setAttribute('aria-selected', 'true');
    document.getElementById(tab.dataset.target).classList.add('active');
  });
});

const toTop = document.getElementById('toTop');
window.addEventListener('scroll', () => {
  toTop.classList.toggle('visible', window.scrollY > 700);
}, { passive: true });
toTop.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));

// Paper-specific floating retrieval companion: appears at Abstract and leans with scroll direction.
const scrollSkillGuide = document.getElementById('scrollSkillGuide');
const abstractSection = document.getElementById('abstract');
if (scrollSkillGuide && abstractSection) {
  let lastScrollY = window.scrollY;
  let settleTimer = 0;
  let guideTicking = false;
  const updateScrollGuide = () => {
    const currentScrollY = window.scrollY;
    const abstractStart = abstractSection.offsetTop - window.innerHeight * 0.44;
    const visible = currentScrollY >= abstractStart;
    scrollSkillGuide.classList.toggle('is-visible', visible);
    scrollSkillGuide.setAttribute('aria-hidden', String(!visible));
    const delta = currentScrollY - lastScrollY;
    if (visible && Math.abs(delta) > 1) {
      scrollSkillGuide.classList.remove('scroll-up', 'scroll-down', 'is-settling');
      scrollSkillGuide.classList.add(delta > 0 ? 'scroll-down' : 'scroll-up');
      window.clearTimeout(settleTimer);
      settleTimer = window.setTimeout(() => {
        scrollSkillGuide.classList.remove('scroll-up', 'scroll-down');
        scrollSkillGuide.classList.add('is-settling');
      }, 150);
    }
    lastScrollY = currentScrollY;
    guideTicking = false;
  };
  window.addEventListener('scroll', () => {
    if (!guideTicking) {
      window.requestAnimationFrame(updateScrollGuide);
      guideTicking = true;
    }
  }, { passive: true });
  window.addEventListener('resize', updateScrollGuide, { passive: true });
  updateScrollGuide();
}

const corpusLayout = document.querySelector('.corpus-layout');
if (corpusLayout) {
  corpusLayout.classList.add('corpus-reveal-ready');
  const corpusObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('corpus-visible');
      observer.unobserve(entry.target);
    });
  }, { threshold: 0.28 });
  corpusObserver.observe(corpusLayout);
}

const copyButton = document.getElementById('copyBib');
copyButton.addEventListener('click', async () => {
  await navigator.clipboard.writeText(document.getElementById('bib').innerText);
  copyButton.textContent = 'Copied';
  window.setTimeout(() => { copyButton.textContent = 'Copy BibTeX'; }, 1600);
});

// Constellation field behind the semantic SkillServer cards.
const constellation = document.getElementById('skillConstellation');
if (constellation) {
  const context = constellation.getContext('2d');
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  let points = [];
  let width = 0;
  let height = 0;
  let frame = 0;
  const pointer = { x: -1000, y: -1000 };
  let cardAnchors = [];

  const resizeConstellation = () => {
    const rect = constellation.getBoundingClientRect();
    const ratio = Math.min(window.devicePixelRatio || 1, 1.5);
    width = rect.width;
    height = rect.height;
    constellation.width = Math.max(1, Math.floor(width * ratio));
    constellation.height = Math.max(1, Math.floor(height * ratio));
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    const count = width < 600 ? 34 : width < 900 ? 52 : 85;
    points = Array.from({ length: count }, (_, index) => ({
      x: Math.random() * width, y: Math.random() * height,
      vx: (Math.random() - 0.5) * 0.62,
      vy: (Math.random() - 0.5) * 0.62,
      radius: 1.5 + Math.random() * 2.2,
      phase: Math.random() * Math.PI * 2,
      accent: index % 7 === 0,
    }));

    const universe = constellation.parentElement;
    const cards = Array.from(universe.querySelectorAll('.skill-card'));
    const used = new Set();
    cardAnchors = cards.map((card) => {
      const cardRect = card.getBoundingClientRect();
      const universeRect = universe.getBoundingClientRect();
      const targetX = cardRect.left - universeRect.left + cardRect.width / 2;
      const targetY = cardRect.top - universeRect.top + cardRect.height / 2;
      let bestIndex = 0;
      let bestDistance = Number.POSITIVE_INFINITY;
      points.forEach((point, index) => {
        if (used.has(index)) return;
        const distance = Math.hypot(point.x - targetX, point.y - targetY);
        if (distance < bestDistance) { bestDistance = distance; bestIndex = index; }
      });
      used.add(bestIndex);
      card.classList.add('network-follow');
      card.style.setProperty('translate', '0px 0px');
      return { card, point: points[bestIndex], baseX: points[bestIndex].x, baseY: points[bestIndex].y };
    });
  };

  const drawConstellation = (time) => {
    context.clearRect(0, 0, width, height);
    const linkDistance = width < 600 ? 120 : 160;
    const now = reduceMotion.matches ? 0 : time;
    points.forEach((point, index) => {
      if (!reduceMotion.matches) {
        point.x += point.vx; point.y += point.vy;
        if (point.x < 0 || point.x > width) point.vx *= -1;
        if (point.y < 0 || point.y > height) point.vy *= -1;
        const pointerDistance = Math.hypot(point.x - pointer.x, point.y - pointer.y);
        if (pointerDistance < 220) {
          point.x -= (point.x - pointer.x) * 0.005;
          point.y -= (point.y - pointer.y) * 0.005;
        }
      }
      point.renderX = point.x; point.renderY = point.y;
      for (let next = index + 1; next < points.length; next += 1) {
        const other = points[next];
        const dx = point.renderX - other.renderX;
        const dy = point.renderY - other.renderY;
        const distance = Math.hypot(dx, dy);
        if (distance < linkDistance) {
          const opacity = (1 - distance / linkDistance) * 0.36;
          context.beginPath(); context.moveTo(point.renderX, point.renderY); context.lineTo(other.renderX, other.renderY);
          context.strokeStyle = 'rgba(170, 246, 236, ' + opacity + ')';
          context.lineWidth = point.accent || other.accent ? 1.15 : 0.7;
          context.stroke();
        }
      }
    });
    cardAnchors.forEach(({ card, point, baseX, baseY }) => {
      const followX = Math.max(-58, Math.min(58, (point.x - baseX) * 0.52));
      const followY = Math.max(-44, Math.min(44, (point.y - baseY) * 0.52));
      card.style.setProperty('--follow-x', followX.toFixed(1) + 'px');
      card.style.setProperty('--follow-y', followY.toFixed(1) + 'px');
    });
    points.forEach((point) => {
      const pulse = 0.62 + Math.sin(now * 0.002 + point.phase) * 0.2;
      context.beginPath();
      context.arc(point.renderX, point.renderY, point.radius * (point.accent ? 1.5 : 1), 0, Math.PI * 2);
      context.fillStyle = point.accent ? 'rgba(208, 255, 151, ' + pulse + ')' : 'rgba(174, 250, 239, ' + (pulse * 0.7) + ')';
      context.shadowColor = point.accent ? '#d3ff9b' : '#9af3df';
      context.shadowBlur = point.accent ? 12 : 6;
      context.fill(); context.shadowBlur = 0;
    });
    if (!reduceMotion.matches) frame = window.requestAnimationFrame(drawConstellation);
  };

  resizeConstellation();
  window.addEventListener('resize', resizeConstellation, { passive: true });
  constellation.parentElement.addEventListener('pointermove', (event) => {
    const rect = constellation.getBoundingClientRect();
    pointer.x = event.clientX - rect.left; pointer.y = event.clientY - rect.top;
  }, { passive: true });
  constellation.parentElement.addEventListener('pointerleave', () => { pointer.x = -1000; pointer.y = -1000; });
  if (reduceMotion.matches) drawConstellation(0);
  else frame = window.requestAnimationFrame(drawConstellation);
  if (reduceMotion.addEventListener) reduceMotion.addEventListener('change', () => {
    window.cancelAnimationFrame(frame); drawConstellation(0);
    if (!reduceMotion.matches) frame = window.requestAnimationFrame(drawConstellation);
  });
}
