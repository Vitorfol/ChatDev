'''
Board handles the 4x4 grid state: robots, obstacles, food, and move computations.
It provides methods for placing obstacles/food, checking bounds, occupancy, and game end conditions.
Also provides a simple logging hook.
'''
/* '''
Board handles the 4x4 grid state: robots, obstacles, food, and move computations.
It provides methods for placing obstacles/food, checking bounds, occupancy, and game end conditions.
Also provides a simple logging hook.
''' */
import java.awt.Color;
import java.util.*;
import java.util.concurrent.CopyOnWriteArrayList;
public class Board {
    private int size;
    private Map<Position, Obstacle> obstacles = new HashMap<>();
    // Use CopyOnWriteArrayList to avoid ConcurrentModificationExceptions when iterating while robots may be marked dead.
    private List<Robo> robots = new CopyOnWriteArrayList<>();
    private Position food = null;
    private StringBuilder internalLog = new StringBuilder();
    public Board(int size) {
        this.size = size;
    }
    public void clear() {
        obstacles.clear();
        robots.clear();
        food = null;
        internalLog.setLength(0);
    }
    public void addRobot(Robo r) {
        robots.add(r);
    }
    public void removeRobot(Robo r) {
        robots.remove(r);
    }
    public List<Robo> getRobots() {
        return robots;
    }
    public Robo getSingleRobot() {
        if (robots.size() == 0) return null;
        return robots.get(0);
    }
    public void addObstacle(Obstacle o) {
        obstacles.put(o.getPosition(), o);
    }
    public void clearObstacles() {
        obstacles.clear();
    }
    public void placeFood(Position p) {
        food = new Position(p);
    }
    public boolean isFoodAt(Position p) {
        return food != null && food.equals(p);
    }
    public Position getFood() {
        return food == null ? null : new Position(food);
    }
    public boolean isWithinBounds(Position p) {
        return p.row >= 0 && p.row < size && p.col >= 0 && p.col < size;
    }
    public Position computeNewPosition(Position from, int dir) {
        int r = from.row;
        int c = from.col;
        switch (dir) {
            case 0: r = r - 1; break; // up
            case 1: c = c + 1; break; // right
            case 2: r = r + 1; break; // down
            case 3: c = c - 1; break; // left
        }
        return new Position(r, c);
    }
    public boolean isOccupied(Position p) {
        for (Robo r : robots) {
            if (r.isAlive() && r.getPosition().equals(p)) return true;
        }
        return false;
    }
    public boolean isObstacleAt(Position p) {
        return obstacles.containsKey(p);
    }
    public Obstacle getObstacleAt(Position p) {
        return obstacles.get(p);
    }
    public int getSize() {
        return size;
    }
    public void checkGameState() {
        // remove dead robots
        List<Robo> toRemove = new ArrayList<>();
        for (Robo r : robots) {
            if (!r.isAlive()) toRemove.add(r);
        }
        robots.removeAll(toRemove);
    }
    public boolean isFinished() {
        // finished when any robot found food or all robots dead
        for (Robo r : robots) {
            if (r.foundFood()) return true;
        }
        return robots.isEmpty();
    }
    public Map<Position, Obstacle> getObstacles() {
        return obstacles;
    }
    public void log(String s) {
        System.out.println("[Board] " + s);
        internalLog.append(s).append("\n");
    }
    public String getLog() {
        return internalLog.toString();
    }
}