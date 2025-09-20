'''
Robo: base robot class with id, position, color (as ANSI code index), stats and movement methods.
Provides move(String dir, Board) and move(int dir, Board) overloads.
Possible directions: "UP","DOWN","LEFT","RIGHT" (case-insensitive)
Integer mapping: 0=UP,1=RIGHT,2=DOWN,3=LEFT
'''
package com.chatdev.robot;
import java.util.Objects;
public class Robo {
    private final String id;
    private Position position;
    // For CLI we store a simple ANSI color code index (0..7); -1 means default.
    private final int colorIndex;
    private boolean alive = true;
    private boolean foundFood = false;
    private int validMoves = 0;
    private int invalidMoves = 0;
    public Robo(String id, Position start, int colorIndex) {
        this.id = Objects.requireNonNull(id);
        this.position = Objects.requireNonNull(start);
        this.colorIndex = colorIndex;
    }
    public String getId() { return id; }
    public Position getPosition() { return position; }
    public int getColorIndex() { return colorIndex; }
    public boolean isAlive() { return alive; }
    public boolean hasFoundFood() { return foundFood; }
    public int getValidMoves() { return validMoves; }
    public int getInvalidMoves() { return invalidMoves; }
    public void setAlive(boolean a) { this.alive = a; }
    public void setPosition(Position p) { this.position = p; }
    public void setFoundFood(boolean f) { this.foundFood = f; }
    // String direction overload
    public void move(String dir, Board board) throws MovimentoInvalidoException {
        String d = dir.trim().toUpperCase();
        int dr = 0, dc = 0;
        switch (d) {
            case "UP": dr = -1; dc = 0; break;
            case "DOWN": dr = 1; dc = 0; break;
            case "LEFT": dr = 0; dc = -1; break;
            case "RIGHT": dr = 0; dc = 1; break;
            default:
                throw new MovimentoInvalidoException("Unknown direction: " + dir);
        }
        moveBy(dr, dc, board);
    }
    // Integer direction overload: 0=UP,1=RIGHT,2=DOWN,3=LEFT
    public void move(int dir, Board board) throws MovimentoInvalidoException {
        switch (dir) {
            case 0: move("UP", board); break;
            case 1: move("RIGHT", board); break;
            case 2: move("DOWN", board); break;
            case 3: move("LEFT", board); break;
            default:
                throw new MovimentoInvalidoException("Unknown numeric direction: " + dir);
        }
    }
    // Helper to attempt movement by delta
    protected synchronized void moveBy(int dr, int dc, Board board) throws MovimentoInvalidoException {
        if (!alive) {
            invalidMoves++;
            throw new MovimentoInvalidoException("Robot is not alive");
        }
        Position target = position.translate(dr, dc);
        if (!board.isWithinBounds(target)) {
            invalidMoves++;
            throw new MovimentoInvalidoException("Out of bounds: " + target);
        }
        // If another robot occupies the target
        Robo occupying = board.getRobotAt(target);
        if (occupying != null && occupying != this) {
            invalidMoves++;
            throw new MovimentoInvalidoException("Cell occupied by another robot at " + target);
        }
        // Save previous
        Position prev = position;
        // Move into cell (board will update robot map)
        board.updateRobotPosition(this, target);
        // Handle obstacles
        Obstacle obst = board.getObstacleAt(target);
        if (obst != null) {
            obst.interact(this, board, prev);
        }
        // Check if robot alive and update found food
        if (this.isAlive()) {
            if (board.hasFoodAt(target)) {
                this.foundFood = true;
                board.removeFood(); // Food found; remove from board
            }
            validMoves++;
        }
    }
    @Override
    public String toString() {
        return id;
    }
}