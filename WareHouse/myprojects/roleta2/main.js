/*
DOCSTRING:
main.js
Wires UI to the Wheel class:
- loads themes.json (URL injected by Flask)
- populates theme selector
- reads names and updates wheel
- handles spin logic and result display
Includes robust fallback if fetching themes.json fails.
*/
/* DOM wiring and app logic */
document.addEventListener('DOMContentLoaded', async () => {
  const canvas = document.getElementById('wheel-canvas');
  const nameInput = document.getElementById('name-input');
  const addBtn = document.getElementById('add-name');
  const namesTextarea = document.getElementById('names-textarea');
  const spinBtn = document.getElementById('spin-btn');
  const resultDiv = document.getElementById('result');
  const themeSelect = document.getElementById('theme-select');
  const loadSampleBtn = document.getElementById('load-sample');
  const clearBtn = document.getElementById('clear-names');
  const importBtn = document.getElementById('import-names');
  const exportBtn = document.getElementById('export-names');
  const wheel = new Wheel(canvas, { names: [], colors: ['#ffb3b3','#ffd9b3','#fff3b3','#d9ffb3'] });
  let themes = [];
  // A small fallback theme set in case fetching themes.json fails.
  const defaultThemes = [
    {
      id: 'fallback',
      name: 'Default',
      bg: '#ffffff',
      text: '#222222',
      accent: '#007bff',
      colors: ['#ffb3b3','#ffd9b3','#fff3b3','#d9ffb3']
    }
  ];
  // Helper to populate theme selector
  function populateThemeSelector(list) {
    themeSelect.innerHTML = '';
    list.forEach(t => {
      const opt = document.createElement('option');
      opt.value = t.id;
      opt.textContent = t.name;
      themeSelect.appendChild(opt);
    });
  }
  // Load themes.json (URL injected by Flask)
  try {
    const themesUrl = window.THEMES_JSON_URL || '/static/themes.json';
    const resp = await fetch(themesUrl, {cache: 'no-cache'});
    if (!resp.ok) throw new Error('HTTP ' + resp.status);
    themes = await resp.json();
    if (!Array.isArray(themes) || themes.length === 0) throw new Error('No themes found');
    populateThemeSelector(themes);
    // apply first theme
    applyTheme(themes[0]);
    themeSelect.value = themes[0].id;
  } catch (err) {
    console.error('Failed to load themes:', err);
    // fallback
    themes = defaultThemes;
    populateThemeSelector(themes);
    applyTheme(themes[0]);
    themeSelect.value = themes[0].id;
  }
  function applyTheme(theme) {
    if (!theme) return;
    document.documentElement.style.setProperty('--bg', theme.bg || '#fff');
    document.documentElement.style.setProperty('--text', theme.text || '#222');
    document.documentElement.style.setProperty('--accent', theme.accent || '#007bff');
    // set panel bg slightly adjusted
    let panelBg = theme.bg;
    try {
      panelBg = lightenOrDarkenColor(theme.bg || '#fff', 18);
    } catch(e) {
      panelBg = '#f6f8fa';
    }
    document.documentElement.style.setProperty('--panel-bg', panelBg);
    wheel.setTheme({ colors: theme.colors || [], text: theme.text || '#222' });
    // recolor pointer (DOM element)
    const pointer = document.getElementById('pointer');
    if (pointer) pointer.style.color = theme.accent || '';
    // recolor spin button
    const spin = document.getElementById('spin-btn');
    if (spin) spin.style.background = theme.accent || '';
  }
  function lightenOrDarkenColor(col, amt) {
    // accepts #rgb or #rrggbb. amt can be negative to darken.
    if (typeof col !== 'string') throw new Error('Invalid color');
    let colStr = col.trim();
    if (colStr[0] === '#') colStr = colStr.slice(1);
    if (colStr.length === 3) {
      colStr = colStr.split('').map(c => c + c).join('');
    }
    if (colStr.length !== 6) throw new Error('Invalid hex color');
    const num = parseInt(colStr, 16);
    let r = (num >> 16) & 0xFF;
    let g = (num >> 8) & 0xFF;
    let b = num & 0xFF;
    r = Math.max(0, Math.min(255, r + amt));
    g = Math.max(0, Math.min(255, g + amt));
    b = Math.max(0, Math.min(255, b + amt));
    const newHex = '#' + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
    return newHex;
  }
  themeSelect.addEventListener('change', () => {
    const id = themeSelect.value;
    const t = themes.find(x => x.id === id);
    if (t) applyTheme(t);
  });
  function parseNamesFromTextarea() {
    const lines = namesTextarea.value.split('\n').map(s => s.trim()).filter(s => s.length);
    return lines;
  }
  function updateWheelFromTextarea() {
    const names = parseNamesFromTextarea();
    wheel.setNames(names);
  }
  addBtn.addEventListener('click', () => {
    const v = nameInput.value.trim();
    if (!v) return;
    const cur = parseNamesFromTextarea();
    cur.push(v);
    namesTextarea.value = cur.join('\n');
    nameInput.value = '';
    updateWheelFromTextarea();
  });
  nameInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      addBtn.click();
      e.preventDefault();
    }
  });
  namesTextarea.addEventListener('input', () => {
    updateWheelFromTextarea();
  });
  loadSampleBtn.addEventListener('click', () => {
    const sample = ['Alice','Bob','Charlie','Diana','Eva','Frank','George','Helen','Ivy','Jack'];
    namesTextarea.value = sample.join('\n');
    updateWheelFromTextarea();
  });
  clearBtn.addEventListener('click', () => {
    namesTextarea.value = '';
    updateWheelFromTextarea();
    resultDiv.classList.add('hidden');
  });
  importBtn.addEventListener('click', async () => {
    // prompt user for a newline separated list (simple)
    const data = prompt('Paste names (one per line):');
    if (data === null) return;
    namesTextarea.value = data.split('\n').map(s => s.trim()).filter(s => s).join('\n');
    updateWheelFromTextarea();
  });
  exportBtn.addEventListener('click', () => {
    const names = parseNamesFromTextarea();
    const blob = new Blob([names.join('\n')], {type: 'text/plain'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'names.txt';
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  });
  spinBtn.addEventListener('click', async () => {
    const names = parseNamesFromTextarea();
    if (names.length === 0) {
      alert('Please add at least one name.');
      return;
    }
    resultDiv.classList.add('hidden');
    spinBtn.disabled = true;
    spinBtn.textContent = 'Spinning...';
    // Ensure wheel has latest names before selecting index
    wheel.setNames(names);
    // pick random index
    const idx = wheel.getRandomIndex();
    try {
      const winnerIndex = await wheel.spinToIndex(idx, { duration: 4500 });
      const winner = names[winnerIndex];
      resultDiv.textContent = `Winner: ${winner}`;
      resultDiv.classList.remove('hidden');
      spinBtn.textContent = 'SPIN';
      spinBtn.disabled = false;
    } catch (err) {
      console.error(err);
      spinBtn.textContent = 'SPIN';
      spinBtn.disabled = false;
    }
  });
  // initial sample and initial canvas sizing
  namesTextarea.value = 'Alice\nBob\nCharlie\nDiana\nEva';
  updateWheelFromTextarea();
  // Ensure wheel draws crisply at startup and on resize
  function handleResize() {
    if (typeof wheel.resize === 'function') {
      wheel.resize();
    } else {
      // fallback: redraw
      wheel.draw();
    }
  }
  window.addEventListener('resize', handleResize);
  // Run a resize after a short delay to ensure layout settled
  setTimeout(handleResize, 50);
});