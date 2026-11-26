/* CHEMVERSE Structure Lab – 2D molecule editor on <canvas> */
(function () {
  const COLOR = { H: '#e5e7eb', C: '#334155', N: '#3b82f6', O: '#ef4444', S: '#eab308', P: '#f97316', F: '#4ade80', Cl: '#22c55e',
    Br: '#b45309', I: '#9333ea', B: '#fda4af', Si: '#d6b98c', Na: '#a78bfa', Mg: '#84cc16' };
  const DARK_TEXT = ['H', 'S', 'F', 'B', 'Si', 'Mg'];
  const R = 18;

  function drawMol(ctx, atoms, bonds, opts) {
    const o = Object.assign({ scale: 1, ox: 0, oy: 0, grid: false, w: ctx.canvas.width, h: ctx.canvas.height, valence: {} }, opts || {});
    ctx.clearRect(0, 0, o.w, o.h);
    if (o.grid) {
      ctx.strokeStyle = 'rgba(148,163,255,.06)'; ctx.lineWidth = 1;
      for (let x = 0; x < o.w; x += 30) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, o.h); ctx.stroke(); }
      for (let y = 0; y < o.h; y += 30) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(o.w, y); ctx.stroke(); }
    }
    const P = a => ({ x: a.x * o.scale + o.ox, y: a.y * o.scale + o.oy });
    ctx.lineWidth = 3 * Math.max(o.scale, .5); ctx.strokeStyle = '#c7d2fe';
    bonds.forEach(b => {
      const A = P(atoms[b.a]), B = P(atoms[b.b]);
      const dx = B.x - A.x, dy = B.y - A.y, L = Math.hypot(dx, dy) || 1, nx = -dy / L * 5 * o.scale, ny = dx / L * 5 * o.scale;
      (b.order === 1 ? [0] : b.order === 2 ? [-.6, .6] : [-1.1, 0, 1.1]).forEach(k => {
        ctx.beginPath(); ctx.moveTo(A.x + nx * k, A.y + ny * k); ctx.lineTo(B.x + nx * k, B.y + ny * k); ctx.stroke();
      });
    });
    const used = i => bonds.reduce((s, b) => s + (b.a === i || b.b === i ? b.order : 0), 0);
    atoms.forEach((a, i) => {
      const p = P(a), r = R * o.scale, over = o.valence[a.el] && used(i) > o.valence[a.el];
      ctx.beginPath(); ctx.arc(p.x, p.y, r, 0, 7); ctx.fillStyle = COLOR[a.el] || '#64748b'; ctx.fill();
      ctx.lineWidth = over ? 3 : 1.5; ctx.strokeStyle = over ? '#f87171' : 'rgba(255,255,255,.45)'; ctx.stroke();
      ctx.fillStyle = DARK_TEXT.includes(a.el) ? '#0f172a' : '#fff';
      ctx.font = 'bold ' + Math.round(14 * o.scale) + 'px Sora, sans-serif'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      ctx.fillText(a.el, p.x, p.y + 1);
    });
  }

  // ---------- gallery thumbnails ----------
  document.querySelectorAll('canvas.mini-mol').forEach(c => {
    let d; try { d = JSON.parse(c.dataset.mol); } catch (e) { return; }
    if (!d || !d.atoms || !d.atoms.length) return;
    const xs = d.atoms.map(a => a.x), ys = d.atoms.map(a => a.y);
    const minX = Math.min(...xs) - 30, maxX = Math.max(...xs) + 30, minY = Math.min(...ys) - 30, maxY = Math.max(...ys) + 30;
    const s = Math.min(c.width / (maxX - minX), c.height / (maxY - minY), 1.2);
    drawMol(c.getContext('2d'), d.atoms, d.bonds || [], { scale: s, ox: (c.width - (maxX - minX) * s) / 2 - minX * s, oy: (c.height - (maxY - minY) * s) / 2 - minY * s });
  });

  // ---------- editor ----------
  const cv = document.getElementById('molCanvas');
  if (!cv) return;
  const ctx = cv.getContext('2d');
  const VAL = JSON.parse(document.getElementById('valence-data').textContent);
  const MASS = JSON.parse(document.getElementById('mass-data').textContent);
  let atoms = [], bonds = [], history = [];
  let el = 'C', mode = 'draw', bondOrder = 1, dragFrom = null, dragAtom = null, mouse = { x: 0, y: 0 }, moved = false;

  const snapshot = () => { history.push(JSON.stringify({ atoms, bonds })); if (history.length > 60) history.shift(); };
  const pos = e => {
    const r = cv.getBoundingClientRect(), p = e.touches ? (e.touches[0] || e.changedTouches[0]) : e;
    return { x: (p.clientX - r.left) * cv.width / r.width, y: (p.clientY - r.top) * cv.height / r.height };
  };
  const atomAt = p => atoms.findIndex(a => Math.hypot(a.x - p.x, a.y - p.y) <= R + 3);
  const bondAt = p => bonds.findIndex(b => {
    const A = atoms[b.a], B = atoms[b.b], dx = B.x - A.x, dy = B.y - A.y, L = dx * dx + dy * dy || 1;
    const t = Math.max(0, Math.min(1, ((p.x - A.x) * dx + (p.y - A.y) * dy) / L));
    return Math.hypot(A.x + t * dx - p.x, A.y + t * dy - p.y) < 7;
  });
  const findBond = (i, j) => bonds.findIndex(b => (b.a === i && b.b === j) || (b.a === j && b.b === i));
  const used = i => bonds.reduce((s, b) => s + (b.a === i || b.b === i ? b.order : 0), 0);
  function removeAtom(i) {
    bonds = bonds.filter(b => b.a !== i && b.b !== i).map(b => ({ a: b.a > i ? b.a - 1 : b.a, b: b.b > i ? b.b - 1 : b.b, order: b.order }));
    atoms.splice(i, 1);
  }
  function link(i, j) { const k = findBond(i, j); if (k >= 0) bonds[k].order = bondOrder === bonds[k].order ? bonds[k].order % 3 + 1 : bondOrder; else bonds.push({ a: i, b: j, order: bondOrder }); }

  function render() {
    drawMol(ctx, atoms, bonds, { grid: true, valence: VAL });
    if (dragFrom !== null && mode === 'draw') {
      ctx.setLineDash([6, 6]); ctx.strokeStyle = '#22d3ee'; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.moveTo(atoms[dragFrom].x, atoms[dragFrom].y); ctx.lineTo(mouse.x, mouse.y); ctx.stroke(); ctx.setLineDash([]);
    }
    const counts = {};
    atoms.forEach(a => { counts[a.el] = (counts[a.el] || 0) + 1; });
    const keys = Object.keys(counts);
    const order = (counts.C ? ['C', 'H'].filter(k => counts[k]) : []).concat(keys.filter(k => !(counts.C && (k === 'C' || k === 'H'))).sort());
    const formula = order.map(k => k + (counts[k] > 1 ? counts[k] : '')).join('');
    document.getElementById('formulaOut').innerHTML = formula ? CV.chem(formula) : '–';
    document.getElementById('massOut').textContent = atoms.length ? atoms.reduce((s, a) => s + (MASS[a.el] || 0), 0).toFixed(3) + ' g/mol' : '–';
    document.getElementById('atomCount').textContent = atoms.length;
    const bad = atoms.filter((a, i) => used(i) > (VAL[a.el] || 4)).length;
    document.getElementById('valenceWarn').textContent = bad ? '⚠ ' + bad + ' atom(s) exceed their usual valence' : '';
  }

  function down(e) {
    e.preventDefault();
    const p = pos(e); mouse = p; moved = false;
    const ai = atomAt(p);
    if (mode === 'erase') {
      if (ai >= 0) { snapshot(); removeAtom(ai); } else { const bi = bondAt(p); if (bi >= 0) { snapshot(); bonds.splice(bi, 1); } }
      return render();
    }
    if (mode === 'move') { if (ai >= 0) { snapshot(); dragAtom = ai; cv.style.cursor = 'grabbing'; } return; }
    if (ai >= 0) { dragFrom = ai; return; }
    const bi = bondAt(p);
    if (bi >= 0) { snapshot(); bonds[bi].order = bonds[bi].order % 3 + 1; return render(); }
    snapshot(); atoms.push({ el, x: p.x, y: p.y }); render();
  }
  function move(e) {
    const p = pos(e); mouse = p;
    if (dragAtom !== null) { atoms[dragAtom].x = Math.max(R, Math.min(cv.width - R, p.x)); atoms[dragAtom].y = Math.max(R, Math.min(cv.height - R, p.y)); moved = true; render(); }
    else if (dragFrom !== null) { moved = true; render(); }
  }
  function up(e) {
    if (dragFrom !== null) {
      const p = pos(e), target = atomAt(p);
      if (target >= 0 && target !== dragFrom) { snapshot(); link(dragFrom, target); }
      else if (target === dragFrom && !moved) { if (atoms[dragFrom].el !== el) { snapshot(); atoms[dragFrom].el = el; } }
      else if (target < 0 && Math.hypot(p.x - atoms[dragFrom].x, p.y - atoms[dragFrom].y) > R * 2) {
        snapshot(); atoms.push({ el, x: p.x, y: p.y }); bonds.push({ a: dragFrom, b: atoms.length - 1, order: bondOrder });
      }
    }
    dragFrom = null; dragAtom = null; if (mode === 'move') cv.style.cursor = 'grab';
    render();
  }
  cv.addEventListener('mousedown', down); cv.addEventListener('mousemove', move);
  window.addEventListener('mouseup', e => { if (dragFrom !== null || dragAtom !== null) up(e); });
  cv.addEventListener('touchstart', down, { passive: false });
  cv.addEventListener('touchmove', e => { e.preventDefault(); move(e); }, { passive: false });
  cv.addEventListener('touchend', up);

  const group = (sel, fn) => document.querySelectorAll(sel).forEach(b => b.addEventListener('click', () => {
    document.querySelectorAll(sel).forEach(x => x.classList.remove('active')); b.classList.add('active'); fn(b);
  }));
  group('.pal', b => { el = b.dataset.el; });
  group('.bond-btn', b => { bondOrder = +b.dataset.order; });
  group('.mode-btn', b => { mode = b.dataset.mode; cv.style.cursor = mode === 'move' ? 'grab' : mode === 'erase' ? 'not-allowed' : 'crosshair'; });
  document.getElementById('clearBtn').onclick = () => { if (!atoms.length || confirm('Clear the canvas?')) { snapshot(); atoms = []; bonds = []; render(); } };
  document.getElementById('undoBtn').onclick = () => { const s = history.pop(); if (s) { const d = JSON.parse(s); atoms = d.atoms; bonds = d.bonds; render(); } };
  document.addEventListener('keydown', e => { if ((e.ctrlKey || e.metaKey) && e.key === 'z' && document.activeElement.tagName !== 'INPUT') { e.preventDefault(); document.getElementById('undoBtn').click(); } });

  document.getElementById('autoH').onclick = () => {
    snapshot();
    const n = atoms.length;
    for (let i = 0; i < n; i++) {
      const a = atoms[i]; if (a.el === 'H') continue;
      let free = (VAL[a.el] || 4) - used(i);
      const taken = bonds.filter(b => b.a === i || b.b === i).map(b => { const o = atoms[b.a === i ? b.b : b.a]; return Math.atan2(o.y - a.y, o.x - a.x); });
      for (let k = 0; free > 0 && k < 16; k++) {
        const ang = k * Math.PI / 4 + (k >= 8 ? Math.PI / 8 : 0);
        if (taken.some(t => Math.abs(Math.atan2(Math.sin(t - ang), Math.cos(t - ang))) < 0.6)) continue;
        atoms.push({ el: 'H', x: a.x + 50 * Math.cos(ang), y: a.y + 50 * Math.sin(ang) });
        bonds.push({ a: i, b: atoms.length - 1, order: 1 }); taken.push(ang); free--;
      }
    }
    render();
  };

  const T = {
    water: [[['O', 480, 280], ['H', 425, 320], ['H', 535, 320]], [[0, 1, 1], [0, 2, 1]]],
    methane: [[['C', 480, 290], ['H', 480, 230], ['H', 540, 290], ['H', 480, 350], ['H', 420, 290]], [[0, 1, 1], [0, 2, 1], [0, 3, 1], [0, 4, 1]]],
    co2: [[['O', 400, 290], ['C', 480, 290], ['O', 560, 290]], [[0, 1, 2], [1, 2, 2]]],
    ethyne: [[['H', 340, 290], ['C', 420, 290], ['C', 520, 290], ['H', 600, 290]], [[0, 1, 1], [1, 2, 3], [2, 3, 1]]],
    ethanol: [[['C', 400, 290], ['C', 480, 290], ['O', 560, 290], ['H', 620, 290], ['H', 400, 230], ['H', 400, 350], ['H', 340, 290], ['H', 480, 230], ['H', 480, 350]],
      [[0, 1, 1], [1, 2, 1], [2, 3, 1], [0, 4, 1], [0, 5, 1], [0, 6, 1], [1, 7, 1], [1, 8, 1]]],
    benzene: (() => { const at = [], bd = []; for (let i = 0; i < 6; i++) { const a = Math.PI / 3 * i - Math.PI / 2; at.push(['C', 480 + 70 * Math.cos(a), 290 + 70 * Math.sin(a)]); }
      for (let i = 0; i < 6; i++) { const a = Math.PI / 3 * i - Math.PI / 2; at.push(['H', 480 + 125 * Math.cos(a), 290 + 125 * Math.sin(a)]); bd.push([i, (i + 1) % 6, i % 2 ? 1 : 2], [i, i + 6, 1]); }
      return [at, bd]; })(),
  };
  document.querySelectorAll('.tpl').forEach(b => b.addEventListener('click', () => {
    snapshot();
    const [at, bd] = T[b.dataset.tpl];
    atoms = at.map(([e, x, y]) => ({ el: e, x, y })); bonds = bd.map(([a, c, o]) => ({ a, b: c, order: o }));
    const nm = document.getElementById('structName'); if (!nm.value) nm.value = b.textContent;
    render();
  }));

  const saveBtn = document.getElementById('saveBtn');
  if (saveBtn) saveBtn.onclick = async () => {
    if (!atoms.length) return CV.toast('Draw at least one atom first.', 'bad');
    saveBtn.disabled = true;
    const res = await CV.post(window.STRUCT.saveUrl, { id: window.STRUCT.id, name: document.getElementById('structName').value,
      is_public: document.getElementById('structPublic').checked, atoms, bonds });
    saveBtn.disabled = false;
    if (res.ok) { window.STRUCT.id = res.id; CV.toast('Saved ' + res.name + ' (' + res.formula + ')', 'ok'); window.history.replaceState(null, '', '?id=' + res.id); }
    else CV.toast(res.error || 'Could not save', 'bad');
  };
  document.getElementById('pngBtn').onclick = () => {
    const a = document.createElement('a');
    a.download = (document.getElementById('structName').value || 'molecule').replace(/[^\w-]+/g, '_') + '.png';
    a.href = cv.toDataURL('image/png'); document.body.appendChild(a); a.click(); a.remove();
  };

  try { const init = JSON.parse(document.getElementById('initial-structure').textContent); if (init && init.atoms) { atoms = init.atoms; bonds = init.bonds || []; } } catch (e) { /* new drawing */ }
  render();
})();
