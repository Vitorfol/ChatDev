manual.md

# Robot-Food Simulation — User & Developer Manual

A small Python application that simulates robots navigating a 4×4 grid trying to find food while interacting with obstacles (Bombs and Rocks). The application provides a simple GUI (Tkinter) to run user-controlled and automatic simulations, with options for "intelligent" robots that avoid repeating invalid moves.

This manual explains how to install and run the software, how to use the UI and modes, describes the main features and behaviors, and provides developer notes for extending or modifying the system.

---

Table of contents
- Quick summary
- Requirements & installation
- Run the app
- UI overview and controls
  - Modes
  - Controls & interaction
  - Log and visualization
- Game objects and behaviors
  - Robots (Robo and RoboInteligente)
  - Movement: string vs integer overloads
  - Obstacles: Bomb and Rock
  - Food
  - Exceptions: MovimentoInvalidoException
- Typical usage examples (workflows)
- Configuration & customization
- Developer notes (code structure & APIs)
- Troubleshooting
- License & acknowledgements

---

Quick summary
-----------
- What it does: Visualizes robots moving on a 4×4 board, detects collisions with obstacles, tracks valid/invalid moves, and ends when food is found or robots explode.
- Interface: Tkinter GUI (mouse + keyboard + buttons).
- Primary features: user-controlled single robot, random single-robot runs, random multi-robot runs, intelligent robots (try alternative moves when an initial move is invalid), visual logging, animation delay control.

---

Requirements & installation
-----------
Minimum:
- Python 3.8+ (3.9/3.10/3.11 recommended)
- Tkinter (bundled with many Python distributions; install separately on some Linux distros)

No external pip packages are required by the provided code.

Install steps
1. Create and activate a virtual environment (recommended)
   - POSIX (Linux/macOS)
     - python3 -m venv venv
     - source venv/bin/activate
   - Windows (PowerShell)
     - python -m venv venv
     - .\venv\Scripts\Activate.ps1

2. Ensure tkinter is present:
   - macOS: Tkinter is usually present when Python is installed from the official installers.
   - Windows: Tkinter is usually included in standard Python installers.
   - Ubuntu / Debian:
     - sudo apt update
     - sudo apt install python3-tk
   - Fedora:
     - sudo dnf install python3-tkinter
   - If tkinter is missing, install the appropriate OS package or use a Python distribution that includes Tk.

3. (Optional) Install development tools:
   - pip install black flake8 pytest  # for linting/testing if you want

Files in the project
- main.py — Application entry point: constructs and runs the GUI.
- ui.py — Tkinter GUI: drawing the board, controls, and simulation loop.
- game.py — Game logic & board management: DIRS, Game class.
- models.py — Data models: MovimentoInvalidoException, Robo, RoboInteligente, Obstacle (abstract), Bomb, Rock.

---

Run the app
-----------
From the project root, with your environment active:

python main.py

This opens a window showing a 4×4 grid, control pane, and a log panel.

If you prefer to run the GUI script directly:

python -m main

(Equivalent if main.py is executed as the module entry point.)

---

UI overview and controls
-----------

Main layout
- Left: Board canvas (4×4 grid). Robots, obstacles, and food are drawn.
- Right: Controls and options (choose modes, toggle intelligent robots, animation delay, start simulations).
- Bottom/right: Text log shows actions and robot status lines.

Important controls
- Options
  - Intelligent Robots (RoboInteligente) toggle — if checked, newly added robots will be created as RoboInteligente (they will try alternative directions when an attempted move is invalid).
  - Number of Robots — set count for multi-robot random simulations (1–4).
  - Animation delay slider (ms) — delay between automatic rounds (affects automatic/random multi runs).

- Modes (buttons)
  - User-controlled (Single Robot) — reset board and place a single robot you can control with arrow keys or Move buttons.
  - Random Single Robot — simulates one robot making random moves.
  - Random Multiple Robots — simulates many robots (1–4) making random moves each round.

- Movement (User) — clickable buttons:
  - ↑ Up, ← Left, Right →, ↓ Down — send a string-direction move command to the selected robot.
- Step Random Move — in any state, perform a single step for all active robots (each chooses one random direction).
- Reset Board — reset the board: place food and two obstacles (a Bomb and a Rock) at random positions (not on the food), clear robots.

Selecting robots
- Click on a robot in the canvas to select it (highlighted).
- You can then use arrow keys or the Move buttons to send string-move commands to that robot.

Keyboard controls
- Arrow keys: Up/Down/Left/Right — equivalent to clicking the corresponding Move buttons (works for the selected robot).

Animation and logging
- The app logs actions into the text area (moves, invalid moves, robot statuses).
- The animation delay slider controls the automatic random simulation pacing (in milliseconds).

---

Game objects and behaviors
-----------

1) Grid
- Default size: 4 × 4 (rows indexed 0..3, columns 0..3).
- Coordinates are (row, column) or (x, y) in code; x is row, y is column.

