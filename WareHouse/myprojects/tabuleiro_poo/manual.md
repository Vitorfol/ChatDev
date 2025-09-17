# Forty-Square Board Game — User Manual

A simple GUI board game implemented in Python (Tkinter). Up to 6 players race from square 0 to square 40. Players are one of three types — lucky, unlucky or normal — with different dice behaviors. The board contains special squares that affect movement, turns, and player types. The implementation uses inheritance and polymorphism for player behavior and supports a debug mode where you directly set a destination square.

This manual explains how to install and run the game, what the UI does, gameplay rules, how to use debug mode, and short developer notes for customization.

---

Table of contents
- Quick requirements
- Installation and run
- Files and code structure
- Main features & gameplay rules
- UI reference (what each control shows/does)
- Debug mode
- Example gameplay walkthrough
- Developer notes & customization
- Troubleshooting & FAQs

---

Quick requirements
- Python 3.7+ (recommended 3.8/3.9/3.10+)
- Standard library only (tkinter, random, etc.). No external pip packages required.
- On many Linux distributions you may need to install the system package for Tk:
  - Debian/Ubuntu: sudo apt-get install python3-tk
  - Fedora: sudo dnf install python3-tkinter
  - macOS and Windows usually include Tkinter with the standard Python installers.

---

Installation and run

1. Clone or copy the project directory containing:
   - main.py
   - players.py
   - board.py
   - utils.py

2. (Optional) Create and activate a virtual environment:
   - python3 -m venv venv
   - source venv/bin/activate  (Linux/macOS)
   - venv\Scripts\activate     (Windows)

3. Ensure Tkinter is available (see Quick requirements above).

4. Run the game:
   - python main.py

A GUI window will open with a Game Setup dialog. If the window doesn't appear, ensure your environment supports GUI (not a headless server).

---

Files and code structure (what each file contains)
- main.py
  - The GUI application and game flow (Tkinter).
  - Handles setup dialog (player number, names, types), board display, player turn flow, rolling dice, debug destination input, logging, and end-of-game summary.
  - Uses classes from players.py and board.py.
- players.py
  - Player base class and three subclasses:
    - Player (base)
    - NormalPlayer
    - LuckyPlayer — overrides roll_dice to ensure dice sum >= 7 (re-rolls until satisfied)
    - UnluckyPlayer — overrides roll_dice to ensure dice sum <= 6 (re-rolls until satisfied)
  - clone_as(new_type) lets the code change a player's type while preserving state.
  - Demonstrates inheritance and polymorphism: different roll_dice implementations for player types.
- board.py
  - Board logic and special square handling.
  - apply_square_effect(player, players) applies effects for the square the player currently occupies and resolves chained effects (e.g., forward moves that land on another special square).
  - Special squares are defined here and their behavior implemented.
- utils.py
  - Small utility helpers:
    - roll_two_dice(): random dice roll
    - choose_furthest_ahead / choose_furthest_behind: helper selection functions for opponents
    - random_other_type: pick a player type different from the current

---

Main features & gameplay rules

- Board:
  - Squares are numbered 0 .. 40. Winning line is reaching or passing square 40.
- Players:
  - Up to 6 players (minimum 2). Players start at square 0.
  - Types: normal, lucky, unlucky.
    - Lucky: dice rolls will always give sums >= 7 (the implemented method re-rolls until this is satisfied).
    - Unlucky: dice rolls will always give sums <= 6.
    - Normal: standard dice behavior.
  - At least two different player types must be present in the game setup.
- Movement:
  - Movement is determined by the sum of two 6-sided dice (two dice rolled).
  - If a player rolls doubles (both dice equal), they immediately get a bonus turn (do not advance to next player).
  - Total moves and individual move counts are tracked.
- Special squares:
  - 10, 25, 38: landing on these causes the player to miss their next turn (skip flag).
  - 13 (Surprise): draws a surprise card that changes the player's type randomly to a different type.
  - 5, 15, 30: move the player forward 3 spaces automatically (unless the player is Unlucky — then no forward movement).
  - 17, 27: forces the triggering player to send an opponent back to start (implementation sends the furthest-ahead opponent).
  - 20, 35: swap positions with the player who is the furthest-behind (tie broken by first encountered).
