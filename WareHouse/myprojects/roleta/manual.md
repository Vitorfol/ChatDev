manual.md

# Random Winner Wheel — User Manual

Random Winner Wheel is a small, accessible, browser-based web app that lets you collect participant names and spin a visual wheel to randomly pick a winner. It is built with plain HTML, CSS and JavaScript, and requires no external libraries or build tools. The UI supports multiple themes, import/export of participant lists, keyboard shortcuts, and basic accessibility features.

Contents
- Overview
- What’s included (file list)
- System requirements & dependencies
- Quick start (run locally)
- Deploying (static hosting / GitHub Pages)
- Walkthrough — main features & UI
  - Adding names (single, sample, bulk)
  - Editing/removing names
  - Spinning and rerolling
  - Theme selection
  - Import / Export (CSV)
  - Keyboard shortcuts & accessibility
- Developer guide / Customization
  - How wheel chooses a winner (algorithm)
  - Changing theme palettes
  - Exposing the Wheel instance for scripting
  - Tuning animation & wheel appearance
  - File structure & key functions
- Troubleshooting & FAQs
- License & contact

---

Overview
A lightweight interactive wheel you can use for classroom raffles, team giveaways, decision-making, and more. Enter names manually or import them, spin the wheel, and see the winner highlighted.

What’s included (file list)
- index.html — Main page and UI.
- styles.css — All UI and theme styling.
- script.js — Wheel implementation and UI glue code.
- manual.md — This file.

System requirements & dependencies
- A modern web browser (Chrome, Firefox, Edge, Safari).
- No frameworks or packages required.
- Optional: a small static HTTP server if you prefer to serve rather than opening the file directly (recommended for import file handling in some browsers).

Quick start (run locally)
1. Download or clone the project files into a folder.
2. Open index.html directly in the browser, or run a simple static server:

- Using Python 3 (recommended):
  - In a terminal at the project folder:
    - python -m http.server 8000
  - Visit http://localhost:8000 in your browser.

- Using Node (http-server):
  - npm install -g http-server
  - http-server . -p 8000
  - Visit http://localhost:8000.

- Open index.html file directly:
  - Double-click index.html (works in most browsers). Some browsers restrict local file imports (CSV import), so serving via a simple HTTP server is safer.

Deploying (static hosting / GitHub Pages)
- This is a static site: upload the files to any static hosting provider (GitHub Pages, Netlify, Vercel, Surge, S3 + CloudFront).
- To host on GitHub Pages:
  - Create a repository and push the files.
  - Enable GitHub Pages on the repository (source: main branch root).
  - Access at https://<your-username>.github.io/<repo>.

Walkthrough — main features & UI

Main layout
- Header: Title and short description.
- Controls area: Single add, sample/random add, bulk add area, theme selector, spin/clear/import/export controls.
- Wheel area: Circular canvas with a pointer at the top.
- Participants list: Shows all added names with remove buttons and participant count.
- Result panel: Shows the winner after a spin and a "Spin Again" option.

Adding names
- Single add:
  - Type a name into the "Enter a name" input, press Add or hit Enter.
- Add sample:
  - Click "Add Sample" to add a small random batch of sample names (convenient for testing).
- Bulk add:
  - Paste or type multiple names into the bulk textarea separated by commas, semicolons, or newlines (e.g., "Alice, Bob; Charlie\nDana").
  - Click "Bulk Add".
  - The app trims, filters empty entries, and adds each name.

Editing/removing names
- Each participant in the list has a small ✕ button to remove that individual.
- "Clear Names" clears all participants (a confirmation prompt appears).

Spinning and rerolling
- Click "Spin" to animate the wheel and randomly pick a winner.
- While the wheel is spinning, the Spin button is temporarily disabled.
- After the spin completes, the winner is shown in the "Winner" section and the corresponding participant list entry is highlighted.
- Click "Spin Again" to reroll (the app chooses a new random outcome).

Theme selection
- Use the Theme dropdown to switch UI themes: Light, Dark, Neon, Pastel, Retro.
- Themes affect both page CSS variables and the wheel segment color palette.

Import / Export (CSV)
- Export: Click "Export CSV" to download the current list as a CSV file (one column, one name per line).
- Import: Click "Import CSV" and choose a CSV file (or text file). The app supports a single column per line, with quoted values (basic CSV).
- Note: Some browsers restrict file access when opening index.html locally — if CSV import fails, run a local static server.

Keyboard shortcuts & accessibility
- Ctrl/Cmd + K: Focus the name input for quick typing.
- Space: If not focused on an input/textarea, pressing Space triggers a spin.
- ARIA: The participants list and result area use aria-live attributes to notify assistive tech of changes.
- Pointer: A visual triangular pointer sits at the top of the wheel; the winner segment aligns with the pointer when spinning completes.

Developer guide / Customization

File structure & key functions
- script.js contains:
  - Wheel class — core drawing, spin animation, name management.
    - Methods: setNames, addName, removeName, clearNames, setTheme, draw, spin.
    - Constructor accepts options: { theme, onResult } where onResult receives { index, name }.
  - THEME_PALETTES — color palettes used per theme.
  - UI glue code inside DOMContentLoaded — connects DOM elements to Wheel calls and handles export/import, messages, etc.
- styles.css contains:
  - Theme variables controlled by body.theme-<name>.
  - Layout, responsive rules, toast styles, and wheel canvas appearance.