2) Robots
- Two classes:
  - Robo: base robot.
  - RoboInteligente: subclass overriding move behavior to avoid repeating the same invalid move attempt — if a preferred move is invalid, it tries other directions until one succeeds or all fail.
- Each robot tracks:
  - id: integer
  - x, y: current coordinates
  - color: visualization color
  - previous_position: previously occupied cell (used when a Rock pushes the robot back)
  - exploded: boolean flag if the robot exploded (Bomb)
  - valid_moves / invalid_moves counters

3) Movement methods
- move(direction, game): accepts string direction — "UP", "RIGHT", "DOWN", "LEFT" (case-insensitive).
  - Checks bounds and whether target cell is occupied by a living robot.
  - On success, updates previous_position and current coordinates; increments valid_moves.
  - On invalid attempts, increments invalid_moves and raises MovimentoInvalidoException.
  - After a successful move, calls game.apply_interaction(robot) to handle obstacle interaction and then game.check_food(robot).
- move_code(code, game): accepts integer code 0..3
  - Mapping: 0=UP, 1=RIGHT, 2=DOWN, 3=LEFT (consistent ordering).
  - This is an "overload" style interface to demonstrate the integer variant.
- RoboInteligente overrides move so if the preferred direction fails it tries other directions until one succeeds.

4) Obstacles
- Abstract class Obstacle: subclasses implement interact(robot, game).
- Bomb:
  - When a robot steps onto a Bomb, the robot explodes.
  - The robot is flagged exploded (game.remove_robot(robot) is called), and the bomb is removed from the board.
  - The robot remains in the robot list (exploded = True) so the canvas shows an "X".
- Rock:
  - When a robot steps onto a Rock, the rock pushes the robot back to its previous position (if available). The rock remains.

5) Food
- Placed at a cell via game.place_food(x, y).
- When a robot moves onto the food, game.found_food becomes True and the simulation ends or reports the finding.
- The UI shows a green circle on the food cell.

6) Exceptions
- MovimentoInvalidoException raised when:
  - Move is out of bounds,
  - Cell is occupied by another living robot,
  - Robot has exploded (cannot move),
  - Invalid direction code or string provided.
- RoboInteligente catches movement exceptions internally while trying other directions; only if all directions fail will it raise MovimentoInvalidoException.

---

Typical usage examples
-----------

1) Play manually (user-controlled)
- Launch app: python main.py
- Click "User-controlled (Single Robot)".
- Select the robot (it may be auto-selected); press arrow keys or Move buttons to move the robot.
- If the robot steps on food, a popup indicates the winner.
- Observe logs for valid/invalid move counts.

2) Run an automatic random single robot
- Toggle Intelligent Robots ON or OFF as desired.
- Click "Random Single Robot".
- The single robot will make random moves each round until it finds food or explodes.
- Use the animation delay slider to slow/speed visualization.

3) Run a multi-robot random simulation
- Set "Number of Robots" to desired count (1–4).
- Optionally enable Intelligent Robots.
- Click "Random Multiple Robots".
- The simulation runs rounds where each active robot makes one random move.
- Simulation stops when food is found or all robots have exploded.

4) Step-by-step
- Press "Step Random Move" to make a single random-step cycle (useful for debugging or observation).

---

Configuration & customization
-----------

Common customization points in code:
- Grid size:
  - In ui.py, GRID constant is set to 4. Change to alter UI grid size, and pass the same size into Game(size=GRID). Update drawing cell sizes if needed.
- Colors and visuals:
  - Robot colors and shapes are controlled in ui.draw.
- Obstacles:
  - By default reset_board places one Bomb and one Rock (ui.reset_board).
  - Modify placement logic or add new obstacle types by subclassing Obstacle in models.py and updating game.place_obstacle usage.
- Intelligent behavior:
  - RoboInteligente.move tries all directions in the order of DIRS keys; you can change priority or add heuristics (e.g., distance to food).
- Delay/Animation:
  - Delay is controlled via a Tkinter Scale bound to delay_ms in ui.py.

---

Developer notes — code structure & APIs
-----------

Files & responsibilities
- main.py
  - Simple entry point:
    - from ui import RobotApp
    - app = RobotApp(); app.run()
- ui.py
  - RobotApp class:
    - __init__ builds GUI, holds state (self.game, self.canvas, self.info_text)
    - reset_board(): creates new Game(size=GRID), places food and obstacles
    - start_user_controlled(), start_random_single(), start_random_multi(): modes
    - _run_random(robots): internal loop using Tk.after for animation
    - step_random_move(), on_move_cmd(), on_canvas_click(): UI interactions
    - draw(): draws grid, obstacles (Bomb, Rock), food, robots, and logs state
