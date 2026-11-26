/* CHEMVERSE – shared front-end helpers */
window.CV = (function () {
  function getCookie(name) {
    const m = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return m ? decodeURIComponent(m.pop()) : '';
  }
  function csrf() {
    const inp = document.querySelector('input[name=csrfmiddlewaretoken]');
    return getCookie('csrftoken') || (inp ? inp.value : '');
  }
  async function post(url, data) {
    try {
      const res = await fetch(url, {
        method: 'POST', credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf(), 'Accept': 'application/json' },
        body: JSON.stringify(data),
      });
      const ct = res.headers.get('content-type') || '';
      if (!ct.includes('json')) return { ok: false, error: res.status === 403 ? 'Session expired – please sign in again.' : 'Server error (' + res.status + ')' };
      return await res.json();
    } catch (e) { return { ok: false, error: 'Network error' }; }
  }
  async function getJSON(url) { const r = await fetch(url, { credentials: 'same-origin' }); return r.json(); }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])); }
  function chem(s) { return esc(s).replace(/([A-Za-z\)\]])(\d+)/g, '$1<sub>$2</sub>').replace(/-&gt;/g, '→'); }
  function toast(msg, kind) {
    const t = document.createElement('div');
    t.className = 'cv-toast ' + (kind || ''); t.setAttribute('role', 'status'); t.textContent = msg;
    document.body.appendChild(t);
    requestAnimationFrame(() => t.classList.add('show'));
    setTimeout(() => { t.classList.remove('show'); setTimeout(() => t.remove(), 300); }, 2800);
  }
  function chartDefaults() {
    if (!window.Chart) return;
    Chart.defaults.color = '#94a3b8';
    Chart.defaults.borderColor = 'rgba(148,163,255,.12)';
    Chart.defaults.font.family = 'Inter, system-ui, sans-serif';
  }
  return { getCookie, csrf, post, getJSON, esc, chem, toast, chartDefaults };
})();

