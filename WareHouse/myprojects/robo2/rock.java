'''
Rock obstacle: pushes robot back when stepping on it.
Uses the new interact signature that receives the robot's source (original) position.
Behavior: the robot will be returned to its original cell (source) if possible.
'''
public class Rock extends Obstacle {
    public Rock(Position p) {
        super(p);
    }
    @Override
    public boolean interact(Robo r, Board board, int incomingDirection, Position source) {
        // Use the provided source position (the robot's position before attempting the move)
        Position original = new Position(source);
        // If original is within bounds and not occupied by another robot and not an obstacle, move robot back there
        if (board.isWithinBounds(original) && !board.isOccupied(original) && !board.isObstacleAt(original)) {
            r.setPosition(original);
            board.log(r.getName() + " was pushed back by Rock at " + pos + " to " + original);
        } else {
            // cannot push further; keep robot at original for safety (prefer not to leave robot in obstacle cell)
            r.setPosition(original);
            board.log(r.getName() + " hit a Rock at " + pos + " and could not be pushed back further; stays at " + original);
        }
        return true; // interaction handled; robot remains alive
    }
    @Override
    public String toString() {
        return "Rock@" + pos;
    }
}