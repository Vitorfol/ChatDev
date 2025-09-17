'''
DOCSTRING:
wheel.js
Contains a Wheel class that draws the wheel on a canvas and animates spins.
Key methods:
- constructor(canvas, options)
- setNames(names)
- setTheme(theme)
- draw()
- resize() -> handle high-DPI displays
- spinToIndex(index) -> Promise resolves with index after animation
- getRandomIndex()
'''
/* A small utility to requestAnimationFrame safely (browser-provided) */
class Wheel {
  constructor(canvas, options = {}) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.names = options.names || [];
    this.colors = options.colors || ['#ffb3b3', '#ffd9b3', '#fff3b3', '#d9ffb3', '#b3ffd9', '#b3e6ff'];
    this.textColor = options.textColor || '#222';
    this.rotation = 0; // degrees
    this.font = options.font || '16px Inter, Arial';
    this.onDraw = options.onDraw || function(){};
    this._animating = false;
    // Set up high-DPI friendly canvas and metrics
    this.resize();
    // Redraw once created
    this.draw();
    // Optional: handle container resize via ResizeObserver if available
    if (window.ResizeObserver) {
      try {
        const ro = new ResizeObserver(() => this.resize());
        ro.observe(this.canvas.parentElement || this.canvas);
        this._resizeObserver = ro;
      } catch (e) {
        // ignore
      }
    } else {
      window.addEventListener('resize', () => this.resize());
    }
  }
  resize() {
    // Make the canvas crisp on high-DPI screens.
    const dpr = window.devicePixelRatio || 1;
    const rect = this.canvas.getBoundingClientRect();
    // Fallback to element width/height attributes if bounding rect is 0
    const cssWidth = rect.width || this.canvas.clientWidth || this.canvas.width / (dpr || 1);
    const cssHeight = rect.height || this.canvas.clientHeight || this.canvas.height / (dpr || 1);
    // Set backing store size
    this.canvas.width = Math.max(1, Math.round(cssWidth * dpr));
    this.canvas.height = Math.max(1, Math.round(cssHeight * dpr));
    // Keep CSS size consistent
    this.canvas.style.width = cssWidth + 'px';
    this.canvas.style.height = cssHeight + 'px';
    // Reset transform so we can set a scale for dpr
    this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    // Use CSS pixel coordinates for drawing from now on
    this.centerX = cssWidth / 2;
    this.centerY = cssHeight / 2;
    this.radius = Math.min(cssWidth, cssHeight) / 2 - 10;
    // Recompute font size based on canvas size to keep labels legible
    // If user supplied a font (with px), keep it; otherwise set a sensible value.
    if (!this.font || typeof this.font !== 'string') {
      this.font = Math.max(12, Math.round(this.radius * 0.06)) + 'px Inter, Arial';
    } else {
      // keep user's font but ensure text scale reasonable
      // (we don't attempt to parse px here; leaving as provided)
    }
    this.draw();
  }
  setNames(names) {
    this.names = names.slice();
    this.draw();
  }
  setTheme(theme) {
    if (!theme) return;
    if (theme.colors && theme.colors.length) this.colors = theme.colors.slice();
    if (theme.text) this.textColor = theme.text;
    this.draw();
  }
  clearCanvas() {
    // Clear the visible canvas area (CSS pixels)
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
  }
  draw() {
    this.clearCanvas();
    const ctx = this.ctx;
    const n = Math.max(1, this.names.length);
    const seg = 360 / n;
    ctx.save();
    // Translate to center using CSS pixel coordinates
    ctx.translate(this.centerX, this.centerY);
    ctx.rotate(this.degToRad(this.rotation));
    // Draw segments
    for (let i = 0; i < n; i++) {
      const start = this.degToRad(i * seg);
      const end = this.degToRad((i + 1) * seg);
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.arc(0, 0, this.radius, start, end);
      ctx.closePath();
      ctx.fillStyle = this.colors[i % this.colors.length];
      ctx.fill();
      // stroke
      ctx.lineWidth = Math.max(1, this.radius * 0.008);
      ctx.strokeStyle = 'rgba(0,0,0,0.08)';
      ctx.stroke();
      // Draw label
      ctx.save();
      const angle = start + (end - start) / 2;
      ctx.rotate(angle);
      ctx.translate(this.radius * 0.55, 0);
      ctx.rotate(Math.PI / 2);
      ctx.fillStyle = this.textColor;
      // Set font size relative to radius if not provided precisely
      ctx.font = this.font;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      const name = this.names[i] || '';
      this.wrapText(ctx, name, 0, 0, this.radius * 0.35, parseInt(Math.max(12, this.radius * 0.06), 10));
      ctx.restore();
    }
    ctx.restore();
    // center circle
    ctx.beginPath();
    ctx.arc(this.centerX, this.centerY, this.radius * 0.12, 0, Math.PI * 2);
    // Fill with background-like color; allow theme override by drawing over it in CSS if necessary
    ctx.fillStyle = '#ffffff';
    ctx.fill();
    ctx.lineWidth = Math.max(1, this.radius * 0.008);
    ctx.strokeStyle = 'rgba(0,0,0,0.06)';
    ctx.stroke();
    this.onDraw();
  }
  wrapText(ctx, text, x, y, maxWidth, lineHeight) {
    // A simple wrap for canvas text
    const words = String(text).split(' ');
    let line = '';
    let yOffset = y;
    for (let n = 0; n < words.length; n++) {
      const testLine = line + words[n] + ' ';
      const metrics = ctx.measureText(testLine);
      const testWidth = metrics.width;
      if (testWidth > maxWidth && n > 0) {
        ctx.fillText(line.trim(), x, yOffset);
        line = words[n] + ' ';
        yOffset += lineHeight;
      } else {
        line = testLine;
      }
    }
    ctx.fillText(line.trim(), x, yOffset);
  }
  degToRad(d) {
    return d * Math.PI / 180;
  }
  radToDeg(r) {
    return r * 180 / Math.PI;
  }
  getRandomIndex() {
    if (!this.names.length) return 0;
    return Math.floor(Math.random() * this.names.length);
  }
  // Spin such that the segment at `index` lands on the pointer at top.
  spinToIndex(index, opts = {}) {
    if (this._animating) return Promise.reject('Already animating');
    if (!this.names.length) return Promise.reject('No names');
    const n = this.names.length;
    const segAngle = 360 / n;
    // Normalize current rotation to [0, 360)
    const normalized = ((this.rotation % 360) + 360) % 360;
    // Center of segment i is at angle: (i * segAngle + segAngle/2)
    const centerAngle = index * segAngle + segAngle / 2;
    // We want (centerAngle + rotation) mod 360 = 270 (pointing upward if pointer is at top)
    let targetRotation = 270 - centerAngle;
    targetRotation = ((targetRotation % 360) + 360) % 360;
    const fullSpins = opts.fullSpins !== undefined ? opts.fullSpins : (3 + Math.floor(Math.random() * 3)); // 3-5 spins
    const endRotation = targetRotation + fullSpins * 360 + (opts.randomOffset || 0);
    const startRotation = normalized;
    const delta = endRotation - startRotation;
    const duration = opts.duration || 5000; // ms
    const startTime = performance.now();
    this._animating = true;
    return new Promise((resolve) => {
      const animate = (now) => {
        const elapsed = now - startTime;
        const t = Math.min(1, elapsed / duration);
        // ease out cubic
        const eased = 1 - Math.pow(1 - t, 3);
        const current = startRotation + delta * eased;
        this.rotation = current;
        this.draw();
        if (t < 1) {
          requestAnimationFrame(animate);
        } else {
          this._animating = false;
          // Normalize rotation to endRotation mod 360
          this.rotation = ((endRotation % 360) + 360) % 360;
          this.draw();
          resolve(index);
        }
      };
      requestAnimationFrame(animate);
    });
  }
}