- Chained effects:
  - If an automatic effect moves the player to another special square or changes their type such that the new square or state triggers another effect, the board logic re-evaluates until a stable state or a safety limit is reached. Messages are logged for each event.
  - Note: when an opponent is sent back or swapped, the opponents' new positions are updated, but those opponents' new squares are not recursively re-evaluated as part of the same call (to avoid complex recursion).
- End conditions:
  - The first player to reach or pass square 40 wins.
  - On game end, the UI shows the winner, total moves made, and final positions of all players (also printed in the message log).

---

UI reference (what each area does)

- Setup dialog (opens at startup):
  - Number of players: spinbox (2–6).
  - For each player row:
    - Name entry (default P1, P2, ...).
    - Type selector (normal, lucky, unlucky). At least two different types must be selected before start.
  - Start Game button — closes setup and opens the main UI.
  - Cancel — quit application.

- Main game window:
  - Board row:
    - A horizontal row of square labels from 0 to 40. Each label shows the square number and any player names who are on that square.
  - Players status (left/middle):
    - A text area listing each player: index, name, type, position, skip-next-turn flag (if any), and moves made.
  - Controls / Info (right):
    - Turn label: shows whose turn it is (name and type).
    - Dice label: shows dice values and sum for the most recent roll or debug destination.
    - Roll Dice button: roll normally (disabled when debug mode is on).
    - Debug mode checkbox: toggles debug mode (when enabled you can input a destination).
    - Destination entry: when debug mode enabled, enter an integer destination square.
    - Set Destination button: applies the destination move (disabled unless debug is on).
  - Messages:
    - Log area that records dice rolls, special square messages, skip notices, type changes, double-roll bonuses, and the end-of-game summary.
  - End-of-game:
    - When a player wins, a pop-up message shows the winner, total moves, and final positions. The message is also logged.

---

How to play (step-by-step)
1. Start the program (python main.py). Setup dialog appears.
2. Select number of players (2–6). Edit player names and choose types. Ensure at least two different types are selected; otherwise the game will not start.
3. Click Start Game.
4. The main board appears. The first player's turn is shown in the Turn label.
5. If not in Debug mode: click Roll Dice to roll two dice for the current player.
   - Dice values and sum appear in the Dice label.
   - The player moves forward by the sum (their position increases).
   - Special square effects (if any) will be resolved automatically and messages appear in the log.
   - If doubles are rolled (both dice the same), the player gets an immediate bonus turn — do not press anything to proceed; the player can roll again.
   - If the player is required to skip their next turn (from landing on 10, 25 or 38), the next time their turn comes around the UI will report they miss the turn and clear the skip flag.
6. If Debug mode is enabled:
   - Check "Debug mode (input dest)". This disables the Roll Dice button.
   - Enter a destination integer into the Destination field (for example, 13 to test Surprise).
   - Click Set Destination to apply the move for the current player (counts as 1 move). Debug moves do not grant bonus turns for doubles.
7. Continue turns until a player reaches or passes square 40.
8. On game end, the winner is displayed in a pop-up. The message log shows a final summary listing each player's final position and moves.

---

Debug mode details and uses
- Purpose: simpler testing of square effects and chained interactions by setting the player's destination directly instead of rolling dice.
- Enable the checkbox "Debug mode (input dest)"; Roll Dice button becomes disabled.
- Enter an integer (0+) in the Destination field and press Set Destination.
  - The system sets the player's position to that destination and applies all square effects just like a normal move.
  - Debug moves count toward total moves and the player's move_count.
  - Debug moves do NOT award a bonus turn for doubles (because no dice rolled).
- Use debug mode to test:
  - Landing on 13 to force type change
  - Landing on 5/15/30 to test forward +3 (or prevented by Unlucky)
  - Landing on swap/send squares
  - Confirm skip-turn behavior by setting exactly 10/25/38

---

Example gameplay walkthrough (two players)
1. Setup:
   - Player 1: "Alice" [lucky]
   - Player 2: "Bob" [unlucky]
2. Turn 1 (Alice):
   - Alice (lucky) rolls 4 + 3 = 7 (always >=7 because of lucky behavior).
   - Moves to position 7. No special square. Log: "Alice rolled 4 and 3 (sum 7). Alice moves to 7."
