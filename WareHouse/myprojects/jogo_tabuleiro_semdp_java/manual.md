# ChatDev Board Game — User Manual

Version: 1.0  
Platform: Desktop (Java Swing)  
Author: ChatDev — Chief Product Officer

This manual explains how to install, run, configure and play the ChatDev Board Game — a desktop Java board-game application for up to 6 players with a customizable board and square effects. The application ships as Java source files (Swing GUI) and uses a Game facade class to coordinate gameplay.

Contents
- Quick overview
- Features
- System requirements
- Installation & build (compile/run)
- Files included & class responsibilities
- How to configure a game (GUI walkthrough)
- Gameplay rules and square effects (detailed)
- Debug mode
- End-of-game reporting
- Troubleshooting & FAQ
- Extension ideas & developer notes

Quick overview
-------------
ChatDev Board Game is a turn-based multiplayer board game implemented in Java using Swing. Players move by the sum of two dice (or via debug input), squares have different behaviors (like changing player type, moving forward/back, missing turns, etc.), and the first player to reach or pass the final square wins. The Game class acts as a facade for setup and gameplay actions and is the main interface between UI and game logic.

Key features
------------
- 2–6 players (configurable names, display colors, and player types)
- Customizable board size (10–50 recommended; code supports 5–50)
- Customizable square types per square
- Player types: Lucky, Unlucky, Normal (at least two different types required)
- Dice movement (sum of 2 dice); doubles = bonus turn
- Special squares: Surprise, Prison, Lucky, Unlucky, Reverse, PlayAgain
- Simple squares increment player coins (reward)
- Debug mode: manually set destination instead of rolling dice
- UI displays turn info, positions, dice results, and logs messages
- End-of-game summary with winner, total moves and final positions

System requirements
-------------------
- Java Development Kit (JDK) 8 or newer (JDK 11+ recommended).
- Desktop OS with GUI support (Windows, macOS, Linux with X11/Wayland).
- No external libraries required (uses standard Java SE / Swing).

Installation & build
--------------------
The project is provided as individual .java files (no package statements). Compile and run in a directory that contains all the .java files.

1. Install JDK (if not already installed). Verify:
   - java -version
   - javac -version

2. Place all .java source files in one folder. Example files included:
   - Main.java
   - GameGUI.java
   - Game.java
   - Player.java
   - Board.java
   - Square.java
   - SimpleSquare.java
   - SurpriseSquare.java
   - PrisonSquare.java
   - LuckySquare.java
   - UnluckySquare.java
   - ReverseSquare.java
   - PlayAgainSquare.java
   - PlayerType.java

3. Compile:
   - Open a terminal / command prompt in the folder and run:
     javac *.java
   This produces .class files.

4. Run:
   - Start the GUI:
     java Main

Packaging as a JAR (optional)
- Create an executable JAR (assumes Main is the entry point):
  1. javac *.java
  2. echo Main-Class: Main > manifest.txt
  3. jar cfm ChatDevBoardGame.jar manifest.txt *.class
  4. java -jar ChatDevBoardGame.jar

If you use an IDE (Eclipse, IntelliJ IDEA, NetBeans), create a Java project, add the files to the src root (no packages required), compile and run Main.

Files included & responsibilities
---------------------------------
(Brief explanation of the main classes)

- Main.java
  - Application entry point. Starts the Swing UI by creating GameGUI.

- GameGUI.java
  - Swing-based GUI for setup and gameplay.
  - Setup panel: choose player count, names, colors, types, board size and square types.
  - Game panel: shows current status, positions, action buttons (Roll Dice / debug).
  - Connects to the Game facade to start and advance the game, displays logs and status.

- Game.java (facade)
  - Coordinates players, board and square effects.
  - Exposes:
    - playTurnRoll() — roll dice and process move
    - playTurnDebug(int destination) — move player to chosen position (debug)
    - grantExtraTurnTo(Player) — used by PlayAgain square
    - swapPositions(Player, Player), findLastOnBoard(), getTypeFromDiceSum(int)
  - Maintains game state: current player index, total moves, finished flag and winner.

- Player.java
  - Represents a player: name, color (java.awt.Color), type (PlayerType), position (int), coins (int)
  - Flags: skipNextTurn (prison), hasExtraTurn (PlayAgain)

- Board.java
  - Holds ordered list of Square objects. Provides getSize() and getSquareAt(position).

- Square.java (abstract)
  - Base for all specialized squares. Each square implements getName() and applyEffect(Game, Player, diceSum, logger).

- SimpleSquare.java
  - Default square: increments player's coins by 1 when landed on.

- SurpriseSquare.java
  - Changes player's type according to dice sum:
    - diceSum >= 7 -> LUCKY
    - diceSum <= 6 -> UNLUCKY
    (Note: debug moves pass diceSum = 0, so Surprise will set UNLUCKY in debug mode.)

