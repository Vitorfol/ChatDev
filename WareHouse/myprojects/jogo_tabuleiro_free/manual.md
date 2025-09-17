# Custom Board Game — User Manual

A simple customizable board game implemented in Python with a Tkinter GUI.  
This manual explains installation, running the app, GUI usage, game rules, debug mode, and developer notes (Game facade API and data models).

---

## Table of contents
- Overview
- Requirements
- Installation
- Launching the application
- GUI walkthrough
  - Setup screen (configuration)
  - Players configuration
  - Board squares editor
  - Starting the game
  - Game screen (during play)
  - Controls and messages
- Gameplay rules (detailed)
  - Turn flow
  - Dice and doubles
  - Player types
  - Square types and effects
  - Coins and win condition
  - Special behaviors & clarifications
- Debug mode
- End of game & summary
- Developer reference (Game facade & models)
  - Game class public API
  - Models and enums
  - Notes on implementation details / extension points
- Troubleshooting & FAQs
- Example configuration & quick play scenario
- License & contact

---

## Overview
This application lets up to 6 players play a customizable board game. Players are represented by a color and a type (lucky / unlucky / normal). The board is configurable in size and per-square type. Movement is based on two dice; doubles grant an extra turn. Various special squares modify player state or movement.

The GUI implements the setup and play screens. The core game logic is contained in the Game class which acts as a facade for setup and gameplay.

---

## Requirements
- Python 3.8 or newer (3.10+ recommended)
- Standard library modules: tkinter, random, enum, functools (all standard with CPython)
- No third-party pip packages are required.

Note: On some Linux distributions Tkinter must be installed separately. See installation notes below.

---

## Installation

