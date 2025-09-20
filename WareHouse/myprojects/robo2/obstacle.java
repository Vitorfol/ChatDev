'''
Abstract Obstacle class. Concrete obstacles must implement interact.
This version uses defensive copies for positions and provides an explicit
'source' parameter so obstacles can rely on the robot's original position
(before the attempted move). Implementations should NOT rely on r.getPosition()
being the original source.
'''
public abstract class Obstacle {
    protected Position pos;
    public Obstacle(Position p) {
        this.pos = new Position(p);
    }
    public Position getPosition() {
        return new Position(pos);
    }
    /**
     * Interact with a robot trying to move from source -> this.pos with incomingDirection.
     * @param r the robot (note: r.getPosition() may be the tentative target depending on caller; do not rely on it)
     * @param board board context
     * @param incomingDirection direction robot used to enter obstacle cell (0=up,1=right,2=down,3=left)
     * @param source the robot position before attempting the move (defensive copy)
     * @return true if robot remains alive / standing on that cell; false if robot destroyed or cannot stand there
     */
    public abstract boolean interact(Robo r, Board board, int incomingDirection, Position source);
}