- PrisonSquare.java
  - Player misses their next turn (skipNextTurn flag is set).

- LuckySquare.java
  - If player is not UNLUCKY: player moves forward 3 spaces immediately.
  - If player is UNLUCKY: no forward effect.

- UnluckySquare.java
  - If player is not LUCKY: player moves back 3 spaces immediately (min 0).
  - If player is LUCKY: no backward effect.

- ReverseSquare.java
  - Swap positions with the "last" player (smallest position).
  - No effect if the landing player is already the last.

- PlayAgainSquare.java
  - Grants an extra turn to the landing player (sets hasExtraTurn flag on player). The extra turn will be consumed immediately on the next step (player keeps current turn when appropriate).

- PlayerType.java
  - Enum: LUCKY, UNLUCKY, NORMAL

How to configure a game (GUI walkthrough)
-----------------------------------------
1. Launch the application (java Main); the Setup panel opens first.

2. Top controls:
   - Players (2–6): choose number of players.
   - Board size: enter a number (recommended 10–50; code accepts 5–50).

3. Players configuration:
   - Up to 6 player rows are shown. Only the number selected will be enabled.
   - For each enabled player:
     - Name: enter a display name.
     - Color: choose a color (used in the positions area).
     - Type: choose initial type (Normal, Lucky, Unlucky).
   - Note: The GUI enforces at least two different player types across the players. You must select player types such that at least two distinct types are present.

4. Board squares configuration:
   - Click "Generate Square Config" to populate square configuration rows for each board index.
   - For each square (1 .. BoardSize), pick a square type from:
     Simple, Surprise, Prison, Lucky, Unlucky, Reverse, PlayAgain
   - Square 1 (start) and the final square are set to Simple by default to avoid surprises at the very start and final square.

5. Debug mode:
   - Checkbox "Debug mode (allow manual destination)":
     - When enabled, the main game panel provides a text field where you can type an absolute destination (index).
     - Instead of rolling dice, entering a destination and clicking "Roll Dice" will move the current player to that absolute square index (useful for testing).
   - When disabled, standard two-dice rolling is used.

6. Start game:
   - Click "Start Game" to create the Game instance and switch to the game panel.

Game panel overview
-------------------
- Top area:
  - Status label: Shows whose turn it is and their type or shows winner when game ends.
  - Positions (right below): HTML-formatted list showing each player's name, position, coin count, type and a visual color indicator. If a player is set to skip next turn, "(skip)" is appended.

- Middle area:
  - Log area: chronological messages about rolls, moves, square landings and special effects.

- Bottom controls:
  - "Roll Dice" button:
    - Normal mode: triggers playTurnRoll() — runs a dice roll (two dice, 1..6).
    - Debug mode: reads the integer destination from "Debug dest (index)" field and calls playTurnDebug(destination).
  - Debug dest (index): input for debug mode.
  - Back to Setup: return to setup panel to adjust game config (note that current game state is discarded when you go back).

Gameplay mechanics & rules (detailed)
------------------------------------
- Turn order:
  - Players take turns in configured order. Current player is tracked by Game.currentPlayerIndex.
  - If a player is marked as finished (reached/passed final square), they are skipped for future turns.
  - Prison square sets skipNextTurn flag — on the player's next turn the skip is consumed and they do not move.

- Movement:
  - Normal mode: two dice are rolled (d1 and d2); sum = d1 + d2.
  - Player moves forward by "sum" positions (from current position).
  - If a player reaches or passes the final square (position >= board size), they immediately win; the game ends.

- Dice doubles:
  - If the two dice show the same face (d1 == d2), the player receives a bonus turn and remains the current player (GUI logs the double and extra-turn).
  - PlayAgain square also grants an extra turn via a flag on the player; the extra-turn flag is consumed when used.

- Square landing:
  - If player lands on a square (position >= 1 and <= board size), the square's applyEffect(...) is called with the dice sum (0 for debug moves).
  - SimpleSquare: increments player's coins by 1 (coins are displayed in UI).
  - SurpriseSquare: changes player's type according to dice sum:
    - diceSum >= 7 -> LUCKY
    - diceSum <= 6 -> UNLUCKY
    - (Note: because diceSum is either >= 2 and <= 12 or 0 in debug mode, SurpriseSquare will set UNLUCKY for debug moves as diceSum = 0.)
  - PrisonSquare: sets player to skip next turn.
  - LuckySquare: if player's current type != UNLUCKY, player moves forward 3 positions immediately; otherwise no effect.
  - UnluckySquare: if player's type != LUCKY, player moves back 3 positions (minimum 0); otherwise no effect.
  - ReverseSquare: swap positions with the player who is last on the board (smallest position). If the landing player is already last, no effect.
  - PlayAgainSquare: grants an extra turn (flag on player). The flag is consumed when used: the player remains current for one more turn.

- Coin accumulation:
  - Only SimpleSquare increments coins (+1).
  - Coins are purely a score-like stat and do not directly change movement.

