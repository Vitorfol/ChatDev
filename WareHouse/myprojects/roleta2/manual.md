# Wheel of Names — User & Developer Manual

A small, responsive web app (Flask + HTML5 Canvas + vanilla JS) to enter names, pick one at random with a spinning wheel, and switch between visual themes.

This manual explains what the app does, how to install and run it, how to use the UI, how to customize themes and appearance, and how to deploy and troubleshoot the application.

---

Table of contents
- Overview
- Main features
- Requirements
- Quick install (local development)
- Run locally
- File / code overview
- How to use (user guide)
- Theme management (add / edit themes)
- Customization & development notes
- Deployment recommendations (production)
- Troubleshooting & FAQ
- Security & accessibility notes
- License & credits

---

Overview
--------
Wheel of Names is a simple, self-contained web app that lets you:
- Add names (one-per-line or single add),
- Visualize them as segments on a circular wheel,
- Spin the wheel with an animated rotation and land on a randomly selected winner,
- Change the application's look by selecting different themes (colors/background/text),
- Import/export name lists and load sample data.

The UI uses a canvas to draw and animate the wheel. Themes are supplied as JSON (themes.json) and applied at runtime.

Main features
-------------
- Add names via input or paste a newline-separated list.
- Load a sample set of names, import from clipboard/prompt, or export a text file.
- Responsive, high-DPI friendly canvas rendering.
- Theme selector with multiple built-in themes (editable via themes.json).
- Smooth spin animation with easing and configurable duration / spin count.
- Result displayed prominently after spin.

Requirements
------------
- Python 3.8+ (recommended)
- Flask (for the simple web server)
- Browser with Canvas and basic JavaScript support (modern Chrome, Firefox, Edge, Safari, etc.)

Optional (for production):
- gunicorn (or another WSGI server) if you want to run the app in production.
- Docker (if you prefer containerized deployment).

Quick install (local development)
---------------------------------
1. Clone or copy the project into a directory.
2. Create and activate a virtual environment (recommended):

   On macOS / Linux:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

   On Windows (PowerShell):
   ```
   python -m venv venv
   venv\Scripts\Activate.ps1
   ```

3. Install Flask:
```
pip install flask
```

(Optionally install gunicorn for production testing: `pip install gunicorn`)

Run locally
-----------
Start the application:

```
python main.py
```

By default the app listens on http://127.0.0.1:5000/ (or 0.0.0.0:5000 when running directly as in main.py). You can override the port with the PORT environment variable:

Linux / macOS:
```
PORT=8080 python main.py
```

Windows (PowerShell):
```
$env:PORT=8080; python main.py
```

When running locally you should see Flask logs and be able to open the app in your browser.

File / code overview
--------------------
Top-level files in the repo:

- main.py
  - Small Flask application that serves templates and static files.
  - Route: `/` -> renders `templates/index.html`.
  - Uses the standard Flask `static` folder (serves `static/*`).

- templates/index.html
  - The main HTML file; contains the UI structure, includes CSS and JS.
  - Injects `window.THEMES_JSON_URL` using Flask's `url_for('static', filename='themes.json')` so JS can fetch themes reliably.

- static/themes.json
  - JSON array of themes. Each theme object contains:
    - id: machine identifier (string)
    - name: display name
    - bg: page background color (hex)
    - text: primary text color (hex)
    - accent: accent color used for pointer / button (hex)
    - colors: array of segment colors used for wheel segments

- static/css/styles.css
  - CSS variables and styles for layout and responsive design.
  - Uses CSS custom properties (--bg, --text, --accent, --panel-bg) that are updated by JS when themes change.

- static/js/wheel.js
  - Wheel class that draws the wheel on a canvas and animates spins.
  - Main APIs:
    - constructor(canvas, options)
    - setNames(names)
    - setTheme(theme) — (expects {colors: [...], text: '#...'})
    - draw()
    - resize()
    - spinToIndex(index, opts) -> Promise that resolves when animation completes
    - getRandomIndex() -> integer
  - Handles high-DPI displays by scaling backing store and CSS size.

- static/js/main.js
  - Wires the DOM controls to the Wheel instance.
  - Loads themes.json using `window.THEMES_JSON_URL`.
  - Handles add/enter, import/export, clear, load sample, theme selection, and spin logic.

How to use (user guide)
-----------------------
Open the app in a browser.