1. Install Python 3.8+ (from https://www.python.org/) or use your system package manager.

2. Ensure tkinter is available:
   - macOS: Tkinter is typically available with the system Python.
   - Windows: Tkinter is included with the official Python installer.
   - Ubuntu/Debian:
     sudo apt update
     sudo apt install python3-tk
   - Fedora:
     sudo dnf install python3-tkinter

3. (Optional) Create and activate a virtual environment:
   python -m venv venv
   source venv/bin/activate  # Unix/macOS
   venv\Scripts\activate     # Windows

4. Copy the project files into a folder:
   - main.py
   - gui.py
   - game.py
   - models.py

No pip installs are required beyond optional environment setup.

---

## Launching the application

From the project directory run:
python main.py

This launches the Tkinter GUI. On close, the application exits.

---

## GUI walkthrough

The GUI has two main phases: Setup and Game.

### Setup screen (top-level)
- Board Size (squares): enter the number of board squares (integer). Minimum allowed is 5.
- Number of Players: choose 2–6 players. The player rows update automatically when you change this.
- Debug mode (checkbox): if enabled, you may manually input destination indices during play instead of rolling dice.

### Players configuration
For each player you can set:
- Name (text)
- Color (drop-down; colors must be unique across players)
- Type (lucky, unlucky, normal)

Important:
- You must choose at least two different player types across all players (e.g., at least one "lucky" and one "normal").
- Colors must be distinct.

### Board squares editor
Displays one row per square index (0 .. board_size-1), each with a type drop-down. Square types come from the SquareType enum. Controls:
- "Auto-fill some special squares": randomly fills some internal squares with special types (keeps start and final squares SIMPLE).
- "Reset squares to default Simple": rebuilds list with all squares set to SIMPLE.

Notes:
- Square index 0 (start) and index (board_size - 1) (final) are forced to SIMPLE and their controls are disabled in the editor.
- If you change board_size, press the reset or rebuild (change the board size field and click outside) to reinitialize the editor.

### Starting the game
Click "Start Game" once players and squares are configured correctly. Validation performed:
- Board size >= 5
- 2–6 players
- Unique colors
- At least two different player types

If validation passes, the game UI opens.

---

## Game screen (during play)

Main elements:
- Board canvas: squares drawn left to right, colored based on type. Player tokens (small colored dots) are shown on their current squares.
- Players panel: lists player name, color, position, coins, type, and moves.
- Messages area: shows turn events, dice rolls, and special-square messages.
- Controls:
  - Roll Dice: roll two dice for the current player (unless debug mode is active and you choose to use debug destination).
  - Debug destination entry (only usable if debug mode enabled at setup): input an integer index and press "Use Debug Destination" to move current player directly.
  - Next (skip turn): manually skip the current player's turn (counts as a move).
  - End Game: end the game early; the winner will be chosen as the player with the farthest position.

Turn indicator and other status messages appear near the top.

---

## Gameplay rules (detailed)

### Turn flow
- Game keeps a round-robin turn order.
- On a player's turn:
  - If they have skip_turn (from Prison), they miss this turn, skip_turn is cleared, move counted, and turn advances.
  - Else:
    - In normal mode: two dice are rolled, the player moves forward by the sum, and any square effect is applied.
    - In debug mode: if you invoke the debug destination, the player is moved directly to that index and square effects are applied.
- After the move and square effect:
  - If the player reaches or passes the final square (index board_size-1), they immediately win and the game ends.
  - Extra-turns:
    - Rolling a double (both dice same) grants an extra turn.
    - Landing on a PlayAgain square grants an extra turn.
    - When extra turn is granted, the current_player_index does not advance; the same player plays again next.
  - Otherwise the turn advances to the next player.

### Dice and doubles
- Two standard six-sided dice.
- A double (d1 == d2) grants an extra turn for that player.

### Player types
- Each player has a ptype: "lucky", "unlucky", or "normal".
- The code uses player type to determine reactions to certain squares:
  - Lucky and Unlucky squares check the player's ptype to determine whether to apply their movement effect.

Note: Player ptype itself is not directly used to modify dice rolls — the "lucky/unlucky" roll categories mentioned in the task description are informational only. The code marks rolls with sum >= 7 as "lucky" and sum <= 6 as "unlucky" in logs but does not automatically change player type.

### Square types and effects
Squares are enumerated by the SquareType enum. Effects are applied when the player lands on that square (only once — extra movement caused by that effect does not trigger the new square's effect again, see "Special behaviors" below).

- SIMPLE:
  - No special effect besides giving the player 1 coin upon landing.
- SURPRISE:
  - Randomly changes player's ptype to one of ["lucky","unlucky","normal"].
- PRISON:
  - Sets player's skip_turn flag (they will miss next turn once).
- LUCKY:
  - Moves player forward 3 squares unless player's ptype == "unlucky".
- UNLUCKY:
  - Moves player back 3 squares (minimum 0) unless player's ptype == "lucky".
- REVERSE:
  - Swaps positions with the player at the last index in the players list (the "last in order"), unless current player is already last in the order. This is swap by player list index (turn order), not "last by position".
- PLAYAGAIN:
  - Grants an extra turn to the player immediately.

Important: Coins are only incremented for SIMPLE squares in this implementation.

### Coins and win condition
- Players collect 1 coin when landing on SIMPLE squares.
- The first player to reach or pass the final square (index board_size - 1) wins immediately.
- If the user ends the game early (End Game), the "winner" is chosen as the player with the highest position (farthest advanced).

### Special behaviors & clarifications
- Effects that move a player forward/backward (LUCKY / UNLUCKY / REVERSE) do not recursively apply the effects of the landing square the player moves onto. The square effect is applied only once per turn by the code.
- Reverse uses the last element of the players list (index = len(players)-1) as the swap partner. That player is not necessarily the one with the last position on the board.
- PRISON sets a skip flag which is consumed on the player's next turn; the skip is then cleared.
- Debug destination moved via debug mode is clamped: negative indices clamp to 0. If you move beyond the final square, the game interprets it as reaching the final square and triggers a win.
- The game keeps per-player move count (in Player.moves) and a global total_moves counter. Skipping a turn using Next or missing a turn due to prison still counts as moves.

---

## Debug mode
- Enable "Debug mode (manual destination input)" in the setup screen before starting a game.
- During play, the small entry field on the right lets you type an integer destination index and click "Use Debug Destination".
- That moves the current player directly to that index and applies the square effect for the landing square.
- Debug mode bypasses dice rolling for that move. The GUI still logs the debug move in messages.
- Validations: the code treats non-integer input as invalid and will report an error.

---

## End of game & summary
When a player wins (reaches/passes last square), the GUI displays a messagebox with:
- Winner name
- Total moves
- Final positions, coins, type, and moves for each player

If the user presses End Game manually, a similar summary is shown and the app closes (or can be used to inspect final state).

---

## Developer reference (Game facade & models)

Project files:
- main.py — application entry point. Launches the GUI.
- gui.py — Tkinter-based GUI: setup screen, board editor, game screen, and UI wiring.
- game.py — Game facade class containing game logic and public API used by GUI.
- models.py — Data models (SquareType Enum, Square, Player).

Key models (models.py):
- SquareType (Enum): SIMPLE, SURPRISE, PRISON, LUCKY, UNLUCKY, REVERSE, PLAYAGAIN
- Square: index, type
- Player: name, color, coins, position, ptype (string), skip_turn (bool), moves (int)

Game public API (game.py):
- Game.setup(board_size, players_list, squares_types=None, debug=False)
  - board_size: integer >= 5
  - players_list: list of dicts: {"name": str, "color": str, "type": "lucky"|"unlucky"|"normal"}
  - squares_types: optional list of SquareType for each index; must match board_size if provided
  - debug: enable manual destination moves
- Game.next_turn(debug_destination=None)
  - Advance one logical turn. If debug is enabled and debug_destination is provided, player is moved to that index instead of rolling dice.
  - Returns dict with keys:
    - messages: list of strings logged during the turn
    - dice: (d1,d2) if rolled
    - debug_move: destination if debug used
    - winner: Player instance if someone won
    - total_moves: int
    - extra_turn: bool (True when same player gets another turn)
- Game.skip_current_player()
  - Skip the current player's turn (counts as a move).
- Game.end_game()
  - Ends the game and returns (winner, total_moves). Winner is chosen by max position when ended manually.
- Game.roll_dice() and internal apply_square_effect(...) exist (roll_dice is just a helper; apply_square_effect is used internally by next_turn).

Implementation notes:
- apply_square_effect applies exactly one square effect at the square where the player landed after the dice move or debug move. If that effect moves the player to another square, the new square's effect is not applied in the same turn.
- The "Reverse" square swaps position with the last player in the players list (not "last by position" necessarily).
- The code stores player type as a string (player.ptype) and uses it for conditional behavior on certain squares.

---

## Troubleshooting & FAQs

Q: The app complains "Board size must be at least 5".
A: Set Board Size >= 5 in the setup UI.

Q: Setup fails with "Color clash" or duplicate color error.
A: Choose unique colors per player. The GUI requires distinct colors.

Q: Setup fails with "There must be at least two different player types".
A: Choose player types such that at least two types (e.g., lucky and normal) are present among players.

Q: Debug destination doesn't do anything or error appears.
A: Ensure "Debug mode" checkbox was enabled in setup before starting the game. The debug field expects an integer destination index.

Q: I want special squares to chain (i.e., land on lucky, move +3 and apply the new square's effect).
A: The current implementation does not chain square effects. To support chaining, modify game.apply_square_effect to check if a movement occurred and call apply_square_effect again (taking care to avoid infinite recursion).

Q: I get a Tkinter import error on Linux.
A: Install python3-tk from your distro package manager (example: sudo apt install python3-tk).

---

## Example configuration & quick play scenario

1. Start the app (python main.py).
2. Board Size = 20, Number of Players = 3.
3. Player 1: Name = Alice, Color = red, Type = lucky  
   Player 2: Bob, Color = blue, Type = normal  
   Player 3: Carla, Color = green, Type = unlucky
4. Click "Auto-fill some special squares" to randomly add some SURPRISE, PRISON, LUCKY, etc.
5. Enable "Debug mode" if you'd like to test specific landings.
6. Click "Start Game".
7. Use "Roll Dice" to play normally or "Use Debug Destination" to move a player to a chosen square (debug).
8. Follow messages area for dice sums and square messages. Player tokens on the board reflect positions.
9. The first player to reach or pass square index 19 (board_size - 1) wins.

---

## Extending & customization notes

- To change the coin rule (e.g., also give coins on certain special squares), modify apply_square_effect in game.py where SquareType.SIMPLE is handled.
- To chain square effects when movement caused by a square lands on another special square, enhance apply_square_effect to loop while the new square is different and continue applying effects (watch out for infinite loops).
- To alter the "Reverse" behavior to swap with the player currently last by position, compute the player with the minimum/maximum position and swap with them instead of the last index.
- To add new square types, extend SquareType enum, update gui.squares editor options and apply_square_effect to handle the new type.

---

## Contact & support
This implementation is a small demonstrative project. For enhancements, bug reports, or support, edit the Python files in your local project, or reach out to your project team.

---

Thank you for using the Custom Board Game. Have fun!