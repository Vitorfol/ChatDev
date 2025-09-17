# ChatDev Board Game — User Manual

A simple 2–6 player board game implemented in Java (Swing GUI). Players move along a 40-square board (0..40+). Each player has a type (Lucky, Unlucky, Normal) that affects dice outcomes. The first player to reach or pass square 40 wins.

This manual explains features, installation/build/run instructions, how to play, UI controls, special-square rules, debug mode, and developer notes.

---

Table of contents
- Overview & Main Features
- System Requirements
- Project structure
- Build & Run (Command-line, IDE, JAR)
- Using the GUI — Controls & Workflow
- Game Rules & Special Squares (detailed)
- Debug Mode
- Example playthrough (sample messages)
- Developer notes (design, inheritance & polymorphism, extension points)
- Troubleshooting & FAQs
- Suggested enhancements

---

Overview & Main Features
- Desktop GUI game (Java Swing).
- Up to 6 players; players start at square 0.
- Three player types:
  - Lucky — dice sum always >= 7.
  - Unlucky — dice sum always <= 6.
  - Normal — standard dice.
- Movement is determined by the sum of two dice; double (both dice same) grants a bonus turn.
- Special squares with effects (see "Game Rules & Special Squares").
- GUI shows:
  - Each player's name, type, position and skip-next-turn flag,
  - Current player's turn,
  - Dice result,
  - Message/log area with events,
  - Total moves counter.
- Game ends when a player reaches or passes square 40; final summary (winner, total moves, final positions) is shown in the messages.
- Debug mode: instead of rolling dice, user can input a destination square to move the current player directly (landing effects still apply).
- Implementation uses inheritance and polymorphism (Player base class, LuckyPlayer/UnluckyPlayer/NormalPlayer subclasses).

---

System Requirements
- Java Development Kit (JDK) 8 or later. (JDK 11+ recommended.)
- Minimal memory and CPU (Swing-based GUI).
- Optional: Maven or Gradle if you prefer building via a build tool.

---

Project structure (files provided)
Files are in package chatdev.boardgame. Example tree (relative to src root):

- src/chatdev/boardgame/Main.java
- src/chatdev/boardgame/GameGUI.java
- src/chatdev/boardgame/Game.java
- src/chatdev/boardgame/Board.java
- src/chatdev/boardgame/Player.java
- src/chatdev/boardgame/LuckyPlayer.java
- src/chatdev/boardgame/UnluckyPlayer.java
- src/chatdev/boardgame/NormalPlayer.java
- src/chatdev/boardgame/DiceResult.java

Key classes and roles:
- Main — application entrypoint; instantiates the GUI.
- GameGUI — Swing interface; setup dialogs and main gameplay controls.
- Game — game logic manager (turns, special squares, winner detection).
- Player (abstract) — base player; defines state and abstract rollDice() method.
- LuckyPlayer / UnluckyPlayer / NormalPlayer — concrete player types overriding rollDice().
- DiceResult — small value object holding two dice and derived info.
- Board — constants and helper methods for special squares.

---

Build & Run

