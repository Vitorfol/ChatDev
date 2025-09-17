# Multi-player Board Game — User Manual

A lightweight Java Swing board-game application for up to 6 players with a customizable board and square behaviors. This manual explains what the software does, how to install and run it, how to play, and some developer notes (architecture, extension points and troubleshooting).

---

Contents

- Overview
- Quick features
- System requirements
- Install & build (command-line and IDE)
- Run the application
- GUI walkthrough — Setup screen
- GUI walkthrough — Play screen
- Game rules & square behaviors (detailed)
- Debug mode
- End-of-game summary & logs
- Design & architecture (patterns used)
- Extending the game
- Troubleshooting & FAQ
- License & contact

---

Overview

This application provides a configurable board game where:
- 2..6 players take turns moving by the sum of two dice.
- The board length is configurable (10..30 squares).
- Each square can be assigned one of several behaviors (Simple, Surprise, Prison, Lucky, Unlucky, Reverse, PlayAgain).
- Players have types (LUCKY, UNLUCKY, NORMAL) which affect some square outcomes.
- Coins are awarded on simple squares.
- The first player to reach or pass the final square wins.
- A Game facade (Game class) coordinates setup and play; GUI listens for game events.

Quick features

- Fully GUI-driven configuration and gameplay (Java Swing).
- Configure each square individually via a scrollable list.
- Choose number of players (2..6), each player's color and type.
- Debug mode: set destination square manually instead of rolling dice.
- Turn feedback: dice value, messages when landing on special squares, board view with players and coins.
- End-of-game summary: winner, total moves and final positions for each player.

System requirements

- Java Development Kit (JDK) 8 or later (JDK 11+ recommended).
- No external libraries are required — uses standard Java SE (Swing).
- A Java-aware IDE (IntelliJ IDEA, Eclipse, NetBeans) is optional but convenient.

Files & package layout

All source files are under package app. Example files included in the distribution (one-per-file):

- app/Main.java
- app/GUI.java
- app/Game.java
- app/GameListener.java
- app/Board.java
- app/Square.java (and concrete Square subclasses within)
- app/SquareFactory.java
- app/SquareType.java
- app/Player.java
- app/PlayerType.java
- app/Dice.java

(If you received a ZIP, unzip and keep the `app` directory structure.)

Install & build

From terminal (command line)

1. Confirm JDK is installed:

   java -version
   javac -version

