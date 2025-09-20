# Robot Simulator — User Manual

A small, object-oriented Java application (GUI + CLI) that simulates robots moving on an N×N board searching for food while interacting with obstacles. The system demonstrates inheritance, polymorphism, exceptions, multi-threading and simple design patterns. It includes user-controlled and autonomous robots and both console and Swing graphical frontends.

This manual explains what the software does, how it is organized, how to build and run it (CLI and GUI), user controls, configuration points, design notes, and troubleshooting tips.

---

Table of contents
- Overview
- Features
- Project layout (important files & classes)
- Installation / prerequisites
- Build instructions (simple javac and suggested Maven layout)
- Run instructions (CLI and GUI modes)
- How to play / how it behaves
- Configuration & customization (board size, obstacles, delays, colors)
- Design notes (OOP, patterns, thread-safety)
- Troubleshooting
- Extending the project
- Support

---

Overview
--------
This project implements a robot simulation on a square board (default 4×4). Robots move around, encounter obstacles (Bomb and Rock), and try to find a food cell. Movements can be initiated by a user (GUI or CLI) or by intelligent robots (RoboInteligente) which autonomously decide moves and avoid repeating invalid moves during a single decision attempt.

Key behaviours:
- Bomb: robot steps on a bomb → explodes (dead) and removed from board.
- Rock: robot steps on a rock → pushed back to previous cell (if possible).
- Food: robot that steps on the food cell wins; the food is removed and simulation ends.
- RoboInteligente: chooses random directions and, within a decision cycle, does not repeat the same invalid move; if all directions are invalid it stops (throws MovimentoInvalidoException).
- Board methods are synchronized for thread-safety so multiple robots may act concurrently.

Features
--------
- CLI and Swing GUI frontends.
- User-controlled single robot (GUI and CLI).
- Autonomous RoboInteligente single robot (GUI and CLI).
- Autonomous RoboInteligente multiple robots moving concurrently (GUI and CLI).
- Obstacles: Bomb (explosion) and Rock (push-back).
- Console ANSI color support (if terminal supports ANSI).
- Simple status tracking (valid/invalid moves, alive/found food).
- Custom checked exception MovimentoInvalidoException for invalid moves.

Project layout (key classes)
----------------------------
(Your source files are provided in the repository. These are the main files and a short description.)

- com.chatdev.robot.MovimentoInvalidoException — checked exception for invalid moves.
- com.chatdev.robot.Position — immutable row/col pair.
- com.chatdev.robot.Obstacle (abstract) — obstacle API: interact(Robo, Board, Position).
  - com.chatdev.robot.Bomb — concrete; explodes robot and removes bomb.
  - com.chatdev.robot.Rock — concrete; tries to push robot back to previous cell.
- com.chatdev.robot.Robo — base robot (id, position, color index, stats). move(String) and move(int) overloads.
- com.chatdev.robot.RoboInteligente — extends Robo; decideAndMove(Board) picks random directions without repeating the same invalid move in the same attempt.
- com.chatdev.robot.Board — manages grid, robots, obstacles, food. Synchronized methods for thread-safety.
- com.chatdev.robot.Utils — small utilities (sleepMillis).
- com.chatdev.robot.ConsoleRenderer — renders the board in the console using optional ANSI colors.
- com.chatdev.robot.GUIBoard — Swing JPanel that paints the board (robots, obstacles, food).
- Launcher (Launcher.java) — GUI launcher to pick GUI modes.
- UserMain, RandomSingleMain, RandomMultipleMain — GUI entry points.
- UserMainCLI, RandomSingleCLI, RandomMultipleCLI — console entry points.

Note: many source files use the package com.chatdev.robot. Ensure files are placed under src/com/chatdev/robot for compilation unless you intentionally change package declarations.

Installation / prerequisites
----------------------------
Minimum requirements:
- Java Development Kit (JDK) 11 or later. JDK 17 or JDK 21 recommended.
- On Windows, to get ANSI colors in console you may need a terminal that supports ANSI (Windows Terminal, Git Bash, or enable virtual terminal processing) or set environment variable ANSICON/TERM if using a compatible ANSI wrapper.

Recommended:
- A build tool (optional) such as Maven or Gradle makes compilation and packaging easier.
- For GUI run you need a Java that includes Swing (standard JDKs do).

Build instructions (simple javac)
---------------------------------
Assuming the code layout where classes with `package com.chatdev.robot;` are in `src/com/chatdev/robot/` and others (if any) in `src/`:

1. Create directories (if not already):
   - src/com/chatdev/robot/

2. Place all files that declare `package com.chatdev.robot;` into `src/com/chatdev/robot/`. If some GUI classes do not declare a package, either:
   - Move them into the same package by adding `package com.chatdev.robot;` at the top (recommended for simplicity), or
   - Keep them without package and compile accordingly—but the simplest path is to put everything in `com.chatdev.robot`.