Main UI elements:
- Add name field: type a single name and click "Add" or press Enter.
- Names textarea: edit the full list (one name per line). The wheel updates automatically as you change this list.
- Load Sample: populates the textarea with example names.
- Clear: empties the names list.
- Import: paste a newline-separated list when prompted (simple import).
- Export: downloads the current names as `names.txt`.
- Theme selector: pick a theme to change colors and background.
- SPIN button: initiates the spin animation and picks a random winner.
- Result box: shows the winner after the spin.

Step-by-step example:
1. Type or paste names in the textarea or use the Add field.
2. Optionally change the theme in the theme dropdown.
3. Press "SPIN". The spin button becomes disabled and shows "Spinning..." while the wheel animates.
4. After the animation completes, the chosen name is displayed in the result area.

Spin details:
- The JS picks a random index via wheel.getRandomIndex(), then calls wheel.spinToIndex(index).
- spinToIndex() runs a 3–5 full-spins easing animation by default and lands so the chosen segment lines up with the pointer at the top.
- Duration is configurable in code (default uses 4500 ms in main.js; wheel.spinToIndex accepts an `opts` object with `duration`, `fullSpins`, and `randomOffset`).

Theme management (add / edit themes)
-----------------------------------
Themes live in `static/themes.json`. Each entry looks like:

```json
{
  "id": "classic",
  "name": "Classic",
  "bg": "#ffffff",
  "text": "#222222",
  "accent": "#007bff",
  "colors": ["#ffb3b3", "#ffd9b3", "#fff3b3", "#d9ffb3"]
}
```

To add a new theme:
1. Edit `static/themes.json` and add a new object to the array.
2. Give it a unique `id` and a `name`.
3. Provide `bg`, `text`, `accent` hex values and a `colors` array for wheel segments.
4. Save file and refresh the browser. The theme selector will show the new theme.

Notes:
- The app fetches themes.json on page load; if the fetch fails it falls back to a built-in default theme (so the app still works).
- Colors are applied by JS — `--bg`, `--text`, `--accent`, and `--panel-bg` CSS variables are updated.
- `panel-bg` is computed from `bg` to provide a slightly contrasting panel background (JS uses a small lighten/darken helper in main.js). If you prefer full control, modify CSS or modify the theme application code.

Customization & development notes
---------------------------------
Common customizations:
- Change default sample names in `main.js` (the `loadSampleBtn` handler).
- Change initial names loaded at launch at the bottom of `main.js` (initial `namesTextarea.value`).
- Change spin duration or spin behavior: modify the `duration` parameter passed to `wheel.spinToIndex()` in `main.js` (default `4500` ms in the example).
- Change number of full spins: pass `fullSpins` in `spinToIndex(index, { fullSpins: 5, duration: 5000 })`.

Wheel class API (quick reference)
- new Wheel(canvas, options)
  - options:
    - names: array of strings
    - colors: array of hex strings (segment colors)
    - textColor: color for text labels
    - font: CSS font string for canvas text
    - onDraw: callback executed after draw()
- setNames(names) — set the array of names and redraw
- setTheme(theme) — set colors and text color (expects an object containing `colors` and `text`)
- draw() — force a redraw
- resize() — recalculate metrics for the current canvas size and redraw
- getRandomIndex() — returns an integer in [0, names.length)
- spinToIndex(index, opts) — spins to the given index and returns a Promise that resolves with the index when done
  - opts may contain: duration (ms), fullSpins (integer), randomOffset (degrees)

Canvas scaling and high-DPI:
- wheel.resize() computes backing-store size to match devicePixelRatio so the canvas looks crisp on retina / high-DPI displays.
- The resizing logic is executed at startup and on window resize (and via ResizeObserver if available).

Development tips
- Static assets live under `static/`. Edit JS or CSS and refresh the page. In production consider adding cache headers or fingerprinting for cache busting.
- To test changes to `themes.json`, save the file and refresh. If browser caches the JSON, reload with cache disabled (DevTools) or configure Flask to send cache-control headers.

Deployment (production)
----------------------
Minimal production recommendations:
- Do not run Flask's builtin server with `debug=True` in production. In `main.py`, set `debug=False` and use a real WSGI server (gunicorn, uwsgi, etc.)
- Example with gunicorn:
  ```
  pip install gunicorn
  gunicorn -b 0.0.0.0:8000 main:create_app()
  ```
- Or create a small wrapper for production:
  ```
  export FLASK_APP=main.py
  flask run --host=0.0.0.0 --port=8000
  ```
  (still not recommended for high load)

