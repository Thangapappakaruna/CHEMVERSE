/* CHEMVERSE Lab Simulator – five safe virtual experiments */
(function () {
  const lab = document.getElementById('lab');
  if (!lab) return;
  const $ = id => document.getElementById(id);
  let result = '';
  const setResult = r => { result = r; $('labResult').textContent = r; };
  const rec = $('recordBtn');
  if (rec) rec.onclick = async () => {
    if (!result) return CV.toast('Run the experiment first.', 'bad');
    const r = await CV.post(lab.dataset.record, { result });
    CV.toast(r.ok ? (r.guest ? 'Recorded for this visit ✓ – sign in to keep it' : 'Recorded in your lab notebook ✓') : (r.error || 'Could not record'), r.ok ? 'ok' : 'bad');
  };
  CV.chartDefaults();
  const exp = lab.dataset.exp;

  // ---------- 1. Acid–base titration (strong acid / strong base, 25 °C) ----------
  if (exp === 'titration') {
    const Va = 25;
    const pH = (Ca, Cb, Vb) => {
      const na = Ca * Va / 1000, nb = Cb * Vb / 1000, V = (Va + Vb) / 1000;
      if (Math.abs(na - nb) < 1e-12) return 7;
      if (na > nb) return -Math.log10((na - nb) / V);
      return 14 + Math.log10((nb - na) / V);
    };
    const ind = p => p < 8.2 ? ['Colourless', 'rgba(226,232,240,.85)'] : p < 10 ? ['Pink', '#f9a8d4'] : ['Deep pink / magenta', '#db2777'];
    const chart = new Chart($('tChart'), { type: 'line', data: { datasets: [
      { label: 'pH', data: [], borderColor: '#22d3ee', pointRadius: 0, borderWidth: 2, tension: .2 },
      { label: 'Now', data: [], pointRadius: 6, pointBackgroundColor: '#f472b6', showLine: false }] },
      options: { maintainAspectRatio: false, animation: false, parsing: false, scales: { x: { type: 'linear', min: 0, max: 60, title: { display: true, text: 'NaOH added (mL)' } }, y: { min: 0, max: 14, title: { display: true, text: 'pH' } } }, plugins: { legend: { display: false } } } });
    const update = () => {
      const Ca = +$('ca').value, Cb = +$('cb').value, Vb = +$('vb').value;
      $('caV').textContent = Ca.toFixed(2); $('cbV').textContent = Cb.toFixed(2); $('vbV').textContent = Vb.toFixed(2);
      const p = pH(Ca, Cb, Vb), [name, col] = ind(p), eq = Ca * Va / Cb;
      $('phV').textContent = p.toFixed(2); $('indV').textContent = 'Phenolphthalein: ' + name; $('eqV').textContent = eq.toFixed(1);
      $('flaskLiquid').setAttribute('fill', col);
      $('buretteLiquid').setAttribute('height', Math.max(0, 116 * (1 - Vb / 60))); $('buretteLiquid').setAttribute('y', 7 + 116 * Vb / 60);
      const curve = []; for (let v = 0; v <= 60; v += 0.25) curve.push({ x: v, y: pH(Ca, Cb, v) });
      chart.data.datasets[0].data = curve; chart.data.datasets[1].data = [{ x: Vb, y: p }]; chart.update();
      setResult('pH ' + p.toFixed(2) + ' after ' + Vb.toFixed(1) + ' mL of ' + Cb.toFixed(2) + ' M NaOH (equivalence at ' + eq.toFixed(1) + ' mL)');
    };
    ['ca', 'cb', 'vb'].forEach(id => $(id).addEventListener('input', update));
    lab.querySelectorAll('[data-add]').forEach(b => b.onclick = () => { $('vb').value = Math.min(60, +$('vb').value + +b.dataset.add).toFixed(1); update(); });
    $('tReset').onclick = () => { $('vb').value = 0; update(); };
    update();
  }

  // ---------- 2. Flame tests ----------
  if (exp === 'flame-test') {
    lab.querySelectorAll('.salt').forEach(b => b.onclick = () => {
      lab.querySelectorAll('.salt').forEach(x => x.classList.remove('active')); b.classList.add('active');
      $('flame').style.setProperty('--f', b.dataset.color);
      $('flameName').textContent = b.dataset.name;
      $('flameInfo').textContent = b.dataset.salt + ' – the ' + b.dataset.ion + ' ion gives a ' + b.dataset.name.toLowerCase() + ' flame.';
      setResult(b.dataset.ion + ' → ' + b.dataset.name + ' flame');
    });
  }

  // ---------- 3. pH & indicators ----------
  if (exp === 'ph-indicator') {
    const UNI = [[0, '#e11d48', 'Red'], [3, '#f97316', 'Orange'], [5, '#facc15', 'Yellow'], [6.5, '#22c55e', 'Green'], [7.5, '#14b8a6', 'Blue-green'], [9, '#3b82f6', 'Blue'], [11, '#4f46e5', 'Indigo'], [12.5, '#7c3aed', 'Violet']];
    const uni = p => UNI.filter(u => p >= u[0]).pop();
    const show = (p, label) => {
      const u = uni(p);
      $('tubeUni').style.background = u[1]; $('uniName').textContent = u[2];
      const lit = p < 4.5 ? ['#ef4444', 'Red'] : p > 8.3 ? ['#3b82f6', 'Blue'] : ['#9b59b6', 'Purple (in transition range)'];
      $('stripLitmus').style.background = lit[0]; $('litName').textContent = lit[1];
      const ph = p < 8.2 ? ['rgba(226,232,240,.4)', 'Colourless'] : p < 10 ? ['#f9a8d4', 'Pink'] : ['#db2777', 'Magenta'];
      $('tubePhth').style.background = ph[0]; $('phthName').textContent = ph[1];
      $('phMarker').style.left = (p / 14 * 100) + '%';
      const kind = p < 7 ? (p < 3 ? 'strongly acidic' : 'acidic') : p > 7 ? (p > 11 ? 'strongly basic (alkaline)' : 'basic (alkaline)') : 'neutral';
      $('phText').textContent = (label ? label + ': ' : '') + 'pH ' + p + ' is ' + kind + '.';
      setResult((label || 'Custom solution') + ' – pH ' + p + ', universal indicator ' + u[2].toLowerCase());
    };
    lab.querySelectorAll('.sol').forEach(b => b.onclick = () => { lab.querySelectorAll('.sol').forEach(x => x.classList.remove('active')); b.classList.add('active'); $('phCustom').value = b.dataset.ph; $('phCustomV').textContent = (+b.dataset.ph).toFixed(1); show(+b.dataset.ph, b.textContent.split(' – ')[0]); });
    $('phCustom').addEventListener('input', e => { $('phCustomV').textContent = (+e.target.value).toFixed(1); show(+e.target.value); });
    show(7);
  }

  // ---------- 4. Gas laws ----------
  if (exp === 'gas-laws') {
    const R = 0.08206;
    const chart = new Chart($('gasChart'), { type: 'line', data: { datasets: [
      { label: 'P (atm)', data: [], borderColor: '#a78bfa', pointRadius: 0, borderWidth: 2 },
      { label: 'Now', data: [], pointRadius: 6, pointBackgroundColor: '#22d3ee', showLine: false }] },
      options: { maintainAspectRatio: false, animation: false, parsing: false, scales: { x: { type: 'linear', min: 2, max: 60, title: { display: true, text: 'Volume (L)' } }, y: { min: 0, title: { display: true, text: 'Pressure (atm)' } } }, plugins: { legend: { display: false } } } });
    const box = $('gasBox'), g = box.getContext('2d');
    let parts = [], n = 1, T = 273, V = 22.4;
    const update = () => {
      n = +$('gn').value; T = +$('gt').value; V = +$('gv').value;
      const P = n * R * T / V;
      $('nV').textContent = n.toFixed(2); $('tV').textContent = T; $('tcV').textContent = (T - 273.15).toFixed(0); $('vV').textContent = V.toFixed(1); $('pV').textContent = P.toFixed(2);
      const iso = []; for (let v = 2; v <= 60; v += 0.5) iso.push({ x: v, y: n * R * T / v });
      chart.data.datasets[0].data = iso; chart.data.datasets[1].data = [{ x: V, y: P }]; chart.update();
      const want = Math.round(n * 20);
      while (parts.length < want) parts.push({ x: Math.random(), y: Math.random(), a: Math.random() * 6.28 });
      parts.length = want;
      setResult('n = ' + n.toFixed(2) + ' mol, T = ' + T + ' K, V = ' + V.toFixed(1) + ' L → P = ' + P.toFixed(2) + ' atm');
    };
    ['gn', 'gt', 'gv'].forEach(id => $(id).addEventListener('input', update));
    update();
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    (function anim() {
      const W = box.width, H = box.height, h = 40 + (H - 50) * (V / 60), top = H - 10 - h, speed = 0.002 * Math.sqrt(T / 273);
      g.clearRect(0, 0, W, H);
      g.strokeStyle = '#94a3b8'; g.lineWidth = 2; g.strokeRect(20, top, W - 40, h);
      g.fillStyle = '#475569'; g.fillRect(16, top - 8, W - 32, 8);
      parts.forEach(p => {
        p.x += Math.cos(p.a) * speed * 6; p.y += Math.sin(p.a) * speed * 6 * (220 / h);
        if (p.x < 0 || p.x > 1) { p.a = Math.PI - p.a; p.x = Math.min(1, Math.max(0, p.x)); }
        if (p.y < 0 || p.y > 1) { p.a = -p.a; p.y = Math.min(1, Math.max(0, p.y)); }
        g.fillStyle = '#22d3ee'; g.beginPath(); g.arc(26 + p.x * (W - 52), top + 6 + p.y * (h - 12), 3.5, 0, 7); g.fill();
      });
      if (!reduce) requestAnimationFrame(anim);
    })();
  }

  // ---------- 5. Heating curve of water (100 g) ----------
  if (exp === 'heating-curve') {
    const m = 100, cI = 2.09, cW = 4.18, cS = 2.01, Lf = 334, Lv = 2257;
    const q1 = m * cI * 20 / 1000, q2 = q1 + m * Lf / 1000, q3 = q2 + m * cW * 100 / 1000, q4 = q3 + m * Lv / 1000;
    const stateAt = q => {
      if (q <= q1) return [-20 + q * 1000 / (m * cI), 'solid', 'Solid (ice) warming'];
      if (q <= q2) return [0, 'solid', 'Melting – ice and water at 0 °C'];
      if (q <= q3) return [(q - q2) * 1000 / (m * cW), 'liquid', 'Liquid water warming'];
      if (q <= q4) return [100, 'liquid', 'Boiling – water and steam at 100 °C'];
      return [100 + (q - q4) * 1000 / (m * cS), 'gas', 'Steam (gas) heating'];
    };
    const curve = []; for (let q = 0; q <= 310; q += 1) curve.push({ x: q, y: stateAt(q)[0] });
    const chart = new Chart($('hChart'), { type: 'line', data: { datasets: [
      { label: 'Temperature', data: curve, borderColor: '#22d3ee', pointRadius: 0, borderWidth: 2 },
      { label: 'Now', data: [], pointRadius: 7, pointBackgroundColor: '#f472b6', showLine: false }] },
      options: { maintainAspectRatio: false, animation: false, parsing: false, scales: { x: { type: 'linear', min: 0, max: 310, title: { display: true, text: 'Heat added (kJ)' } }, y: { min: -30, max: 160, title: { display: true, text: 'Temperature (°C)' } } }, plugins: { legend: { display: false } } } });
    const update = () => {
      const q = +$('hq').value, [T, s, label] = stateAt(q);
      $('qV').textContent = q.toFixed(1); $('hT').textContent = T.toFixed(1); $('hPhase').textContent = label; $('hPhase').className = 'state state-' + s;
      chart.data.datasets[1].data = [{ x: q, y: T }]; chart.update();
      setResult(q.toFixed(1) + ' kJ added → ' + T.toFixed(1) + ' °C (' + label.toLowerCase() + ')');
    };
    $('hq').addEventListener('input', update); update();
  }
})();