- game.py
  - DIRS = {"UP": (-1,0), "RIGHT": (0,1), "DOWN": (1,0), "LEFT": (0,-1)}
  - DIR_NAMES: mapping strings → int codes (0..3) in the defined order
  - class Game:
    - __init__(size=4) -> sets size, robots list, obstacles dict, food, found_food boolean
    - in_bounds(x,y) -> bool
    - is_occupied(x,y) -> bool (ignores exploded robots)
    - add_robot(robot) -> add to self.robots with validation
    - remove_robot(robot) -> flags exploded and keeps for visualization
    - place_obstacle(x, y, obstacle) -> place Obstacle instance
    - apply_interaction(robot) -> if robot stepped on obstacle, calls obstacle.interact(robot, self)
    - check_food(robot) -> returns True if robot at food
    - place_food(x,y) -> set self.food
- models.py
  - MovimentoInvalidoException: custom exception type
  - Obstacle(ABC) with abstract interact(robot, game)
  - Bomb(Obstacle)
    - interact(robot, game): marks robot exploded and removes bomb from game.obstacles
  - Rock(Obstacle)
    - interact(robot, game): pushes robot back to previous_position (if any)
  - Robo:
    - id, x, y, color, exploded flag, previous_position, valid_moves, invalid_moves
    - move(direction, game): string-based movement, raises MovimentoInvalidoException for invalid moves, updates counters, calls game.apply_interaction and game.check_food
    - move_code(code, game): integer-mapped wrapper for move
    - detect_food(game) -> returns boolean
  - RoboInteligente(Robo)
    - move overrides to try preferred direction first then other directions on failure
    - move_code maps code to direction and delegates to the intelligent move

Important mapping details
- Direction codes (move_code): 0=UP, 1=RIGHT, 2=DOWN, 3=LEFT
- DIRS mapping is used throughout; update both DIRS and DIR_NAMES together if changing ordering.

Extending the system
- Add a new Obstacle type:
  - Create a new class in models.py inheriting Obstacle with an interact method that updates robot/game state.
  - Place using game.place_obstacle(x,y, NewObstacle()) from UI or code.
- Add a new robot intelligence strategy:
  - Subclass Robo and override move / move_code accordingly.
- Increase board size:
  - Adjust GRID constant and pass size into Game(size=GRID) in ui.reset_board and drawing code.

---

Testing suggestions
-----------
- Unit-test game logic separately:
  - Test Game.in_bounds() with edges
  - Test add_robot() prevents placement on obstacles or out-of-bounds
  - Test move(...) results: valid moves update position and valid_moves; invalid moves raise exceptions and increment invalid_moves
  - Test Bomb and Rock interactions
- Manual UI tests:
  - Try moving to an occupied cell (should throw MovimentoInvalidoException and increment invalid_moves)
  - Place a robot adjacent to a Bomb and move onto it (robot.exploded True; bomb removed)
  - Place a robot on a Rock path to see the push-back behavior

---

Troubleshooting
-----------
- GUI fails to start or tkinter import errors:
  - On Linux: install the tkinter package (e.g., sudo apt install python3-tk)
  - Confirm that the Python interpreter you run main.py with is the same one that has tkinter installed.
- Window blank or nothing drawn:
  - Ensure main.py was run; check console for tracebacks. UI logs exceptions to the log pane when possible.
- Robots not moving or instantaneous termination:
  - Check the log pane for MovimentoInvalidoException messages. If all robots are blocked or exploded, the simulation stops.
- Food or obstacle placement errors:
  - game.place_food and place_obstacle throw ValueError when attempting to overlap obstacles and food. The UI avoids that but custom changes may cause exceptions.

---

Notes on known behavior & design decisions
-----------
- Exploded robots remain in the robots list (with exploded = True) for visualization; is_occupied ignores exploded robots so other robots can move onto the explosion site.
- Bomb removes itself when it explodes; Rock remains.
- RoboInteligente attempts alternative directions but does not remember invalid moves across rounds — it avoids only within a single move attempt.
- Starting positions: the UI tries to avoid placing robots on obstacles; if the preferred start is blocked it finds the first free cell.

---

Contact & contributions
-----------
This project is intended for demonstration and educational purposes. If you want to contribute:
- Fork the repo
- Add tests for new behaviors
- Submit a PR with a descriptive title and tests/documentation

Acknowledgements
-----------
- Tkinter for the simple GUI
- The Game/Model structure follows classical tiny-simulation patterns for teaching OOP and agent interaction

---

Appendix: Quick reference (commands & key bindings)
-----------
- Run the app:
  - python main.py
- Keyboard arrows: move selected robot
- Mouse: click a robot to select it
- Buttons:
  - User-controlled (Single Robot)
  - Random Single Robot
  - Random Multiple Robots
  - Reset Board
  - Step Random Move
- Direction codes (for programmatic move_code):
  - 0 = UP, 1 = RIGHT, 2 = DOWN, 3 = LEFT

---

If you want, I can:
- Produce sample unit tests (pytest) for game logic and models.
- Provide a headless CLI runner that runs a text-only simulation cycle (no Tkinter).
- Add an option to save logs or simulation traces to a file.