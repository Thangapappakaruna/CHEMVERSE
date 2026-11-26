/* CHEMVERSE – seven chemistry games */
(function () {
  const stage = document.getElementById('gameStage');
  if (!stage) return;
  const D = stage.dataset, game = D.game, scoreEl = document.getElementById('gScore');
  let score = 0, timers = [];
  const setScore = v => { score = Math.max(0, Math.round(v)); scoreEl.textContent = score; };
  const shuffle = a => { a = a.slice(); for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
  const pick = (a, n) => shuffle(a).slice(0, n);
  const every = (fn, ms) => { const id = setInterval(fn, ms); timers.push(id); return id; };
  const stopAll = () => { timers.forEach(clearInterval); timers = []; };
  let EL = null, CMP = null;
  const elements = async () => EL || (EL = (await CV.getJSON(D.elements)).elements);
  const compounds = async () => CMP || (CMP = (await CV.getJSON(D.compounds)).results);
  const CAT = { 'alkali-metal': 'Alkali metal', 'alkaline-earth': 'Alkaline earth metal', 'transition': 'Transition metal', 'post-transition': 'Post-transition metal',
    'metalloid': 'Metalloid', 'nonmetal': 'Reactive non-metal', 'halogen': 'Halogen', 'noble-gas': 'Noble gas', 'lanthanide': 'Lanthanide', 'actinide': 'Actinide' };

  async function finish(title, details) {
    stopAll();
    let extra;
    const r = await CV.post(D.submit, { game, points: score, details: details || '' });
    if (!r.ok) extra = '<p class="text-danger">' + CV.esc(r.error) + '</p>';
    else if (r.guest) extra = '<p class="text-success">Kept for this visit – your best: <b>' + r.best + '</b></p><p class="text-secondary small"><a href="' + D.login + '">Sign in</a> to save scores permanently, earn XP and join the leaderboard.</p>';
    else extra = '<p class="text-success">Score saved! Your best: <b>' + r.best + '</b></p>';
    stage.innerHTML = '<div class="game-over"><h2 class="h3">' + CV.esc(title) + '</h2><div class="display-3 fw-bold grad-text">' + score + '</div><p class="text-secondary">points</p>' + extra +
      '<button class="btn btn-cv" id="again">Play again</button> <a class="btn btn-cv-outline" href="/quiz/leaderboard/?board=games">Leaderboard</a></div>';
    document.getElementById('again').onclick = () => { setScore(0); start(); };
  }
  const top = (left, right) => '<div class="g-top"><span>' + left + '</span><span>' + right + '</span></div>';
  function answerButtons(box, options, label, correct, onDone) {
    box.innerHTML = '';
    options.forEach(o => {
      const b = document.createElement('button'); b.className = 'ans'; b.innerHTML = label(o);
      b.onclick = () => {
        const ok = o === correct;
        [...box.children].forEach((x, i) => { x.disabled = true; if (options[i] === correct) x.classList.add('right'); });
        if (!ok) b.classList.add('wrong');
        setTimeout(() => onDone(ok), ok ? 450 : 900);
      };
      box.appendChild(b);
    });
  }

  // 1. Guess the Element (60 s, clues)
  async function guessElement() {
    const els = (await elements()).filter(e => e.number <= 56);
    let time = 60, streak = 0, n = 0, right = 0;
    stage.innerHTML = top('⏱ <b id="gt">60</b> s', '🔥 streak <b id="gs">0</b>') + '<div class="clue-list" id="clues"></div><div class="answers" id="ans"></div>';
    every(() => { time--; document.getElementById('gt').textContent = time; if (time <= 0) finish("Time's up!", right + '/' + n + ' correct'); }, 1000);
    const round = () => {
      if (time <= 0) return;
      const opts = pick(els, 4), t = opts[Math.floor(Math.random() * 4)];
      document.getElementById('clues').innerHTML = '<div>Atomic number: <b>' + t.number + '</b></div><div>Group <b>' + (t.group || '–') + '</b>, period <b>' + t.period + '</b></div><div>Category: <b>' + CAT[t.category] + '</b></div>';
      answerButtons(document.getElementById('ans'), opts, o => CV.esc(o.name) + ' <span class="text-secondary">(' + o.symbol + ')</span>', t, ok => {
        n++; if (ok) { right++; streak++; setScore(score + 10 + Math.min(streak, 10) * 2); } else streak = 0;
        document.getElementById('gs').textContent = streak; round();
      });
    };
    round();
  }

  // 2. Periodic Table Challenge (click the right cell)
  async function periodicChallenge() {
    const els = await elements();
    const pos = e => (e.number >= 57 && e.number <= 71) ? [e.number - 54, 9] : (e.number >= 89 && e.number <= 103) ? [e.number - 86, 10] : [e.group, e.period];
    const targets = pick(els.filter(e => e.number <= 86), 10);
    let r = 0;
    stage.innerHTML = top('Round <b id="pr">1</b>/10', 'Find: <b id="pf" class="text-cyan"></b>') + '<div class="mini-pt" id="mpt"></div><p class="small text-secondary text-center mt-3">Exact cell = 100 pts, a neighbouring cell = 40 pts.</p>';
    const grid = document.getElementById('mpt');
    els.forEach(e => {
      const [c, row] = pos(e), b = document.createElement('button');
      b.style.gridColumn = c; b.style.gridRow = row; b.textContent = e.symbol; b.dataset.n = e.number; b.title = '';
      b.onclick = () => {
        const t = targets[r]; if (!t) return;
        const [tc, tr] = pos(t), d = Math.abs(tc - c) + Math.abs(tr - row);
        const tb = grid.querySelector('[data-n="' + t.number + '"]');
        if (e.number === t.number) { setScore(score + 100); b.classList.add('right'); }
        else { setScore(score + (d === 1 ? 40 : 0)); b.classList.add('wrong'); tb.classList.add('show'); }
        grid.style.pointerEvents = 'none';
        setTimeout(() => { grid.querySelectorAll('button').forEach(x => x.className = ''); grid.style.pointerEvents = ''; r++; next(); }, 900);
      };
      grid.appendChild(b);
    });
    const next = () => { if (r >= targets.length) return finish('Table complete!', score + ' pts'); document.getElementById('pr').textContent = r + 1; document.getElementById('pf').textContent = targets[r].name; };
    next();
  }

  // 3. Chemical Formula Matching
  async function formulaMatch() {
    const all = (await compounds()).filter(c => c.data_quality !== 'user');
    let round = 0, start = Date.now(), mistakes = 0;
    const play = () => {
      if (round >= 3) { const secs = Math.round((Date.now() - start) / 1000); setScore(Math.max(100, 1500 - secs * 10 - mistakes * 40)); return finish('All matched!', secs + ' s, ' + mistakes + ' mistakes'); }
      const set = pick(all, 6); let sel = null, done = 0;
      stage.innerHTML = top('Set <b>' + (round + 1) + '</b>/3', 'Mistakes <b id="mm">' + mistakes + '</b>') +
        '<div class="match-cols"><div id="mn"></div><div id="mf"></div></div><p class="small text-secondary text-center mt-2">Click a name, then its formula.</p>';
      const mk = (txt, id, kind, html) => { const b = document.createElement('button'); b.className = 'match-item'; b.dataset.id = id; b.dataset.kind = kind; b.innerHTML = html || CV.esc(txt); return b; };
      shuffle(set).forEach(c => document.getElementById('mn').appendChild(mk(c.name, c.id, 'n')));
      shuffle(set).forEach(c => document.getElementById('mf').appendChild(mk(c.formula, c.id, 'f', '<span class="mono">' + CV.chem(c.formula) + '</span>')));
      stage.querySelectorAll('.match-item').forEach(b => b.onclick = () => {
        if (b.classList.contains('done')) return;
        if (!sel || sel.dataset.kind === b.dataset.kind) { stage.querySelectorAll('.sel').forEach(x => x.classList.remove('sel')); sel = b; b.classList.add('sel'); return; }
        if (sel.dataset.id === b.dataset.id) { sel.classList.replace('sel', 'done'); b.classList.add('done'); done++; sel = null; if (done === 6) { round++; setTimeout(play, 400); } }
        else { mistakes++; document.getElementById('mm').textContent = mistakes; [sel, b].forEach(x => { x.classList.add('shake'); setTimeout(() => x.classList.remove('shake', 'sel'), 350); }); sel = null; }
      });
    };
    play();
  }

  // 4. Molecular Weight Challenge
  async function weightChallenge() {
    const all = (await compounds()).filter(c => c.molar_mass);
    const qs = pick(all, 10); let r = 0, right = 0;
    const round = () => {
      if (r >= qs.length) return finish('Challenge complete', right + '/10 correct');
      const c = qs[r];
      const wrong = shuffle(all.filter(x => Math.abs(x.molar_mass - c.molar_mass) > 4)).slice(0, 3).map(x => x.molar_mass);
      const opts = shuffle([c.molar_mass, ...wrong]);
      stage.innerHTML = top('Question <b>' + (r + 1) + '</b>/10', 'Correct <b>' + right + '</b>') +
        '<div class="text-center mb-3"><div class="small text-secondary">What is the molar mass of</div><div class="formula-xl">' + CV.chem(c.formula) + '</div><div class="text-secondary">' + CV.esc(c.name) + '</div></div><div class="answers" id="ans"></div>';
      answerButtons(document.getElementById('ans'), opts, o => o + ' g/mol', c.molar_mass, ok => { if (ok) { right++; setScore(score + 150); } r++; round(); });
    };
    round();
  }

  // 5. Memory game
  async function memory() {
    const set = pick((await elements()).filter(e => e.number <= 36), 8);
    const cards = shuffle(set.flatMap(e => [{ id: e.number, text: e.symbol }, { id: e.number, text: e.name }]));
    let open = [], matched = 0, moves = 0, lock = false; const t0 = Date.now();
    stage.innerHTML = top('Moves <b id="mv">0</b>', 'Match each symbol to its name') + '<div class="mem-grid" id="mg"></div>';
    const g = document.getElementById('mg');
    cards.forEach(c => {
      const d = document.createElement('button'); d.className = 'mcard'; d.innerHTML = '<span class="back">⚛</span><span class="face">' + CV.esc(c.text) + '</span>';
      d.onclick = () => {
        if (lock || d.classList.contains('open')) return;
        d.classList.add('open'); open.push([d, c]);
        if (open.length < 2) return;
        moves++; document.getElementById('mv').textContent = moves;
        const [[d1, c1], [d2, c2]] = open;
        if (c1.id === c2.id && c1.text !== c2.text) {
          d1.classList.add('done'); d2.classList.add('done'); open = [];
          if (++matched === set.length) { const s = Math.round((Date.now() - t0) / 1000); setScore(Math.max(80, 1000 - moves * 20 - s * 3)); setTimeout(() => finish('All pairs found!', moves + ' moves, ' + s + ' s'), 400); }
        } else { lock = true; setTimeout(() => { d1.classList.remove('open'); d2.classList.remove('open'); open = []; lock = false; }, 750); }
      };
      g.appendChild(d);
    });
  }

  // 6. Boiling Point Challenge
  async function boilingChallenge() {
    const list = shuffle((await compounds()).filter(c => c.boiling_point !== null));
    let i = 0, streak = 0;
    const round = () => {
      if (i + 1 >= list.length) return finish('You beat every compound!', 'streak ' + streak);
      const a = list[i], b = list[i + 1];
      stage.innerHTML = top('🔥 Streak <b>' + streak + '</b>', 'Which boils at a higher temperature?') + '<div class="hl-wrap">' +
        '<div class="hl-card"><h3 class="h5">' + CV.esc(a.name) + '</h3><div class="mono">' + CV.chem(a.formula) + '</div><div class="display-6 fw-bold mt-2">' + a.boiling_point + ' °C</div></div><div class="hl-vs">VS</div>' +
        '<div class="hl-card"><h3 class="h5">' + CV.esc(b.name) + '</h3><div class="mono">' + CV.chem(b.formula) + '</div><div class="display-6 fw-bold mt-2" id="bb">? °C</div>' +
        '<div class="d-flex gap-2 justify-content-center mt-2"><button class="btn btn-cv" data-g="h">▲ Higher</button><button class="btn btn-cv-outline" data-g="l">▼ Lower</button></div></div></div>';
      stage.querySelectorAll('[data-g]').forEach(btn => btn.onclick = () => {
        stage.querySelectorAll('[data-g]').forEach(x => x.disabled = true);
        document.getElementById('bb').textContent = b.boiling_point + ' °C';
        const ok = (btn.dataset.g === 'h') === (b.boiling_point >= a.boiling_point);
        if (ok) { streak++; setScore(score + 20 * streak); i++; setTimeout(round, 800); }
        else setTimeout(() => finish('Wrong – ' + b.name + ' boils at ' + b.boiling_point + ' °C', 'streak ' + streak), 900);
      });
    };
    round();
  }

  // 7. Timed Chemistry Quiz
  async function timedQuiz() {
    const qs = (await CV.getJSON(D.questions + '?n=50')).questions;
    let time = 60, i = 0, right = 0;
    stage.innerHTML = top('⏱ <b id="tt">60</b> s', 'Correct <b id="tc">0</b>') + '<h2 class="h5 text-center mb-3" id="tq"></h2><div class="answers" id="ans"></div>';
    every(() => { time--; document.getElementById('tt').textContent = time; if (time <= 0) finish("Time's up!", right + ' correct of ' + i); }, 1000);
    const round = () => {
      if (time <= 0) return;
      if (i >= qs.length) return finish('You answered every question!', right + ' correct');
      const q = qs[i];
      document.getElementById('tq').textContent = q.text;
      answerButtons(document.getElementById('ans'), q.options, o => CV.esc(o), q.options[q.answer], ok => {
        i++; if (ok) { right++; setScore(score + ({ easy: 50, medium: 80, hard: 120 }[q.difficulty] || 50)); }
        document.getElementById('tc').textContent = right; round();
      });
    };
    round();
  }

  const GAMES = { 'guess-element': guessElement, 'periodic-challenge': periodicChallenge, 'formula-match': formulaMatch,
    'weight-challenge': weightChallenge, 'memory': memory, 'boiling-challenge': boilingChallenge, 'timed-quiz': timedQuiz };
  function start() {
    stopAll();
    stage.innerHTML = '<p class="text-center text-secondary py-5">Loading…</p>';
    const fn = GAMES[game];
    if (!fn) { stage.innerHTML = '<p class="text-center">Unknown game.</p>'; return; }
    fn().catch(() => { stage.innerHTML = '<p class="text-center text-danger py-5">Could not load game data. Is the database seeded?</p>'; });
  }
  window.CVGames = { start };
  start();
})();