- Winning:
  - The first player to have position >= board size is declared winner immediately.
  - The game ends, GUI logs summary: winner name, total moves count and final positions + coins for each player.

Debug mode details
------------------
- Use Debug mode to control movement deterministically:
  - Enable "Debug mode (allow manual destination)" in setup.
  - In the Game panel supply a destination integer in "Debug dest (index)" and click "Roll Dice".
  - The destination is an absolute board index (0 = start). If destination >= board size, the player wins immediately.
  - No dice are rolled and playTurnDebug() calls the square effect with diceSum = 0 (so SurpriseSquare will set UNLUCKY in debug).
  - After a debug move, play advances normally unless the player has an extra-turn flag (from a PlayAgain square).

End-of-game reporting
---------------------
When the game ends, the GUI:
- Sets status label to show winner.
- Logs "=== GAME OVER ===".
- Logs winner's name, total moves and final positions for each player (name, pos, coins, type).
- Disables the Roll Dice button.

Total moves:
- The Game class increments totalMoves by 1 on each active move (roll or debug move), so totalMoves is a measure of turns executed (not including skipped turns).

Troubleshooting & FAQ
---------------------
Q: Compilation errors like "cannot find symbol" or "package ... does not exist"?
- Ensure all .java files are in the same directory and you run javac *.java from there.
- If you added package declarations, move files to appropriate folder structure or remove package lines.

Q: The UI looks broken or is blank on startup?
- Verify Java is installed and compatible. Swing should work on standard desktop setups.
- Ensure you run `java Main` in the directory where Main.class exists (no package).

Q: Surprise square in debug mode makes player UNLUCKY — why?
- Debug mode sets diceSum = 0 for square effects so SurpriseSquare uses Game.getTypeFromDiceSum(0) which maps to UNLUCKY (diceSum <= 6). For testing Surprise with an actual dice-derived change, use normal roll mode.

Q: A player hit PlayAgain but the turn advanced — bug?
- PlayAgain sets a hasExtraTurn flag on the player. The game is implemented to preserve the current player if hasExtraTurn is true. If you observe different behavior, ensure you are running the latest compiled classes and not an older build.

Q: Are there AI/computer-controlled players?
- Not in this release. All players are operated through the GUI controls (human players).

Known limitations
-----------------
- No persistence: the game state is not saved when you close the app.
- No networked multiplayer — all players share the same local GUI.
- SurpriseSquare uses diceSum argument; debug moves supply 0 which defaults to UNLUCKY.
- There is no animated board: positions are textual in the UI only.
- The GUI enforces (on Start) that at least two distinct player types are present — this is a game rule.

Extending the game (developer notes)
-----------------------------------
- To add new square types:
  1. Add new class extending Square and implement getName() and applyEffect(...).
  2. Add the new type name to the squareTypes array in GameGUI so it appears in the setup UI.
  3. Update GameGUI's board creation switch to instantiate the new square type.

- To add AI players:
  - Add an isAI flag to Player and implement a decision routine in Game (or GameGUI) to auto-advance AI turns.

- To persist settings or save game state:
  - Serialize Game state to disk (e.g., JSON) and implement Load/Save in the GUI.

- To support packaged resources, add package declarations and move files under appropriate src/ directories, then use build tools (Maven/Gradle).

Sample play example (quick)
---------------------------
1. Start app: java Main
2. In Setup:
   - Players: 3
   - Board size: 20
   - Configure player names/colors/types: Player1 (Red, Normal), Player2 (Blue, Lucky), Player3 (Green, Unlucky)
   - Click "Generate Square Config" and review/adjust squares.
   - (Optional) Check "Debug mode" for testing.
   - Click Start Game.
3. Game panel:
   - Current turn: Player1
   - Click "Roll Dice": logs show roll and movement.
   - If lands on Simple square: "gains 1 coin".
   - If lands on Lucky and not UNLUCKY: immediate +3 spaces.
   - If rolls doubles: log shows bonus turn and you get to click Roll Dice again for same player.
4. Continue until some player reaches position >= 20 — winner is declared and final stats logged.

Contact & support
-----------------
If you need help or want feature requests, contact the ChatDev team internally. Include Java version and the exact console logs if you hit an error.

Legal & credits
---------------
- Code provided by ChatDev.
- The application uses Java SE standard libraries (Swing).

Appendix: Important notes about the code
----------------------------------------
- The Game class is the facade exposing methods used by the GUI to start and progress gameplay.
- Square classes are stateless except for index; they operate by mutating Player and calling Game helper methods when necessary.
- The GUI uses Consumer<String> logging callbacks to append messages to the text area on the Swing EDT (thread-safe via SwingUtilities).
- The board uses 1-based indices for squares. Player positions are integers where 0 means "start / before first square".
- Always recompile all .java files after editing (javac *.java).

Enjoy playing and customizing the ChatDev Board Game!