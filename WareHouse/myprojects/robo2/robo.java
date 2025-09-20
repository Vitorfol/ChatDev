'''
Basic Robo class with position, color, name, move overloads (String and int),
tracking of valid/invalid moves, alive status, food detection.
Updated to pass the robot's original source position to obstacle.interact(...) so
obstacles can reliably compute push-back or other semantics without depending
on r.getPosition() being the original.
'''
import java.awt.Color;
public class Robo {
    protected String name;
    protected Position pos;
    protected Color color;
    protected boolean alive = true;
    protected boolean food = false;
    protected int validMoves = 0;
    protected int invalidMoves = 0;
    public Robo(String name, Position start, Color color) {
        this.name = name;
        this.pos = new Position(start);
        this.color = color;
    }
    public String getName() { return name; }
    public Position getPosition() { return new Position(pos); }
    public void setPosition(Position p) { this.pos = new Position(p); }
    public Color getColor() { return color; }
    public boolean isAlive() { return alive; }
    public void setAlive(boolean a) { alive = a; }
    public boolean foundFood() { return food; }
    public void setFoundFood(boolean f) { food = f; }
    public int getValidMoves() { return validMoves; }
    public int getInvalidMoves() { return invalidMoves; }
    public void incrementValid() { validMoves++; }
    public void incrementInvalid() { invalidMoves++; }
    // overload: string direction
    public boolean move(Board board, String dir) throws MovimentoInvalidoException {
        dir = dir.trim().toUpperCase();
        int d;
        switch (dir) {
            case "UP": d = 0; break;
            case "RIGHT": d = 1; break;
            case "DOWN": d = 2; break;
            case "LEFT": d = 3; break;
            default: throw new MovimentoInvalidoException("Unknown direction: " + dir);
        }
        return move(board, d);
    }
    // overload: int direction 0=up,1=right,2=down,3=left
    public boolean move(Board board, int dir) throws MovimentoInvalidoException {
        if (!alive) throw new MovimentoInvalidoException(name + " is dead and cannot move.");
        Position target = board.computeNewPosition(pos, dir);
        if (!board.isWithinBounds(target)) {
            throw new MovimentoInvalidoException("Move outside board to " + target);
        }
        // If another robot occupies target, invalid
        if (board.isOccupied(target)) {
            throw new MovimentoInvalidoException("Another robot occupies " + target);
        }
        // Check obstacle
        Obstacle ob = board.getObstacleAt(target);
        if (ob != null) {
            // store starting pos before changing
            Position starting = new Position(pos);
            // tentatively move to target (keeps compatibility for obstacles that may inspect r.getPosition())
            pos = new Position(target);
            boolean cont = ob.interact(this, board, dir, starting);
            if (!isAlive()) {
                // Do NOT remove robot from board here to avoid concurrent modification.
                // Let Board.checkGameState() remove dead robots at a safe point.
                incrementValid(); // stepping onto bomb considered a valid action (but kills)
                board.log(name + " exploded and will be removed by Board.checkGameState().");
                return false;
            } else {
                // obstacle handled the interaction (e.g., rock may have moved us back)
                incrementValid();
                // check food at current position (obstacle may have changed pos)
                if (board.isFoodAt(pos)) {
                    setFoundFood(true);
                    board.log(name + " found the food at " + pos + "!");
                }
                return true;
            }
        } else {
            // normal empty or food cell
            pos = new Position(target);
            incrementValid();
            if (board.isFoodAt(pos)) {
                setFoundFood(true);
                board.log(name + " found the food at " + pos + "!");
            }
            return true;
        }
    }
}