3. Turn 2 (Bob):
   - Bob (unlucky) rolls 2 + 3 = 5 (unlucky ensures sums <= 6).
   - Moves to 5. Square 5 is a forward-three square; because Bob is Unlucky, he does NOT move forward 3.
   - Log: "Bob landed on 5 but is Unlucky; does not move forward 3 spaces."
4. Later, a player lands on 13:
   - Suppose Alice lands on 13 via a move or forward chain.
   - The game picks a new type different from Alice's current type and replaces the player object (preserving name, position and counters).
   - Log: "Alice landed on 13 (Surprise!) and changes type from lucky to normal."
5. A player lands on 20:
   - That player swaps positions with the player furthest behind; both positions are updated and logged.
6. When someone reaches or passes 40:
   - End-of-game pop-up and log appear with the winner, total moves, and final positions.

---

Developer notes & customization points

- How inheritance & polymorphism are used:
  - players.py defines Player and subclasses LuckyPlayer and UnluckyPlayer that override roll_dice. clone_as() allows changing a player's type at runtime while preserving state.
  - The GUI uses polymorphic roll_dice() — GameGUI doesn't need to know what kind of player it is; it simply calls current.roll_dice() and the right behavior happens.
- Where to change the board size or special squares:
  - board.Board has attribute self.size (currently 40). Change it to change winning square.
  - Special-square sets are defined in Board.__init__:
    - miss_turn_squares = {10, 25, 38}
    - surprise_square = 13
    - forward_three = {5, 15, 30}
    - send_opponent_back = {17, 27}
    - swap_with_behind = {20, 35}
  - Modifying these sets or rules will adapt game behavior. If you change numbers, also consider updating the board display generation in main.py to reflect new max square.
- Safety and chaining:
  - apply_square_effect re-evaluates the player's square until stable. It includes a maximum iteration guard to avoid infinite loops.
  - When apply_square_effect changes a player's type, it returns a new player instance (new_player) to the caller; main.py replaces the player object in the players list.
- Helper utilities:
  - utils.choose_furthest_ahead and choose_furthest_behind use object identity (is) for exclusions; if you make deeper copies elsewhere, be careful.
- Testing:
  - Use Debug mode to directly move players to test special squares without multiple rolls.
  - To simulate many games automatically, you could add a script that uses the player classes and Board.apply_square_effect without the GUI.

---

Troubleshooting & FAQs

- Q: The GUI doesn't start on my Linux server.
  - A: Ensure you have Tkinter installed. On Debian/Ubuntu: sudo apt-get install python3-tk.
- Q: I clicked Start Game but nothing happened / I get an error about types.
  - A: Ensure at least two distinct player types are selected in the setup dialog (the game enforces this).
- Q: The player changed type but the players list shows old type / duplicates.
  - A: Type changes replace the player instance in the players list. The messages and UI should reflect the change; if you modify code, ensure main.py receives the new_player returned from board.apply_square_effect and replaces the old entry.
- Q: How are ties broken when choosing furthest ahead or furthest behind?
  - A: choose_furthest_ahead and choose_furthest_behind return the first player encountered with the extreme position in the players list (tie broken by order in the players list).
- Q: Can I run this headless (no GUI)?
  - A: This implementation is GUI-first. To run headless you’d need to create a separate CLI script that uses Player and Board classes and orchestrates turns (not provided by default).

---

Contact & support (for internal devs)
- The codebase is small and self-contained. For feature requests (e.g., networked multiplayer, AI opponents, alternate board layouts), open an issue in your project tracker and include desired behavior.
- For bugs: locate reproduction steps and try to reproduce in Debug mode to capture logged messages.

---

Appendix: Quick command reference

- Run: python main.py
- Setup:
  - Number of players: 2–6
  - Player types: normal, lucky, unlucky
- Controls:
  - Roll Dice — roll two dice (normal play)
  - Debug mode — enable to set Destination manually
  - Destination + Set Destination — move current player to that square (counts as move)
- Win condition:
  - First player to reach or pass square 40 wins.

---

Enjoy playing and testing! If you want, I can prepare:
- A short developer script to run automated simulations without the GUI
- A unit-test skeleton to validate special-square behaviors
- Variant rules (e.g., penalty squares, different bonus rules)

Which would you like next?