Command-line (simple javac/java)
1. From the project root where src/ sits:
   - Compile:
     - Unix / macOS:
       javac -d out src/chatdev/boardgame/*.java
     - Windows (PowerShell/CMD):
       javac -d out src\chatdev\boardgame\*.java
   - Run:
     java -cp out chatdev.boardgame.Main

Notes:
- The -d out option places .class files under out/chatdev/boardgame matching package structure.
- Ensure your current working directory includes src/ as shown; adjust paths otherwise.

Create runnable JAR (optional)
1. After compilation into out/:
   jar cfe chatdev-boardgame.jar chatdev.boardgame.Main -C out .
2. Run:
   java -jar chatdev-boardgame.jar

IDE (IntelliJ IDEA / Eclipse)
- Create a new Java project and import the src/ folder as source root.
- Make sure package declaration (package chatdev.boardgame;) remains intact.
- Set Main class to chatdev.boardgame.Main.
- Run application from IDE run configuration.

Maven (optional)
- You may create a Maven project and place sources under src/main/java/chatdev/boardgame/.
- Set mainClass in the maven-jar-plugin or use the maven-shade-plugin to build a runnable JAR.

---

Using the GUI — Controls & Workflow

1. Startup and Setup:
   - When the program starts, a setup dialog asks for number of players (2–6).
   - For each player, enter a name and select a type (Normal, Lucky, Unlucky).
   - The game requires at least two different player types — if not satisfied you will be asked to restart setup.

2. Main window layout:
   - Left pane:
     - Players list: each entry shows name, type, position, and [SkipNext] if they will miss next turn.
     - Controls:
       - Current: shows current player's name and position.
       - Dice: shows last roll (or "DEBUG").
       - Total moves: total number of moves taken in the game.
       - Roll Dice (button) — perform the current player's turn (or use Debug).
       - End Turn (button) — force advance to next player (useful to end a bonus turn or to skip).
       - DEBUG mode (checkbox) — when checked, enables destination field below.
       - Destination field — integer destination (>= 0) for debug moves.
   - Right pane:
     - Message / log area: displays events and landing messages.

3. Playing:
   - Click Roll Dice to take the current player's turn.
     - If DEBUG is unchecked: the player's rollDice() is invoked and movement occurs according to dice sum.
     - If DEBUG is checked and a valid destination is entered: the current player is moved directly to that square (landing effects still apply).
   - Dice label displays the dice result for normal rolls; shows "DEBUG" when a debug move was used.
   - If a player rolls a double (die1 == die2), they receive a bonus turn (the current player remains the same for the next action). The End Turn button can be used to forfeit that bonus turn and move to the next player.
   - If a player must skip next turn, their entry shows [SkipNext] and the next time their turn comes, the skip will be applied, cleared, and the turn moves on.

4. End of game:
   - When a player reaches or passes square 40, the game ends immediately.
   - Messages include winner, total moves, and final positions of all players.
   - Roll and End Turn buttons are disabled after game end.

---

Game Rules & Special Squares (detailed)

Basic movement
- Two six-sided dice are rolled; movement is the sum of the dice.
- Double roll (both dice same value) grants a bonus turn (you play again immediately).
- Players start at square 0.
- First player to reach or pass square 40 wins.

Player types and dice behavior
- LuckyPlayer: rollDice() re-rolls until sum >= 7, so they always get sum 7..12.
- UnluckyPlayer: rollDice() re-rolls until sum <= 6, so they always get sum 2..6.
- NormalPlayer: standard 1..6 per die, sum 2..12.

Special squares and behaviors (the squares are absolute positions)
- Miss a turn: squares 10, 25, 38
  - Landing on these sets a skip-next flag; on the player's next scheduled turn they lose it and do not play (the skip is cleared).
- Surprise card: square 13
  - Landing on 13 randomly changes the player's type to Normal, Lucky, or Unlucky.
  - The player's name, position, skip-next flag, and move count are preserved.
- Forward 3: squares 5, 15, 30
  - Landing on these immediately moves the player forward 3 spaces (pos += 3). This triggers any landing effects at the new position (chainable).
  - Exception: if the player is Unlucky, they do not move forward 3; a message is shown instead.
- Send opponent home: squares 17, 27
  - Landing here forces the opponent who is furthest ahead to be moved back to square 0 (start).
  - If no other players exist (shouldn't happen in normal gameplay), nothing happens.
- Swap with furthest behind: squares 20, 35
  - Landing here swaps positions with the opponent who is currently furthest behind (lowest position).
  - If no other players exist, nothing happens.

Notes on chaining:
- Forward-3 landing can chain into another special square and trigger its effect (e.g., you move forward 3 and land on a miss-turn or swap). The implementation loops to apply effects until no new move occurs from chainable effects.
- Surprise card replaces the player object in the game's player list; state such as position and skip flag are preserved.

Winning
- As soon as a player's position is >= 40, the game finishes.
- Final summary displayed in message area: winner's name, total moves, final positions for all players.

---

Debug Mode

Purpose
- For testing or demonstration, Debug mode lets you set the destination square for the current player rather than rolling dice.

How it works
- Enable the "DEBUG mode" checkbox.
- Enter an integer destination (0 or greater) in the Destination field.
- Click "Roll Dice" — the game will move the current player directly to that destination.
- Landing effects for that square are applied (Skip-turn, Surprise, Forward3, SendHome, Swap).
- Important: In debug mode the code does not simulate a dice double to give a bonus turn; debug movement is deterministic and does not grant an extra roll even if that would have happened with real dice.

Use cases
- Force specific board scenarios to test special squares.
- Reproduce edge cases (e.g., swapping or sending the leader home).
- Demonstrations in teaching or debugging.

---

Example playthrough (sample messages)
Below is a condensed example of messages you might see in the message area during a few turns:

- Game started with 3 players.
- It's Alice's turn (Normal).
- Rolled: 3 + 4 = 7
- Alice moved to 7.
- It's Bob's turn (Lucky).
- Rolled: 6 + 1 = 7 (this was a Lucky roll)
- Bob moved to 7.
- It's Carol's turn (Unlucky).
- Rolled: 1 + 3 = 4
- Carol moved to 4.
- It's Alice's turn (Normal).
- Rolled: 2 + 2 = 4 (Double)
- Alice moved to 11.
- Alice landed on 11 (no special).
- Alice rolled a double and gets a bonus turn!
- ... later ...
- Dave landed on 17 and sends Alice back to start!
- Eve landed on 20 and swaps place with Bob who was furthest behind.
- John landed on 13. Changing type...
- Now John is LuckyPlayer.
- WINNER: Bob reached 41
- Total moves: 37
- Final positions:
  - Alice (Normal): 10
  - Bob (Lucky): 41
  - Carol (Unlucky): 9

---

Developer notes (design, inheritance & polymorphism)

Object-oriented design highlights
- Player is an abstract base class providing shared state:
  - name, position, skipNextTurn flag, move counter, movement helpers, and abstract rollDice() method.
- LuckyPlayer / UnluckyPlayer / NormalPlayer extend Player and override rollDice():
  - The polymorphic rollDice() invocation in Game lets the Game class treat all players uniformly while delegating the actual dice behavior to the concrete class.
- DiceResult encapsulates the two dice values, sum, and isDouble flag — simplifying communication between Player and Game.
- Game manages turn order, total move count, special-square logic, and finishing logic.
- Board is a single place for square constants and helper methods (isMissTurn, isSurpriseCard, etc.).

Key extensibility points
- Add new player types by subclassing Player and overriding rollDice().
- Add new special squares by editing Board constants and adding logic to Game.applyLandingEffects().
- Replace or extend randomization in surprise card behavior (e.g., choose based on probabilities or allow user choice).

Important implementation behaviors to keep in mind
- Surprise card creates a new Player instance of a new type and replaces the old one in the players list while preserving state (position, skipNextTurn, and movesMade).
- Forward-3 movement can chain: after moving +3, the code re-evaluates the new square for possible effects.
- In debug mode the code assumes no double-rolled extra-turn logic.
- Bonus-turn logic: on regular roll, if isDouble is true, Game.performTurn returns without advancing the current player index (so the same player acts again).

---

Troubleshooting & FAQs

Q: The GUI does not start / no window appears.
- Ensure you have a compatible JDK installed and JAVA_HOME set (or java on PATH).
- Run java -version to confirm.
- Run the application from the console so you can see any exceptions printed to stderr.

Q: I get "package chatdev.boardgame does not exist" during compilation.
- Ensure you're compiling from the correct directory and that the package declaration matches your directory layout:
  - source file header: package chatdev.boardgame;
  - source path: src/chatdev/boardgame/YourFile.java
- Use javac -d out src/chatdev/boardgame/*.java (the -d ensures .class files follow package structure).

Q: The GUI is too small / fonts clipped / window cut off?
- Resize the main window; the GUI uses default sizing. Larger screens may need manual resizing.
- If using a high-DPI display, consider increasing font sizes in GameGUI.java (playersList.setFont(...)).

Q: I clicked DEBUG and entered a value, but no extra "bonus turn" occurred.
- This is expected: debug mode moves the player directly and the implementation intentionally bypasses the dice double-based bonus-turn mechanism.

Q: Why does landing on forward-3 sometimes trigger many messages?
- Forward-3 can chain into another special square; the code loops to apply new landing effects until none remain, producing messages for each step.

---

Suggested enhancements (possible next steps)
- Add sound effects and graphics for dice and board.
- Add an animated board visual rather than text list.
- Allow players to choose which opponent to send home or swap with (instead of automatic furthest ahead/behind).
- Provide a replay or save/load game snapshot.
- Implement networked play / AI opponents.

---

Contact & Support
If you need help building or customizing the project, contact ChatDev product support (internal) or consult the code comments for developer-focused guidance.

---

Appendix A — Quick build & run recap

1) Compile:
javac -d out src/chatdev/boardgame/*.java

2) Run:
java -cp out chatdev.boardgame.Main

3) Create runnable JAR (optional):
jar cfe chatdev-boardgame.jar chatdev.boardgame.Main -C out .
java -jar chatdev-boardgame.jar

---

End of manual

If you want, I can also:
- Provide a sample pom.xml or Gradle build script.
- Add screenshots or annotated UI walkthrough images.
- Produce a short demo script or unit tests for Game logic.