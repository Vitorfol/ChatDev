
/*
'''
Script for the Random Winner Wheel.
Contains the Wheel class to draw and spin the canvas-based wheel and UI glue code to manage names and themes.
'''
 Script for the Random Winner Wheel.
 Contains the Wheel class to draw and spin the canvas-based wheel and UI glue code to manage names and themes.
*/
/* Main JavaScript - Wheel + UI logic */
(() => {
  // Utilities
  function rand(min, max) { return Math.floor(Math.random() * (max - min + 1)) + min; }
  function easeOutCubic(t) { return 1 - Math.pow(1 - t, 3); }
  // Color palettes for themes (will be used to paint wheel segments)
  const THEME_PALETTES = {
    light: ['#FF8A80','#FFD180','#FFF59D','#C8E6C9','#80DEEA','#A7FFEB','#B39DDB','#90CAF9'],
    dark: ['#ff6b6b','#ffd166','#faff8e','#b9f6ca','#4dd0e1','#80cbc4','#b388ff','#64b5f6'],
    neon: ['#ff2d95','#7cff01','#00ffff','#ffdd00','#ff6a00','#00ff9e','#ff00ff','#47ffa2'],
    pastel: ['#ffdbe9','#fff0b3','#d1ffd6','#cfefff','#e7dfff','#ffd6e7','#fbe7d6','#e6f7ff'],
    retro: ['#ffb86b','#ffd3a8','#f3e2a9','#b8e0d2','#c0b9ff','#ffb6c1','#f6c49f','#c3d69b']
  };
  // Wheel class
  class Wheel {
    /*
    Manage wheel: drawing, recalculating segments, spinning animation, and determining winner.
    */
    constructor(canvas, options = {}) {
      this.canvas = canvas;
      this.ctx = canvas.getContext('2d');
      this.names = [];
      this.rotation = 0; // radians
      this.isSpinning = false;
      this.frame = null;
      this.onResult = options.onResult || function() {};
      this.theme = options.theme || 'light';
      this.padAngle = 0.02; // radians padding between segments
      this.textColor = '#111';
      this._devicePixelRatioFix();
      window.addEventListener('resize', () => { this._devicePixelRatioFix(); this.draw(); });
    }
    _devicePixelRatioFix() {
      const dpr = window.devicePixelRatio || 1;
      const rect = this.canvas.getBoundingClientRect();
      // If rect has zero size (canvas not yet laid out), use current width/height attributes as fallback
      const width = rect.width || (this.canvas.width / dpr);
      const height = rect.height || (this.canvas.height / dpr);
      this.canvas.width = width * dpr;
      this.canvas.height = height * dpr;
      this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      this.centerX = width / 2;
      this.centerY = height / 2;
      this.radius = Math.min(width, height) / 2 - 18;
    }
    setTheme(themeId) { this.theme = themeId; this.draw(); }
    setNames(names) {
      this.names = names.slice();
      this.draw();
    }
    addName(name) {
      this.names.push(name);
      this.draw();
    }
    removeName(index) {
      if (index >= 0 && index < this.names.length) {
        this.names.splice(index,1);
        this.draw();
      }
    }
    clearNames() {
      this.names = [];
      this.draw();
    }
    draw() {
      const ctx = this.ctx;
      const w = this.canvas.width / (window.devicePixelRatio || 1);
      const h = this.canvas.height / (window.devicePixelRatio || 1);
      ctx.clearRect(0,0,w,h);
      ctx.save();
      ctx.translate(this.centerX, this.centerY);
      ctx.rotate(this.rotation);
      // draw segments
      const count = Math.max(this.names.length, 1);
      const palette = THEME_PALETTES[this.theme] || THEME_PALETTES.light;
      for (let i = 0; i < count; i++) {
        const start = (i / count) * Math.PI * 2;
        const end = ((i + 1) / count) * Math.PI * 2;
        ctx.beginPath();
        ctx.moveTo(0,0);
        ctx.arc(0,0,this.radius, start + this.padAngle, end - this.padAngle, false);
        ctx.closePath();
        const color = palette[i % palette.length];
        ctx.fillStyle = color;
        ctx.fill();
        ctx.strokeStyle = (i % 2 === 0) ? 'rgba(0,0,0,0.06)' : 'rgba(0,0,0,0.03)';
        ctx.lineWidth = 1;
        ctx.stroke();
        // draw text label
        const mid = (start + end) / 2;
        ctx.save();
        ctx.rotate(mid);
        ctx.translate(this.radius * 0.6, 0);
        ctx.rotate(Math.PI/2);
        ctx.fillStyle = getTextColor(color);
        ctx.font = `${Math.max(12, Math.min(22, this.radius / 8))}px sans-serif`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        const label = (this.names.length === 0) ? 'Add names' : this.names[i % this.names.length];
        wrapFillText(ctx, label, 0, 0, this.radius * 0.5, 16);
        ctx.restore();
      }
      // draw center circle
      ctx.beginPath();
      ctx.arc(0,0, this.radius * 0.16, 0, Math.PI*2);
      ctx.fillStyle = 'rgba(255,255,255,0.9)';
      ctx.fill();
      ctx.strokeStyle = 'rgba(0,0,0,0.06)';
      ctx.stroke();
      ctx.restore();
      // draw outer ring (pointer side neutral)
      ctx.beginPath();
      ctx.arc(this.centerX, this.centerY, this.radius + 10, 0, Math.PI*2);
      ctx.strokeStyle = 'rgba(0,0,0,0.03)';
      ctx.lineWidth = 2;
      ctx.stroke();
    }
    spin() {
      if (this.isSpinning || this.names.length === 0) return;
      this.isSpinning = true;
      const count = this.names.length;
      // Determine random winner index to land on:
      const winnerIndex = rand(0, count - 1);
      // Calculate final rotation so that winner segment lines up with pointer at top (pointer at canvas top - rotation must align)
      // Our pointer is at the top (canvas 0 angle). The segment mid-angle for index i (without rotation) is ((i + 0.5)/count)*2pi
      const segmentMid = ((winnerIndex + 0.5) / count) * Math.PI * 2;
      // We want segmentMid + rotation_final == -Math.PI/2 (so it points at the top pointer), so rotation_final = -Math.PI/2 - segmentMid + 2pi*N
      const extraTurns = rand(5, 8); // full spins
      const rotationFinal = -Math.PI/2 - segmentMid + extraTurns * Math.PI * 2;
      const startRotation = this.rotation % (Math.PI * 2);
      const delta = rotationFinal - startRotation;
      const duration = 4000 + Math.random() * 1500; // ms
      const startTime = performance.now();
      const animate = (now) => {
        const elapsed = now - startTime;
        const t = Math.min(elapsed / duration, 1);
        const eased = easeOutCubic(t);
        this.rotation = startRotation + delta * eased;
        this.draw();
        if (t < 1) {
          this.frame = requestAnimationFrame(animate);
        } else {
          this.isSpinning = false;
          // Normalize rotation within 0..2pi
          this.rotation = ((this.rotation % (Math.PI*2)) + Math.PI*2) % (Math.PI*2);
          this.draw();
          // Compute final winner index again from rotation
          // finalAngle: the angle of the segment at pointer (0 at right, +counterclockwise). We compute a normalized angle that maps to segment index.
          const finalAngle = ((-this.rotation - Math.PI/2) % (Math.PI*2) + Math.PI*2) % (Math.PI*2);
          const resultingIndex = Math.floor((finalAngle / (Math.PI*2)) * count) % count;
          const winner = this.names[resultingIndex];
          this.onResult({ index: resultingIndex, name: winner });
        }
      };
      this.frame = requestAnimationFrame(animate);
    }
  }
  // Helper: pick readable text color for a background
  function getTextColor(hex) {
    // remove # and convert
    const h = hex.replace('#','');
    const r = parseInt(h.substring(0,2),16);
    const g = parseInt(h.substring(2,4),16);
    const b = parseInt(h.substring(4,6),16);
    // luminance
    const lum = (0.299*r + 0.587*g + 0.114*b) / 255;
    return lum > 0.65 ? '#111' : '#fff';
  }
  // Helper: wrap text within a given width (draws multi-line if necessary)
  function wrapFillText(ctx, text, x, y, maxWidth, lineHeight) {
    const words = (text || '').split(/\s+/);
    if (words.length === 0) return;
    let line = '';
    const lines = [];
    for (let n = 0; n < words.length; n++) {
      const testLine = line ? line + ' ' + words[n] : words[n];
      const metrics = ctx.measureText(testLine);
      if (metrics.width > maxWidth && line) {
        lines.push(line);
        line = words[n];
      } else {
        line = testLine;
      }
    }
    if (line) lines.push(line);
    // If still too many lines, just draw what's possible (we rely on font size)
    for (let i=0;i<lines.length;i++){
      ctx.fillText(lines[i], x, y + (i - (lines.length-1)/2) * lineHeight);
    }
  }
  // UI glue
  document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('wheelCanvas');
    const wheel = new Wheel(canvas, { theme: 'light', onResult: onWinner });
    const nameInput = document.getElementById('nameInput');
    const addBtn = document.getElementById('addBtn');
    const addRandomBtn = document.getElementById('addRandomBtn');
    const bulkInput = document.getElementById('bulkInput');
    const bulkAddBtn = document.getElementById('bulkAddBtn');
    const clearBulkBtn = document.getElementById('clearBulkBtn');
    const nameList = document.getElementById('nameList');
    const countSpan = document.getElementById('count');
    const spinBtn = document.getElementById('spinBtn');
    const rerollBtn = document.getElementById('rerollBtn');
    const clearNamesBtn = document.getElementById('clearNamesBtn');
    const themeSelect = document.getElementById('themeSelect');
    const resultSection = document.getElementById('result');
    const winnerNameDiv = document.getElementById('winnerName');
    const exportBtn = document.getElementById('exportBtn');
    const importBtn = document.getElementById('importBtn');
    const importFile = document.getElementById('importFile');
    // Initial draw
    wheel.draw();
    function updateUI() {
      const names = wheel.names;
      countSpan.textContent = names.length;
      renderNameList();
    }
    function renderNameList() {
      nameList.innerHTML = '';
      wheel.names.forEach((n, i) => {
        const li = document.createElement('li');
        const span = document.createElement('span');
        span.textContent = n;
        li.appendChild(span);
        const btn = document.createElement('button');
        btn.title = 'Remove';
        btn.setAttribute('aria-label', `Remove ${n}`);
        btn.innerHTML = '✕';
        btn.addEventListener('click', () => {
          wheel.removeName(i);
          updateUI();
        });
        li.appendChild(btn);
        nameList.appendChild(li);
      });
    }
    function addNameFromInput() {
      const v = nameInput.value.trim();
      if (!v) { showMessage('Please enter a name.', 'warn'); return; }
      wheel.addName(v);
      nameInput.value = '';
      updateUI();
    }
    addBtn.addEventListener('click', addNameFromInput);
    nameInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') addNameFromInput(); });
    addRandomBtn.addEventListener('click', () => {
      const samples = ['Alex','Jordan','Taylor','Sam','Jamie','Casey','Morgan','Riley','Avery','Dana'];
      const count = rand(3,6);
      for (let i=0;i<count;i++) wheel.addName(samples[rand(0,samples.length-1)] + (rand(1,100)));
      updateUI();
    });
    bulkAddBtn.addEventListener('click', () => {
      const text = bulkInput.value.trim();
      if (!text) { showMessage('Bulk input is empty.', 'warn'); return; }
      const parsed = text.split(/[\n,;]+/).map(s => s.trim()).filter(s => s);
      parsed.forEach(p => wheel.addName(p));
      bulkInput.value = '';
      updateUI();
      showMessage(`Added ${parsed.length} names.`, 'info');
    });
    clearBulkBtn.addEventListener('click', () => { bulkInput.value = ''; });
    spinBtn.addEventListener('click', () => {
      if (wheel.names.length === 0) { showMessage('Add at least one name to spin.', 'warn'); return; }
      resultSection.hidden = true;
      winnerNameDiv.textContent = '';
      wheel.spin();
      spinBtn.disabled = true;
      const checkFinish = setInterval(() => {
        if (!wheel.isSpinning) {
          clearInterval(checkFinish);
          spinBtn.disabled = false;
        }
      }, 200);
    });
    rerollBtn.addEventListener('click', () => {
      resultSection.hidden = true;
      wheel.spin();
    });
    clearNamesBtn.addEventListener('click', () => {
      if (confirm('Clear all names?')) {
        wheel.clearNames();
        updateUI();
      }
    });
    themeSelect.addEventListener('change', (e) => {
      const t = e.target.value;
      document.body.className = 'theme-' + t;
      wheel.setTheme(t);
    });
    function onWinner(result) {
      winnerNameDiv.textContent = result.name || '—';
      resultSection.hidden = false;
      // Flash the winner item in the list (if still present)
      const items = Array.from(nameList.children);
      items.forEach((li, idx) => { li.classList.toggle('winner', idx === result.index); });
      showMessage(`Winner: ${result.name}`, 'success', 4000);
    }
    // Simple message area
    function showMessage(text, type = 'info', duration = 2200) {
      // create small toast
      const t = document.createElement('div');
      t.className = 'tmp-toast ' + type;
      t.textContent = text;
      document.body.appendChild(t);
      // Force reflow to pick up transitions
      window.getComputedStyle(t).opacity;
      setTimeout(()=> { t.style.opacity = '0'; t.style.transform = 'translateY(-10px)'; }, duration - 300);
      setTimeout(()=> { try { t.remove(); } catch(e){} }, duration);
    }
    // Export/import CSV
    exportBtn.addEventListener('click', () => {
      if (wheel.names.length === 0) { showMessage('No names to export.', 'warn'); return; }
      const csv = wheel.names.map(n => `"${(n||'').replace(/"/g,'""')}"`).join('\n');
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'participants.csv';
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
      showMessage('Exported CSV', 'info');
    });
    importBtn.addEventListener('click', () => { importFile.click(); });
    importFile.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = (ev) => {
        const txt = ev.target.result;
        const lines = txt.split(/\r?\n/).map(s => s.trim()).filter(s => s);
        // basic CSV unquote
        const parsed = lines.map(l => {
          // simple CSV single-column parse: handle quoted fields
          if (l.startsWith('"') && l.endsWith('"')) {
            return l.slice(1,-1).replace(/""/g,'"');
          }
          return l;
        });
        parsed.forEach(p => wheel.addName(p));
        updateUI();
        showMessage(`Imported ${parsed.length} names`, 'info');
      };
      reader.readAsText(file);
      importFile.value = '';
    });
    // Initial sample (optional)
    // wheel.addName('Alice'); wheel.addName('Bob'); wheel.addName('Charlie');
    updateUI();
    // (Optional) keyboard shortcuts
    window.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        nameInput.focus();
      }
      if (e.key === ' ') {
        // space triggers spin if not focusing an input
        if (document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
          e.preventDefault();
          spinBtn.click();
        }
      }
    });
  });
})(); 