How the wheel chooses a winner (algorithm)
- The wheel divides the circle into N equal segments (N = number of participants).
- For a chosen winner index i, the code computes the mid-angle of the segment: segmentMid = ((i + 0.5)/N) * 2π.
- It computes a final rotation so the chosen segment mid-angle ends up under the fixed top pointer. Extra full rotations (random 5–8 spins) are added to make the spin feel natural.
- The animation uses an ease-out cubic easing for smooth deceleration.
- After animation, the code normalizes rotation and computes the resulting index from final rotation to confirm the winner.

Changing theme palettes
- Palette array: THEME_PALETTES in script.js maps theme id to an array of colors. Example:
  - light: ['#FF8A80', '#FFD180', ...]
- To add or modify theme colors, edit THEME_PALETTES.
- To add a new theme visually for the page, add a new body.theme-<id> block in styles.css with CSS variables (--bg, --fg, --accent, etc.), and add a matching option in the Theme select in index.html.

Exposing the Wheel instance for scripting
- By default the wheel instance is scoped to the script’s DOMContentLoaded closure.
- To access it in the browser console for debugging or programmatic control, modify script.js after wheel creation:
  - window.wheel = wheel;
- After that you can run commands in console:
  - wheel.addName('Zoe');
  - wheel.setTheme('dark');
  - wheel.spin();

Tuning animation & wheel appearance
- Animation duration: set duration variable in wheel.spin (currently 4000–5500ms).
- Extra turns: change rand(5,8) to fewer or more spins.
- Padding between segments: Wheel.padAngle (radians).
- Center circle size and font sizing are computed relative to canvas radius; adjust draw() if you want different sizing or font.

Saving state (optional)
- The example doesn’t persist names across sessions. To add persistence:
  - Use localStorage: on every add/remove/update, store JSON.stringify(wheel.names) to localStorage.
  - On DOMContentLoaded, read and restore if present.
  - Example (conceptual):
    - localStorage.setItem('wheel_names', JSON.stringify(wheel.names));
    - const saved = JSON.parse(localStorage.getItem('wheel_names') || '[]'); wheel.setNames(saved);

Troubleshooting & FAQs

Q: The wheel canvas is blank / not drawing!
- Make sure JavaScript is enabled.
- Ensure the canvas is visible on screen (some CSS rules or hidden parents can give a zero bounding rectangle; the script uses fallback width/height attributes).
- If the page is served via file:// you might have import restrictions, but drawing itself should still work.
- Open the browser console for errors.

Q: CSV import/export isn’t working when I open the file directly.
- Some browsers (Chrome especially) block file:// handling for security. Run a simple local HTTP server (see Quick start) and try again.

Q: I want to make the wheel fair — is it truly random?
- The selection uses Math.random-based seeding to pick a winner index and a random number of full rotations. Math.random is not cryptographically secure but is suitable for casual selections and giveaways. For higher guarantees, integrate a cryptographic RNG or server-side selection.

Q: How do I change text styles, fonts or the pointer shape?
- Edit styles.css for pointer look and font-family, or change the pointer HTML/CSS. The pointer is a CSS triangle positioned absolutely above the canvas.

Q: I want labels to wrap or use smaller fonts for long names — how?
- The wheel uses wrapFillText and sets dynamic font size relative to radius. For more control, adjust the font size computation in script.js draw() (ctx.font = ...).

FAQ: Accessibility
- The UI includes aria-live on the participant list and result area so screen readers receive updates. If you need further accessibility support:
  - Add aria-labels to interactive items.
  - Add a non-visual log of recent winners (text history) for assistive tech.
  - Consider keyboard-only operation improvements: add focus states, ensure buttons are reachable via tab order.

Extending the app
- Add new themes: edit styles.css and THEME_PALETTES.
- Save/Load presets: add UI to save palettes/names to JSON and fetch them later.
- Analytics or audit trail: append spin results to a list and store in localStorage or send to a server.
- Multi-wheel or weight support: modify wheel logic to accept weights per name (segment size proportional to weight) — this requires updating segment angle calculation and mapping of finalAngle to index.

Sample workflow / quick demo
1. Open the site in your browser (http://localhost:8000).
2. Click the name field, type "Alice", press Enter.
3. Click "Bulk Add", paste "Bob, Charlie, Dana" and click Bulk Add.
4. Choose "Neon" from Theme dropdown to preview wheel colors.
5. Click "Spin". Wait for the wheel to stop and see the winner shown in the Result panel and highlighted in the participant list.
6. Click "Export CSV" to download the current list; or "Import CSV" to load another set.

Developer notes (internal)
- The Wheel class redraws the canvas on each rotation frame. Device pixel ratio is honored by _devicePixelRatioFix().
- The winner computation uses angles with the pointer oriented at top (-π/2 alignment).
- The code tries to be resilient to zero-sized canvas by using fallback attributes.

Troubleshooting quick checklist
- Canvas blank: ensure canvas exists and is visible; resize can trigger re-draw.
- Spin button stuck disabled: check wheel.isSpinning in console; a race condition may exist if you interrupt the animation.
- CSV malformed: Export uses simple one-column CSV; imports parse single-column lines and basic quoted fields.

License & contact
- This project is a small utility demo — update or add a license file in your repo as needed (MIT is a common choice).
- For product questions, integration help, or feature requests, contact your project team (or add an issues tracker in the repo).

Changelog (example)
- v1.0 — Initial build: wheel drawing, spin animation, themes, CSV import/export, basic accessibility.

Thank you for using Random Winner Wheel. If you want, we can:
- Add persistent storage (localStorage or cloud save).
- Add weighted chances or multi-winner support.
- Create a printable or shareable "result" link after a spin.
Tell us which features you'd like next and we'll prioritize them.