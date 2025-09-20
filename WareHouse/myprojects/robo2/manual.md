# Robot Simulator — User & Developer Manual

A small Java-based robot simulation that demonstrates object-oriented design (inheritance, polymorphism, exceptions) on a 4×4 board. The simulator shows robots moving toward food while interacting with obstacles (Bomb and Rock). It includes a Swing GUI where you can run three scenarios: user-controlled single robot, a single intelligent robot (RoboInteligente), and multiple robots running randomly.

This manual covers:
- What the program does
- Requirements
- How to compile and run
- How to use the GUI and controls
- Game rules and behaviors (robots, obstacles, movement, exceptions)
- Developer guide (core classes, extension points)
- Packaging, troubleshooting, and FAQ

---

## Table of contents

- Overview
- Requirements
- Compile & Run
- GUI walkthrough (controls, modes)
- Game rules & behaviors
  - Movement conventions
  - Robo class
  - RoboInteligente behavior
  - Obstacles: Bomb and Rock
  - Board rules, food, and end conditions
- Developer guide (classes & methods)
- Customization and extension examples
- Packaging into a runnable JAR
- Troubleshooting & FAQ
- Contact / License

---

## Overview

The Simulator is a small desktop Java application that visualizes robots moving on a 4×4 grid trying to reach food. Robots can be controlled by the user or run automatically (random moves or intelligent moves). Obstacles can kill robots or push them back. The system uses object-oriented concepts including inheritance, polymorphism and a custom exception (MovimentoInvalidoException) to capture invalid moves.

The GUI shows the board, robots, obstacles and food; it also logs actions and provides controls for stepping the simulation, running it with a configurable delay, and switching scenarios.

---

## Requirements

- Java Development Kit (JDK) 8 or later (recommended Java 11+)
  - The code uses standard Java + Swing, no external libraries.
- Basic terminal / command prompt for compiling and running.
- (Optional) An IDE such as IntelliJ IDEA, Eclipse, or NetBeans for development.

---

## Files (as provided)

Key source files included in the package:

- MainGUI.java — Swing-based simulator launcher (SimulatorFrame).
- Board.java — board logic, robot/obstacle lists, utilities.
- GridPanel.java — custom Swing panel that renders the board.
- Robo.java — base robot class (position, color, movement overloads, stats).
- RoboInteligente.java — intelligent robot subclass (avoid repeating invalid move until a valid one found).
- Obstacle.java — abstract obstacle class (interact method).
- Bomb.java — concrete obstacle; explodes robots.
- Rock.java — concrete obstacle; pushes robot back.
- Position.java — simple row/column holder.
- MovimentoInvalidoException.java — custom exception thrown when a move is invalid.

Note: filenames are case-sensitive on many systems. The main entry point (GUI) is `MainGUI`.

---

## Compile & Run

Assuming all .java files are in one directory:

1. Open terminal and change to the project directory.

2. Compile all Java files:
   javac *.java

   This produces .class files in the same folder.

3. Run the GUI:
   java MainGUI

If you prefer to run from an IDE, create a new Java project, add the files, and run the class MainGUI (it contains main()).

---

## GUI Walkthrough

When you run `MainGUI`, a window titled "Robot Simulator - 4x4 Grid" opens. Main UI components:

- Grid (center): visual 4×4 board showing robots, obstacles, and food.
- Control panel (top):
  - Mode selector (combo box):
    - User-Controlled Single Robot
    - Random Single RoboInteligente
    - Random Multiple Robots
  - Start button — starts automated simulation (for random modes).
  - Step button — executes one step of the simulation.
  - Reset button — resets board for the currently selected mode.
  - Delay (ms) slider — sets delay between automated steps when Start is active.
- Log area (right): textual log of events and per-robot stats.

Initial layout and deterministic placements in the provided code:
- Food placed at (1, 2)
- Bomb at (1, 1)
- Rocks at (2, 1) and (0, 2)
- Default robot placements vary by mode (see reset behavior in code).

Keyboard:
- In "User-Controlled Single Robot" mode you control the robot with arrow keys (Up, Right, Down, Left).
- The window must be focused for arrow keys to work; if keys don't respond, click the window and try again.

Buttons behavior:
- Start: starts a simulation thread (except for user-control mode, where user moves manually).
- Step: performs a single simulation step (random move per robot or one RoboInteligente move).
- Reset: stops simulation thread, restores robots/obstacles/food to defaults for current mode.

Logs & Stats:
- The log area appends messages describing valid moves, invalid attempts, obstacles interactions, robot death, or food discovery.
- After each step / move the system logs robot stats:
  - Position, Alive (true/false), Food found (true/false), Valid moves count, Invalid moves count.

