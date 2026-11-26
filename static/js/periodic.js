/* Periodic table interactions + Bohr model */
(function () {
  const table = document.getElementById('ptable');
  if (table) {
    const info = document.getElementById('ptInfo');
    const els = [...table.querySelectorAll('.el')];
    const show = el => {
      const d = el.dataset;
      info.innerHTML = '<div class="pt-big cat-' + d.cat + '"><small>' + d.number + '</small>' + CV.esc(d.symbol) + '</div>' +
        '<div><h3 class="h5 mb-1">' + CV.esc(d.name) + '</h3><p class="text-secondary">' + CV.esc(d.catlabel) + '</p>' +
        '<p>Atomic mass <b>' + CV.esc(d.mass) + '</b> · Group <b>' + CV.esc(d.group) + '</b> · Period <b>' + d.period + '</b></p>' +
        '<p>State at 25 °C: <b>' + CV.esc(d.phase) + '</b></p></div>';
    };
    els.forEach(el => { el.addEventListener('mouseenter', () => show(el)); el.addEventListener('focus', () => show(el)); });

    let cat = 'all';
    const search = document.getElementById('ptSearch');
    const apply = () => {
      const q = (search && search.value || '').trim().toLowerCase();
      els.forEach(el => {
        const d = el.dataset;
        const okCat = cat === 'all' || d.cat === cat;
        const okQ = !q || d.name.toLowerCase().includes(q) || d.symbol.toLowerCase() === q || d.number === q;
        el.classList.toggle('dim', !(okCat && okQ));
      });
    };
    document.querySelectorAll('.legend [data-cat]').forEach(b => b.addEventListener('click', () => {
      document.querySelectorAll('.legend [data-cat]').forEach(x => x.classList.remove('active'));
      b.classList.add('active'); cat = b.dataset.cat; apply();
    }));
    if (search) search.addEventListener('input', apply);
    apply();
  }

  const cv = document.getElementById('bohr');
  if (cv) {
    const ctx = cv.getContext('2d');
    const shells = cv.dataset.shells.split(',').map(Number);
    const cx = cv.width / 2, cy = cv.height / 2, step = Math.min(20, (cv.width / 2 - 34) / shells.length);
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    let t = 0;
    (function frame() {
      ctx.clearRect(0, 0, cv.width, cv.height);
      const g = ctx.createRadialGradient(cx - 6, cy - 6, 2, cx, cy, 22);
      g.addColorStop(0, '#a5f3fc'); g.addColorStop(1, '#7c3aed');
      ctx.fillStyle = g; ctx.beginPath(); ctx.arc(cx, cy, 22, 0, 7); ctx.fill();
      ctx.fillStyle = '#fff'; ctx.font = 'bold 15px Sora, sans-serif'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      ctx.fillText(cv.dataset.symbol, cx, cy);
      shells.forEach((n, i) => {
        const r = 34 + (i + 1) * step;
        ctx.strokeStyle = 'rgba(148,163,255,.3)'; ctx.beginPath(); ctx.arc(cx, cy, r, 0, 7); ctx.stroke();
        for (let k = 0; k < n; k++) {
          const a = (k / n) * Math.PI * 2 + t * (0.7 / (i + 1));
          ctx.fillStyle = '#22d3ee'; ctx.beginPath(); ctx.arc(cx + r * Math.cos(a), cy + r * Math.sin(a), 3.4, 0, 7); ctx.fill();
        }
      });
      t += 0.02;
      if (!reduce) requestAnimationFrame(frame);
    })();
  }
})();