document.addEventListener('DOMContentLoaded', () => {
  // auto-dismiss flash messages
  document.querySelectorAll('.toast-stack .alert').forEach((a, i) => setTimeout(() => {
    if (window.bootstrap) bootstrap.Alert.getOrCreateInstance(a).close(); else a.remove();
  }, 7000 + i * 500));

  // confirmation for destructive forms
  document.querySelectorAll('form[data-confirm]').forEach(f => f.addEventListener('submit', e => {
    if (!confirm(f.dataset.confirm)) e.preventDefault();
  }));

  // favourite stars (AJAX with normal-form fallback)
  document.querySelectorAll('.fav-form').forEach(f => f.addEventListener('submit', async e => {
    e.preventDefault();
    const btn = f.querySelector('button');
    try {
      const r = await fetch(f.action, { method: 'POST', credentials: 'same-origin', body: new FormData(f),
        headers: { 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json' } });
      const d = await r.json();
      if (d.ok) {
        btn.classList.toggle('on', d.favorite);
        const lbl = btn.querySelector('span'); if (lbl) lbl.textContent = d.favorite ? 'Saved' : 'Save';
        CV.toast(d.favorite ? 'Added to favourites ★' : 'Removed from favourites', 'ok');
      }
    } catch (err) { f.submit(); }
  }));

  // compound search suggestions
  const cs = document.getElementById('cSearch'), box = document.getElementById('cSuggest');
  if (cs && box) {
    let t, idx = -1;
    const hide = () => { box.hidden = true; idx = -1; };
    cs.addEventListener('input', () => {
      clearTimeout(t);
      const q = cs.value.trim();
      if (q.length < 2) return hide();
      t = setTimeout(async () => {
        const d = await CV.getJSON(cs.dataset.suggest + '?q=' + encodeURIComponent(q));
        if (!d.results.length) return hide();
        box.innerHTML = d.results.slice(0, 8).map(c => '<a href="/compounds/' + c.id + '/"><span>' + CV.esc(c.name) + '</span><span class="mono small">' + CV.chem(c.formula) + '</span></a>').join('');
        box.hidden = false;
      }, 200);
    });
    cs.addEventListener('keydown', e => {
      const items = [...box.querySelectorAll('a')];
      if (box.hidden || !items.length) return;
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault(); idx = (idx + (e.key === 'ArrowDown' ? 1 : -1) + items.length) % items.length;
        items.forEach((a, i) => a.classList.toggle('hl', i === idx));
      } else if (e.key === 'Enter' && idx >= 0) { e.preventDefault(); location = items[idx].href; } else if (e.key === 'Escape') hide();
    });
    document.addEventListener('click', e => { if (!box.contains(e.target) && e.target !== cs) hide(); });
  }

  // temperature → state explorer
  const th = document.getElementById('thermo');
  if (th) {
    const mp = th.dataset.mp === '' ? null : parseFloat(th.dataset.mp), bp = th.dataset.bp === '' ? null : parseFloat(th.dataset.bp);
    const range = document.getElementById('tempRange'), val = document.getElementById('tempVal'), st = document.getElementById('tempState'), box2 = document.getElementById('particles');
    const N = 18; const ps = [];
    for (let i = 0; i < N; i++) { const p = document.createElement('i'); box2.appendChild(p); ps.push(p); }
    let state = '';
    const layout = s => {
      const W = box2.clientWidth || 300, H = box2.clientHeight || 140;
      ps.forEach((p, i) => {
        let x, y;
        if (s === 'solid') { x = W / 2 - 75 + (i % 6) * 26; y = H / 2 - 35 + Math.floor(i / 6) * 26; }
        else if (s === 'liquid') { x = 10 + Math.random() * (W - 30); y = H - 18 - Math.random() * (H * 0.45); }
        else { x = Math.random() * (W - 14); y = Math.random() * (H - 14); }
        p.style.left = x + 'px'; p.style.top = y + 'px';
      });
    };
    const update = () => {
      const t = +range.value;
      let s = 'liquid';
      if (mp !== null && t < mp) s = 'solid'; else if (bp !== null && t >= bp) s = 'gas'; else if (mp === null && bp !== null && t < bp) s = 'solid';
      val.textContent = t + ' °C'; st.textContent = s[0].toUpperCase() + s.slice(1); st.className = 'state state-' + s;
      if (s !== state) { state = s; layout(s); }
    };
    range.addEventListener('input', update); update();
    setInterval(() => { if (state === 'gas') layout('gas'); else if (state === 'liquid') layout('liquid'); }, 1200);
  }

  // reaction builder live check
  const rx = document.getElementById('rxForm');
  if (rx) {
    const r = document.getElementById('id_reactants'), p = document.getElementById('id_products');
    let last = r, t;
    [r, p].forEach(inp => inp.addEventListener('focus', () => { last = inp; }));
    document.querySelectorAll('[data-add]').forEach(b => b.addEventListener('click', () => {
      last.value = last.value.trim() ? last.value.trim() + ' + ' + b.dataset.add : b.dataset.add; last.focus(); check();
    }));
    const out = id => document.getElementById(id);
    async function check() {
      clearTimeout(t);
      t = setTimeout(async () => {
        if (!r.value.trim() || !p.value.trim()) { out('rxEq').innerHTML = '–'; out('rxStatus').textContent = 'Add reactants and products.'; out('rxTable').innerHTML = out('rxSuggest').innerHTML = out('rxType').innerHTML = ''; return; }
        const d = await CV.getJSON(rx.dataset.check + '?reactants=' + encodeURIComponent(r.value) + '&products=' + encodeURIComponent(p.value));
        if (!d.ok) { out('rxStatus').innerHTML = '<span class="text-danger">' + CV.esc(d.error) + '</span>'; out('rxTable').innerHTML = out('rxSuggest').innerHTML = ''; return; }
        out('rxEq').innerHTML = CV.chem(d.equation);
        out('rxStatus').innerHTML = d.is_balanced ? '<span class="text-success fw-semibold">✓ Balanced</span>' : '<span class="text-warning fw-semibold">⚠ Not balanced</span>';
        out('rxTable').innerHTML = '<table class="table table-cv table-sm"><thead><tr><th>Element</th><th class="text-end">Left</th><th class="text-end">Right</th></tr></thead><tbody>' +
          d.table.map(x => '<tr class="' + (x.left !== x.right ? 'row-bad' : '') + '"><td>' + x.element + '</td><td class="text-end">' + x.left + '</td><td class="text-end">' + x.right + '</td></tr>').join('') + '</tbody></table>';
        if (d.suggestion) {
          out('rxSuggest').innerHTML = '<div class="alert alert-info py-2 small">Try: <b class="eq">' + CV.chem(d.suggestion) + '</b> <button type="button" class="btn btn-sm btn-cv ms-2" id="useSug">Use it</button></div>';
          document.getElementById('useSug').onclick = () => { const [a, b] = d.suggestion.split('→'); r.value = a.trim(); p.value = b.trim(); check(); };
        } else out('rxSuggest').innerHTML = d.suggestion_error ? '<div class="small text-warning">' + CV.esc(d.suggestion_error) + '</div>' : '';
        out('rxType').innerHTML = '<b>Detected type:</b> ' + CV.esc(d.detected_type) + ' – ' + CV.esc(d.type_info);
      }, 300);
    }
    [r, p].forEach(inp => inp.addEventListener('input', check));
    check();
  }

  // count-up numbers
  document.querySelectorAll('[data-count]').forEach(el => {
    const target = +el.dataset.count; if (!target) return;
    let cur = 0; const step = Math.max(1, Math.round(target / 40));
    const tick = () => { cur = Math.min(target, cur + step); el.textContent = cur; if (cur < target) requestAnimationFrame(tick); };
    el.textContent = '0'; tick();
  });
});