Colors:
- Robots are drawn in their assigned Color (defaults: blue, green, magenta). Dead robots are shown as dark gray.
- Bombs are red circles annotated "BOMB".
- Rocks are gray squares annotated "ROCK".
- Food is an orange circle annotated "FOOD".

---

## Game Rules & Behaviors

This section explains movement conventions, exceptions and interactions.

Movement conventions:
- Directions are represented two ways:
  - String overload: "UP", "RIGHT", "DOWN", "LEFT" (case-insensitive).
  - Integer overload: 0 = UP, 1 = RIGHT, 2 = DOWN, 3 = LEFT.
- Movement calls:
  - Robo.move(Board board, String dir) throws MovimentoInvalidoException
  - Robo.move(Board board, int dir) throws MovimentoInvalidoException

Invalid moves:
- MovimentoInvalidoException is thrown when:
  - Robot is dead but attempted to move.
  - Move would go outside the board.
  - Move target cell is occupied by another alive robot.
  - Unknown direction string passed to string overload.

Robo (base class) behavior:
- Tracks: name, position (Position), color, alive flag, foundFood flag, counts of valid/invalid moves.
- Move semantics:
  - Compute target position.
  - Validate bounds and occupancy; if invalid, throw MovimentoInvalidoException.
  - If target contains an obstacle, the board gives the obstacle to the robot to interact with:
    - Robot sets its pos tentatively to target, then obstacle.interact(...) is called with robot, board, incomingDirection and the original source position (the robot's position before the attempt). This allows obstacles to push robot back reliably.
    - If Bomb interacts → robot dies (alive = false), method returns (considered a valid move for statistics).
    - If Rock interacts → robot likely gets placed back to original position; robot remains alive.
  - If target cell contains food, robot.foundFood is set and board logs it.
  - Robot increments valid or invalid counters accordingly.

RoboInteligente (subclass) behavior:
- Overrides move(Board, int initialDir). It attempts the given direction first; if that attempt throws MovimentoInvalidoException (e.g., out of bounds or occupied), the RoboInteligente catches it, records that direction as tried (and increments invalidMoves), logs avoidance, and tries the next direction (rotating by +1 modulo 4). It never repeats a previously failed direction in the same move call. If all 4 directions are exhausted, it throws MovimentoInvalidoException indicating no valid moves found.
- When RoboInteligente uses super.move and a move succeeds (or robot dies due to Bomb), it returns that result.

Obstacles:

- Obstacle (abstract)
  - Each obstacle holds a Position.
  - Method: boolean interact(Robo r, Board board, int incomingDirection, Position source)
    - The `source` parameter is the robot's original position before attempting the move (defensive copy).
    - Implementations should not rely on r.getPosition() to be the original source; the caller may have set the robot position already to the target for compatibility.

- Bomb
  - Behavior: robot.setAlive(false). Logs explosion. Returns false (robot cannot stand there).
  - The Board.checkGameState later removes dead robots from the list.

- Rock
  - Behavior: tries to push the robot back to `source` if that cell is within bounds, not occupied by another robot, and not occupied by another obstacle. If push-back is possible the robot's position is set back to source and a message is logged. If not possible, robot remains at original (safe) position and message logged. Returns true (robot remains alive).

Board rules:
- Board maintains robot list (CopyOnWriteArrayList to avoid concurrent modification), obstacles map (position → obstacle), and food position.
- Board provides:
  - computeNewPosition(Position from, int dir)
  - isWithinBounds(Position)
  - isOccupied(Position)
  - isObstacleAt(Position)
  - getObstacleAt(Position)
  - placeFood(Position)
  - checkGameState(): removes dead robots from the list (safe removal).
  - isFinished(): simulation ends if any robot found food (r.foundFood()) OR when all robots are dead (empty robot list).
  - log(String): prints to System.out and internal log buffer.

Notes about valid/invalid counters:
- When Robo.move throws MovimentoInvalidoException, the caller (e.g., SimulatorFrame) typically calls r.incrementInvalid() to count the invalid attempt.
- RoboInteligente increments invalid in its own logic when it catches exceptions to try alternatives.

---

## Developer Guide (core classes & extension points)

For developers who want to inspect or extend:

- MainGUI.java (SimulatorFrame)
  - Creates the Board and GridPanel and implements the UI logic (Start/Step/Reset).
  - resetBoardForMode() sets up default positions, obstacles and food. Modify here to change starting scenarios.
  - startSimulation() runs a loop to drive automatic moves for random modes; it uses Thread.sleep(delay).
  - Keyboard input: arrow keys call Robo.move(board, dir) for user-controlled robot.

- Board.java
  - Core responsibilities: bounding, occupancy checks, obstacle registry, robot registry, food position, move calculation, logging and finishing condition.
  - To change board size: instantiate Board with a different size (e.g., new Board(6)).
  - To change obstacles or food location: use addObstacle(), placeFood().

- Robo.java
  - Base robot behaviors and stats.
  - Movement overloads: string and int.
  - Interaction with obstacles uses the new Obstacle.interact signature (with source position) so obstacles can treat push-back correctly.

- RoboInteligente.java
  - Example of a subclass overriding movement behavior. It demonstrates trying alternatives until a valid one is found.

- Obstacle / Bomb / Rock
  - New obstacles can be added by extending Obstacle and implementing interact(...).
  - interact returns boolean that indicates whether the robot remains alive/standing after the interaction.
  - Use board.log(...) to record events.

- GridPanel.java
  - Responsible for rendering. Customize shapes, colors, fonts, sizes here.

Extension points:
- Add more obstacle types (e.g., Sticky, Teleporter, Trap) by subclassing Obstacle.
- Add scoring, multiple food items, pathfinding-based intelligence (A*), or richer user input (text commands, CLI mode).
- Add a CLI main (e.g., MainCLI.java) to drive text-based games for headless environments.

Important design notes:
- Board uses CopyOnWriteArrayList for robots to avoid ConcurrentModificationException when iterating and removing robots. Board.checkGameState() removes dead robots in a safe step.
- Obstacle.interact receives `source` so obstacles do not depend on the robot's current pos for original location; this avoids ambiguity.

---

## Customization examples

Change board size (4 → 6):
- In SimulatorFrame constructor change:
  board = new Board(6);
- Update GridPanel preferred size or scale logic will automatically adapt to new size.

Change default placements:
- In resetBoardForMode() of SimulatorFrame, change positions for robots, food, and obstacles.

Add a new obstacle:
- Create class Sticky extends Obstacle and implement interact(r, board, dir, source).
- Register it with board.addObstacle(new Sticky(new Position(...)));

Add CLI driver (simple outline):
- Implement MainCLI.java that reads console commands (UP/LEFT/RIGHT/DOWN) and calls Board / Robo methods, prints board ASCII to console.
- Use Position and Board.computeNewPosition to simulate moves.

---

## Packaging into a runnable JAR

1. Compile:
   javac *.java

2. Create manifest.txt with:
   Main-Class: MainGUI

   (ensure newline at end)

3. Create JAR:
   jar cfm RobotSimulator.jar manifest.txt *.class

4. Run JAR:
   java -jar RobotSimulator.jar

---

## Troubleshooting & FAQ

Q: Arrow keys don't affect the user-controlled robot.
A: Click the simulator window to ensure it has focus. The frame requests focus, but some platforms/WM may steal it. After clicking the window, arrow keys should be delivered. If not, run in an IDE where focus is managed, or add a button to request focus.

Q: I get NoClassDefFoundError or cannot find main class.
A: Make sure you compiled all files (javac *.java) and run from the directory with the .class files. Class and filenames are case-sensitive on some systems.

Q: Robots stop moving when I press Start.
A: Start creates a thread. If the GUI's simThread is interrupted or encountered an exception, it may stop. Check console output for exceptions. Also, in user-controlled mode Start doesn't automate moves.

Q: How are invalid moves counted?
A: Calls that throw MovimentoInvalidoException typically lead to incrementInvalid() called by the caller (e.g., SimulatorFrame) — RoboInteligente increments its invalids internally when trying alternatives.

Q: Robot stepped on bomb but still appears on the board.
A: Bomb sets robot alive=false. Board.checkGameState() is responsible for removing dead robots; the removal occurs on the next checkGameState call (which is called regularly by the simulator loop, step button, or after user moves). If a live rendering remains until next step, that's expected.

Q: I want a text-mode (CLI) version.
A: The codebase is modular. Implement a simple MainCLI.java that:
- Creates a Board and robots.
- Prints ASCII board.
- Reads user commands or simulates random moves.
- Calls Robo.move(...) and Board.checkGameState().
This is a straightforward exercise using provided classes.

---

## License & Contact

Use and modify the code as needed. If this code came from ChatDev internal project, consult project owner for distribution/license terms. For questions or further feature requests (e.g., pathfinding AI, persistent logging, web UI), contact the product team.

---

Thank you for using the Robot Simulator. If you want, I can:
- Provide a CLI Main implementation (text-based) as an additional file.
- Add a README with build scripts (Ant/Gradle/Maven) or a prebuilt jar.
- Implement additional obstacles or a pathfinding RoboInteligente variant.