Docker example
--------------
Basic Dockerfile (example)

```
FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir flask gunicorn
ENV PORT=8000
EXPOSE 8000
CMD ["gunicorn", "-b", "0.0.0.0:8000", "main:create_app()"]
```

Troubleshooting & FAQ
---------------------
Q: The wheel is blank or names don't show after editing textarea.
- A: Make sure you have at least one non-empty line in the textarea. The wheel draws segments for the count returned by parsing the textarea (trimmed non-empty lines). If the canvas appears small or not updated, reload the page. Resize events trigger redraws.

Q: Themes aren't loading; I see a console error about fetching themes.json.
- A: The app attempts to fetch `window.THEMES_JSON_URL`, injected via Flask. If you serve the app under a subpath or are hosting static files elsewhere, ensure the URL is correct. Check browser console network tab. The app has a fallback theme and will continue to work.

Q: The pointer doesn't match segments or winner doesn't align precisely.
- A: The Canvas rotation and pointer alignment assume the pointer is visually at the top (270 degrees alignment in the code). If you change pointer position or rotation, adjust the calculation in wheel.spinToIndex().

Q: How can I change the spin feeling (ease / duration)?
- A: Modify the easing or `duration` used in spinToIndex or the argument passed from main.js when calling spinToIndex(index, { duration: 4500, fullSpins: 4 }).

Q: I want more advanced import/export or real persistence.
- A: Add an API endpoint in main.py to persist names server-side (POST/GET endpoints) and wire the JS to call those endpoints. For a simple file-based persistence, write to a JSON file in the static or data folder (careful with concurrency and security).

Accessibility notes
-------------------
- The result area uses `aria-live="polite"` so screen readers are notified when a winner is shown.
- The theme selector benefits from sufficient contrast — make sure custom themes have readable text vs background colors.
- The pointer element is marked `aria-hidden="true"`, as the result is announced in the result box. Button labels and form controls are standard HTML elements (accessible by keyboard).
- Keyboard usage:
  - Focus the name input and press Enter to add a name.
  - Use Tab to move between controls; the main "SPIN" is a button and can be activated with Enter / Space.

Security notes
--------------
- This app is a static client-side app with simple Flask static serving. If you add server-side persistence or file upload features, validate and sanitize inputs.
- If you expose the app to the public internet, run behind a secure reverse proxy (HTTPS), set appropriate CORS and CSP headers if needed, and avoid running with debug enabled.

Extending the app
-----------------
- Add analytical logging (e.g., track how often spin is pressed, which names are picked).
- Add repeat-safe selection modes (e.g., remove a name once it has been chosen).
- Add the ability to pin a winner or mark segments with weights.
- Add localization by using texts as localized strings in a small translation file loaded by main.js.

Example: Add weights
- Modify the wheel.getRandomIndex() to choose indexes proportionally to weights associated with names (e.g., read weights from a second column or UI control).

Contributing / Development workflow
-----------------------------------
- Edit JS/CSS/HTML under `static/` and `templates/`, then refresh the browser to preview.
- For larger changes consider using a bundler/build pipeline for minifying / transpiling assets, but the current app is intentionally dependency-free on the front end for simplicity.

License & credits
-----------------
- This manual and the sample app are provided as-is (no warranty). If you adapt the project, please include credits as you see fit.
- The app uses plain HTML/CSS/JS on the client and Flask on the server.

Contact & support
-----------------
If you need help integrating this into a larger product, or want production hardening and feature additions (e.g., persistence, user sessions, theming UI), reach out to your development team or modify the code locally.

---

Appendix: Useful commands summary
- Create venv:
  - `python3 -m venv venv`
- Activate venv:
  - macOS/Linux: `source venv/bin/activate`
  - Windows (PowerShell): `venv\Scripts\Activate.ps1`
- Install:
  - `pip install flask`
- Run:
  - `python main.py`
- Prod with gunicorn:
  - `pip install gunicorn`
  - `gunicorn -b 0.0.0.0:8000 main:create_app()`
- Build & run with Docker: create Dockerfile (example above), then `docker build -t wheel-of-names .` and `docker run -p 8000:8000 wheel-of-names`.

If you'd like, I can:
- produce a sample Dockerfile or docker-compose.yml tuned to this app,
- create a quick `requirements.txt` or `setup.py`,
- generate a small demo script to persist selected winners to disk,
- or write a short unit-test harness for the JavaScript wheel logic (using headless browser / Puppeteer) — tell me which you'd prefer next.