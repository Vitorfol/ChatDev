'''
Bomb obstacle: robot explodes when stepping on it.
Uses the new interact signature that receives the robot's source position.
'''
public class Bomb extends Obstacle {
    public Bomb(Position p) {
        super(p);
    }
    @Override
    public boolean interact(Robo r, Board board, int incomingDirection, Position source) {
        // explode robot: robot dies and is removed from board logically.
        r.setAlive(false);
        board.log(r.getName() + " stepped on a Bomb at " + pos + " and exploded!");
        return false; // cannot stand on bomb; robot is destroyed
    }
    @Override
    public String toString() {
        return "Bomb@" + pos;
    }
}