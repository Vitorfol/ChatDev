'''
Board: manages the 2D grid, obstacles, robots, and food.
Provides synchronized methods to safely update positions from multiple threads.
'''
package com.chatdev.robot;
import java.util.*;
import java.util.List;
public class Board {
    private final int size;
    private final Map<Position, Obstacle> obstacles = new HashMap<>();
    private final Map<Position, Robo> robotsPos = new HashMap<>();
    private final List<Robo> robotsList = new ArrayList<>();
    private Position foodPosition = null;
    private final Random rand = new Random();
    public Board(int size) {
        if (size <= 0) throw new IllegalArgumentException("Size must be positive");
        this.size = size;
    }
    public int getSize() { return size; }
    public synchronized boolean isWithinBounds(Position p) {
        return p != null && p.row() >= 0 && p.row() < size && p.col() >= 0 && p.col() < size;
    }
    // A cell is considered empty for robot placement if there is no robot and no obstacle and not food.
    public synchronized boolean isCellEmpty(Position p) {
        if (!isWithinBounds(p)) return false;
        return !robotsPos.containsKey(p) && !obstacles.containsKey(p) && (foodPosition == null || !foodPosition.equals(p));
    }
    public synchronized void addRobot(Robo r) {
        Position p = r.getPosition();
        if (!isWithinBounds(p)) throw new IllegalArgumentException("Robot position out of bounds: " + p);
        if (!isCellEmpty(p)) throw new IllegalArgumentException("Cell not empty for robot " + r.getId() + " at " + p);
        robotsList.add(r);
        robotsPos.put(p, r);
    }
    public synchronized void removeRobot(Robo r) {
        robotsList.remove(r);
        robotsPos.remove(r.getPosition());
    }
    public synchronized Robo getRobotAt(Position p) {
        return robotsPos.get(p);
    }
    public synchronized Obstacle getObstacleAt(Position p) {
        return obstacles.get(p);
    }
    public synchronized void addObstacle(Position p, Obstacle o) {
        if (isWithinBounds(p)) {
            obstacles.put(p, o);
        }
    }
    public synchronized void removeObstacleAt(Position p) {
        obstacles.remove(p);
    }
    public synchronized void placeFood(Position p) {
        if (isWithinBounds(p)) {
            foodPosition = p;
        }
    }
    public synchronized void placeFoodRandom() {
        Position p;
        int attempts = 0;
        do {
            p = new Position(rand.nextInt(size), rand.nextInt(size));
            attempts++;
            if (attempts > 100) break;
        } while (!isCellAvailableForFood(p));
        placeFood(p);
    }
    private synchronized boolean isCellAvailableForFood(Position p) {
        return isWithinBounds(p) && !robotsPos.containsKey(p) && !obstacles.containsKey(p);
    }
    public synchronized boolean hasFoodAt(Position p) {
        return foodPosition != null && foodPosition.equals(p);
    }
    public synchronized Position getFoodPosition() {
        return foodPosition;
    }
    public synchronized void removeFood() {
        foodPosition = null;
    }
    // Update robot position atomically for thread safety
    public synchronized void updateRobotPosition(Robo r, Position newPos) {
        // Remove from old if present
        robotsPos.remove(r.getPosition());
        r.setPosition(newPos);
        robotsPos.put(newPos, r);
    }
    public synchronized Position getRandomEmptyPosition() {
        Position p;
        int attempts = 0;
        do {
            p = new Position(rand.nextInt(size), rand.nextInt(size));
            attempts++;
            if (attempts > 500) break;
        } while (!isCellEmpty(p));
        return p;
    }
    // Place 'count' obstacles; prototype used to instantiate separate instances when possible
    public synchronized void placeObstacleRandom(Obstacle prototype, int count) {
        int placed = 0;
        int attempts = 0;
        while (placed < count && attempts < 500) {
            Position p = new Position(rand.nextInt(size), rand.nextInt(size));
            if (!obstacles.containsKey(p) && !robotsPos.containsKey(p) && (foodPosition == null || !foodPosition.equals(p))) {
                Obstacle instance = prototype;
                if (count > 1) {
                    try {
                        instance = prototype.getClass().getDeclaredConstructor().newInstance();
                    } catch (Exception ex) {
                        instance = prototype; // fallback
                    }
                }
                obstacles.put(p, instance);
                placed++;
            }
            attempts++;
        }
    }
    public synchronized List<Robo> getRobots() {
        return new ArrayList<>(robotsList);
    }
    public synchronized Map<Position, Obstacle> getObstacles() {
        return new HashMap<>(obstacles);
    }
}