3. Compile:
   From project root:
   - Create an output directory:
     mkdir -p out
   - Compile all Java files:
     javac -d out src/com/chatdev/robot/*.java src/*.java
     (If all files are in package com.chatdev.robot, you can do `javac -d out src/com/chatdev/robot/*.java`)

4. Run:
   - For CLI main class (example: UserMainCLI):
     java -cp out com.chatdev.robot.UserMainCLI
   - For GUI launcher:
     java -cp out Launcher
   - For other mains, use the fully-qualified class name (see Run instructions below).

Build with Maven (recommended for larger projects)
- If you prefer Maven, create a standard Maven project layout:
  - src/main/java/com/chatdev/robot/*.java
  - Add a pom.xml (set Java version) and use `mvn compile` and `mvn exec:java -Dexec.mainClass="com.chatdev.robot.UserMainCLI"` or create an executable jar with `mvn package`.

Run instructions
----------------

General guidance: run the Java main classes by their fully qualified names or through the Launcher GUI.

GUI modes
- Launcher (graphical selector)
  - Run: java -cp out Launcher
  - Opens a small window with three buttons: "User Controlled (Single Robot)", "Random Single Robot", "Random Multiple Robots". Each button launches a GUI main window.

- Direct GUI mains:
  - User-controlled single robot (GUI):
    java -cp out UserMain
    (If UserMain is in package com.chatdev.robot then run: java -cp out com.chatdev.robot.UserMain)
    Controls: on-screen arrow buttons (Up, Down, Left, Right).
  - Random single RoboInteligente (GUI):
    java -cp out RandomSingleMain
    (or fully qualified)
  - Random multiple RoboInteligente (GUI):
    java -cp out RandomMultipleMain
    (or fully qualified)

CLI (console) modes
- User-controlled single robot in console:
  java -cp out com.chatdev.robot.UserMainCLI
  Controls (when the program prompts):
    - w  or up    → UP
    - s  or down  → DOWN
    - a  or left  → LEFT
    - d  or right → RIGHT
    - q, quit, exit → exit program

- Autonomous single RoboInteligente in console:
  java -cp out com.chatdev.robot.RandomSingleCLI

- Autonomous multiple RoboInteligente in console:
  java -cp out com.chatdev.robot.RandomMultipleCLI

Notes:
- The console renderer will auto-detect ANSI color support. On Windows legacy consoles colors might not work; use Windows Terminal, Git Bash, or enable ANSI support.

How to play / expected behaviour
--------------------------------
User-controlled modes:
- Use the controls to move your robot around the board. Each move translates into a change of position (UP, DOWN, LEFT, RIGHT).
- If you try to move out of bounds, into a cell occupied by another robot, or if your robot is dead, a MovimentoInvalidoException is thrown and, in GUI, a dialog notifies you; in CLI a message prints.
- If your robot steps on a Bomb, it explodes: robot is set to not alive and removed from board.
- If your robot steps on a Rock, the Rock's logic tries to push the robot back to its previous position (if empty and within bounds). If not possible, robot stays on the rock.
- If your robot steps on the food cell, it is marked as having found food and the food is removed. Simulation ends, and a message is shown.

Autonomous modes:
- RoboInteligente calls decideAndMove(Board). In each decision it will try directions in a random order, and in that decision cycle it will not repeat the same invalid move. If it exhausts all directions the method throws MovimentoInvalidoException and the robot stops trying.
- In multiple-robot modes, each robot runs in its own thread; Board methods are synchronized so operations are thread-safe.

Statuses:
- Each robot tracks validMoves / invalidMoves, alive status, and whether it found food. The ConsoleRenderer and GUI show these statuses.

Configuration & customization
-----------------------------
Common parameters you may want to change are in the main classes or Board constructor calls:

- Board size:
  - Default is 4 in the provided mains (Board(4)). To change to N, edit the relevant Main class and replace 4 with the desired integer.

- Number and types of obstacles:
  - Each main calls board.placeObstacleRandom(new Bomb(), count) or placeObstacleRandom(new Rock(), count). Modify counts or add new obstacle types by implementing Obstacle subclasses.

- Food position:
  - By default the food is placed randomly using board.placeFoodRandom(). You can call board.placeFood(new Position(r, c)) to place explicitly.

- Robot color indices (CLI):
  - Robo constructors in CLI examples accept a colorIndex (0..7). See ConsoleRenderer for mapping (0=black, 1=red, 2=green, 3=yellow, 4=blue, 5=magenta, 6=cyan, 7=white).

- Delays (visualization speed):
  - The mains use Utils.sleepMillis(...) (or Thread.sleep) to pace the autonomous robots. Change those values to slow down or speed up the simulation.

- GUI color drawing:
  - GUIBoard uses java.awt.Color for robot display. Change or compute colors by altering Robo or GUIBoard to use different colors.

Design notes (OOP, patterns, thread-safety)
-------------------------------------------
- Inheritance & Polymorphism:
  - Obstacle is abstract; Bomb and Rock implement different interactions via override of interact(...).
  - RoboInteligente extends Robo and overrides/extends behavior by providing decideAndMove.
- Exception:
  - MovimentoInvalidoException is a checked exception used to explicitly indicate invalid movement attempts.
- Threading:
  - Board methods that mutate/read shared state are synchronized (isWithinBounds, updateRobotPosition, getRobotAt, addRobot, removeRobot etc.) to keep operations atomic and safe for concurrent robot threads.
- Design patterns:
  - Strategy-like behavior: Obstacle subclasses encapsulate behavior for interactions.
  - Factory-like behavior: Board.placeObstacleRandom uses reflection to instantiate multiple instances if necessary (a light-weight factory approach).
  - Observer / MVC: GUIBoard & ConsoleRenderer act as "views" that render Board state (simple separation of data and rendering).
- Concurrency model:
  - Each RoboInteligente can be executed in a dedicated thread; shared state access is coordinated by Board synchronization.

Troubleshooting
---------------
- "Class not found" or "NoClassDefFoundError":
  - Ensure class files are in the correct package directories and you run with the correct fully qualified main class name.
  - Ensure you used `javac -d out` to put compiled classes into the correct package structure (out/com/chatdev/robot/...).

- GUI not showing or Swing exceptions:
  - Ensure you call Swing code on the Event Dispatch Thread (Mains use SwingUtilities.invokeLater). If you modified mains, maintain Swing thread discipline.

- ANSI colors not showing on Windows:
  - Use Windows Terminal, Git Bash, or enable ANSI support. The ConsoleRenderer detects ANSI roughly; you can force enabling by running the terminal with TERM set (e.g., use Git Bash).

- Overlapping classes or package mismatch:
  - If some files are in default package and others in com.chatdev.robot, compilation and class loading can be confusing. Best practice: put all related classes into the same package com.chatdev.robot.

Extending the project
---------------------
- Add new obstacles:
  - Create new class extending Obstacle, implement interact(...) and label(), and add placement in main(s).
- Add new robot behaviors:
  - Extend Robo to implement different decision strategies (e.g., deterministic search, BFS/heuristic pathfinding).
- Persist simulation:
  - Add logging of moves/timestamps to file or serialize Board state.
- Add command-line arguments:
  - Edit mains to parse args (e.g., board size, robot count, obstacle counts) and pass them to Board and placement methods.
- Add tests:
  - Add JUnit tests for movement, obstacle interactions, and Board operations.

Example usage sessions
----------------------
1) Quick CLI run (autonomous single robot)
- Compile:
  javac -d out src/com/chatdev/robot/*.java
- Run:
  java -cp out com.chatdev.robot.RandomSingleCLI

2) Run GUI launcher
- Compile:
  javac -d out src/com/chatdev/robot/*.java src/*.java
- Run:
  java -cp out Launcher
- Click the desired mode and play with arrow buttons.

3) Play in console (user-controlled)
- Run:
  java -cp out com.chatdev.robot.UserMainCLI
- Follow prompts; use w/a/s/d to move.

Sample console output (truncated)
- Board (size=4):
  [ . ][ . ][ . ][ . ]
  [ . ][ R ][ . ][ F ]
  [ P ][ . ][ B ][ . ]
  [ . ][ . ][ . ][ . ]

  Robots:
  P | Pos:(2,0) | Valid:1 Invalid:0 | Alive:true | Found:false

Notes on safety and limits
--------------------------
- Multiple RoboInteligente threads access the same Board. Race conditions for simultaneous moves on the same cell are avoided by Board synchronization but simultaneous logical conflicts (two robots deciding to move to the same empty target) will be resolved by the order in which the synchronized method runs; one robot will succeed and the other will find the cell occupied and receive MovimentoInvalidoException.
- Board.placeObstacleRandom uses limited attempts to avoid infinite loops when the board is densely populated.

Support
-------
- For help running the project ensure JDK is installed and in PATH.
- Verify package and directory alignment: com.chatdev.robot.* files must be under src/com/chatdev/robot/.
- If you want, we can provide a ready-to-run Maven project (pom.xml) and prebuilt jar.

License & acknowledgements
--------------------------
- This repository is an educational/demo-style project demonstrating OOP and concurrency in Java.

---

If you want, I can:
- Provide a sample pom.xml and Maven instructions to build a jar with a chosen main class.
- Generate a small README.sh script to compile and run all modes easily.
- Convert GUI classes to the `com.chatdev.robot` package (if you have package-mismatch issues) and produce a consistent, ready-to-compile source tree.

Which of these would you prefer next?