2. Compile sources (run from parent directory of app):

   javac app/*.java

   This will produce .class files in the app folder.

3. Run the application:

   java app.Main

Package into executable JAR (optional)

1. Create a manifest file (MANIFEST.MF):

   Manifest-Version: 1.0
   Main-Class: app.Main

   Save as MANIFEST.MF.

2. Create JAR:

   jar cfm BoardGame.jar MANIFEST.MF app/*.class

3. Run JAR:

   java -jar BoardGame.jar

From an IDE (IntelliJ/Eclipse)

- Create a new Java project and add the `app` package with files.
- Mark project SDK to a JDK (8+).
- Build project and run app.Main (or configure a Run configuration).
- You can also export a JAR from the IDE.

Running the application

- Launch via java app.Main (or run from IDE).
- A window will open presenting the setup screen.

GUI walkthrough — Setup screen

Main elements (top to bottom and left-to-right):

- Board size: choose an integer between 10 and 30 (default: 15).
- Configure Board Squares button: opens the square configuration area (scrollable) showing one combobox per square index. Each combobox selects the square's behavior (Simple, Surprise, Prison, Lucky, Unlucky, Reverse, PlayAgain).
- Players: choose number of players (2..6), then for each player select:
  - Color: one of {"Red", "Blue", "Green", "Yellow", "Magenta", "Cyan"} (visual label only).
  - Type: PlayerType: LUCKY, UNLUCKY, NORMAL.
- Debug mode: a checkbox. If selected, gameplay uses the debug destination field instead of dice rolling.
- Start Game: initializes the Game facade and switches to the Play view.

Validation behavior

- The application enforces that at least two different player types are present among the configured players. If not, Start Game will be blocked and a message shown.

GUI walkthrough — Play screen

Main elements:

- Board view (left): a textual list showing each square index, its type, and players currently on that square including coin counts and types. Finished players (past the final square) appear under an "=== Finished Players ===" section.
- Controls & Status (right):
  - Dice label: displays last rolled dice values or "-" when none.
  - Roll Dice button: when not in debug mode, rolls two dice and advances the current player. In debug mode, this button reads the "Debug dest (idx)" field and moves the current player to that index instead of rolling.
  - Debug destination field (only used when Debug mode was enabled on setup).
  - Status area: running log with status messages such as moves, square messages, coin awards, extra-turns, prison skips, winner summary.

How to play (basic flow)

1. Configure board size and squares, select players and types, optionally enable Debug mode, then press Start Game.
2. The Play view displays the board and initial positions (all players start at position 0).
3. The current player uses the Roll Dice button to roll two dice (or, in Debug mode, type an index and press Roll to jump there).
4. Movement: the sum of two dice D1 + D2 advances the player. If D1 == D2 (a double) the player immediately keeps the turn (can roll again).
5. When a player lands on a square, the game logs the event and the square's rule is applied. If it is a Simple square the game awards +1 coin (this is handled during landing).
6. Some square effects grant extra turns (PlayAgain) or set flags that cause the player's next turn to be skipped (Prison), or move the player further forward/back, or swap players, etc.
7. The first player to reach or pass the final square wins.
8. When the game ends the UI displays a final summary with winner, total moves, and final positions for each player.

Game rules & square behaviors (detailed)

General movement

- Movement per turn = sum of two dice (1..6 each) => values 2..12.
- Rolling a double (both dice same value) grants a bonus turn: the player remains the current player and may roll again after the turn actions resolve.
- Coin behavior: Simple squares award 1 coin when landed on. (The Game logic adds the coin for Simple squares; other squares do not award the simple coin.)

Player types

- LUCKY: considered "lucky".
- UNLUCKY: considered "unlucky".
- NORMAL: standard.
- At least two different types must be selected among players during setup.

Square types

- SIMPLE
  - Name: "Simple"
  - Behavior: No special rule besides the +1 coin awarded when landing.
- SURPRISE
  - Name: "Surprise"
  - Behavior: Randomly sets the player's type to one of LUCKY, UNLUCKY, NORMAL. A message indicates the new type.
- PRISON
  - Name: "Prison"
  - Behavior: Sets the player's skipNextTurn flag. On the player's next scheduled turn, the flag is checked and the player will skip that turn (the flag then cleared).
  - Note: The Prison effect is applied when landing; the player continues their current turn as normal (there is no immediate lost turn), but their next time they would act they will be skipped.
- LUCKY
  - Name: "Lucky"
  - Behavior: If the player is not of type UNLUCKY, the player advances forward 3 squares immediately upon landing. If the player is type UNLUCKY, the square has no effect and a message is shown.
- UNLUCKY
  - Name: "Unlucky"
  - Behavior: Unless the player is type LUCKY, the player moves back 3 squares (not below 0). If the player is type LUCKY, the square has no effect and a message is shown.
- REVERSE
  - Name: "Reverse"
  - Behavior: Swap positions with the player currently in last place (the lowest board position). If the landing player is already last, no effect.
- PLAYAGAIN
  - Name: "PlayAgain"
  - Behavior: Grants an extra turn for the current player (the Game facade tracks this). It is equivalent to not advancing the current player index for the next move and the GUI will report that an extra turn was granted.

Edge cases & details

- If a square effect moves a player to or beyond the final square, the player immediately wins and the game ends. The Game class checks win condition after square effects.
- If a player's landing triggers multiple effects (e.g., moved by Lucky into another special square), the Game will apply effects for the new square in the same move cycle via the standard apply logic (Square.onLand is invoked for the new position when any movement sets position and Game.applySquareEffectForPlayerIndex is called accordingly).
- The GUI displays status messages for special squares and coin awards on Simple squares.
- The Game keeps a totalMoves counter incremented at each player action (roll or debug move).

Debug mode

- If Debug mode is enabled on setup, during play the Roll Dice button behaves differently:
  - Instead of rolling dice, the player enters a destination index (integer) in the "Debug dest (idx)" field and presses Roll Dice.
  - The current player is moved directly to that square index and the square effect is applied as in normal play.
- Use debug for testing or demonstration to jump players to specific squares.

End-of-game summary & logs

When a winner is found (a player reaches/passes the final square), the UI:

- Displays a status message announcing the winner.
- Shows a multi-line summary with:
  - Winner Name
  - Total moves
  - Final positions, coins and types for all players

The status panel remains available and the board view will show finishing positions.

Design & architecture (for developers)

Major classes and patterns used

- Game (Facade)
  - Acts as facade for setting up the board, players and controlling the game loop and rules.
- SquareFactory (Factory Pattern)
  - Build concrete Square instances based on SquareType enum.
- GameListener (Observer / Listener)
  - GUI implements this interface; Game notifies GUI about dice rolls, status messages, board updates and game end.
- Player.copy (Prototype-like)
  - Player provides a copy() helper used to expose safe snapshots to the GUI.
- Board (simple wrapper)
  - Holds the ordered list of Square instances.
- GUI (View + Controller for user interactions)
  - Manages both setup and play screens, listens to Game updates and presents the board state.

Threading

- The application initializes GUI using SwingUtilities.invokeLater (Event Dispatch Thread) to keep Swing thread-safety rules correct. All UI updates are performed on the EDT.

Extending the game (developer notes)

- Add a new square type:
  1. Add a new enum value to SquareType.
  2. Add a new Square subclass in app/Square.java or as a separate source file that implements onLand(Player, Game).
  3. Update SquareFactory.createSquare to return an instance for the new type.
  4. Optionally update GUI presentation strings.
- Add new player behaviors:
  - Modify Player class and apply rule checks from Square.onLand or inside Game methods.
- Add persistence:
  - Save/Load board configurations as JSON or simple text files by serializing configured SquareType list and player array.

Troubleshooting & FAQ

Q: Application doesn't start; I get "java: command not found" or "javac: command not found".
A: Install the JDK and add it to your PATH. Use the Oracle JDK or OpenJDK (8+).

Q: The Start Game button is disabled.
A: Make sure you have pressed "Configure Board Squares" (or used the default) and that you picked at least two different PlayerTypes among your players. The GUI enforces at least two different player types.

Q: In debug mode my dice label shows "-" and nothing else happens when I press Roll.
A: In Debug mode you must provide a numeric destination index in the "Debug dest (idx)" field. The Roll button will move the current player to that index instead of rolling dice.

Q: A Player seemed to "skip a turn" even though they were on the Prison square previously.
A: The Prison square sets a skipNextTurn flag and that causes the player's next scheduled turn to be skipped. It does not stop the current move (there is no immediate skipped action on the same turn when landing).

Q: My PlayAgain / double roll logic seems confusing — how do extra turns and doubles interact?
A:
- PlayAgain square explicitly grants an extra turn by setting a flag in Game. When that flag is set the current player will be allowed another action without advancing the turn.
- Rolling a double also allows the current player to act again (the Game logic checks dice equality and does not advance the current player index when a double occurs).
- Both mechanisms mean the current user stays the "current player" and may press Roll again to continue.

Q: How does Reverse choose the last player?
A: Reverse picks the player with the lowest board position (minimum position value). If there are multiple tied for last, it picks whichever Player object was determined by iteration order (no deterministic tie-breaking beyond the list order). If the landing player is already last, no swap happens.

Developer / debug tips

- You can add log outputs or breakpoints inside Game.applySquareEffectForPlayerIndex to inspect the sequence of events.
- Use Debug mode to jump players to specific squares quickly when verifying square interaction sequences.

Sample gameplay walkthrough (example)

1. Setup:
   - Board size: 12
   - Square 0..11: [SIMPLE, LUCKY, SIMPLE, PRISON, UNLUCKY, SIMPLE, SURPRISE, REVERSE, PLAYAGAIN, SIMPLE, SIMPLE, SIMPLE]
   - 3 Players:
     - P1-Red : NORMAL
     - P2-Blue : LUCKY
     - P3-Green : UNLUCKY
   - Debug mode: off
2. Play (example sequence):
   - P1 rolls 3+4=7 -> moves to index 7 (Reverse). Message: P1 landed on Reverse. If P3 was last, P1 swaps with P3, etc.
   - P1 rolled a double? No, advance turn.
   - P2 rolls a double 2+2 -> moves and receives a bonus roll (stay current). GUI reports double and dice label shows "2 + 2 = 4 (Double)".
   - P3 lands on Prison -> next time P3 would play they skip that turn.

Troubleshooting common errors

- OutOfBounds when using Debug mode: Provide destination indices in the 0..(boardSize-1) range. The app will clamp negative values to 0; landing beyond final index triggers a win.
- If the GUI does not update: Ensure Game.setListener(this) was called and that the GUI methods (updateBoard, updateStatus, updateDice, gameEnded) are executed on the EDT. The provided GUI already updates UI on the EDT.

License & contact

- This is a sample application for demonstration and testing. Confirm license terms from your project owner for distribution.
- For feature requests or bug reports, contact the development team (ChatDev product/engineering contacts).

---

If you want, I can:
- Provide a ready-to-run JAR build script (Gradle or simple shell/batch script).
- Add persistence (save/load configuration).
- Add a compact graphical board visualization instead of textual list.
- Add automated unit tests for the Game and Square behaviors.

Would you like a build script (Gradle) or an IDE project configuration file next?