'''
RandomMultipleCLI: launches a console run with multiple RoboInteligente moving concurrently on the same board.
Robots move in separate threads until each finds food or explodes. The simulation stops when food is found or all robots stopped.
'''
package com.chatdev.robot;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicBoolean;
public class RandomMultipleCLI {
    public static void main(String[] args) {
        final int size = 4;
        Board board = new Board(size);
        board.placeFoodRandom();
        board.placeObstacleRandom(new Bomb(), 1);
        board.placeObstacleRandom(new Rock(), 2);
        int robotCount = 3;
        List<RoboInteligente> robots = new ArrayList<>();
        // pick color indices for CLI (0..7)
        int[] colors = {1, 2, 4}; // red, green, blue
        for (int i = 0; i < robotCount; i++) {
            RoboInteligente r = new RoboInteligente("R" + (i + 1), board.getRandomEmptyPosition(), colors[i % colors.length]);
            robots.add(r);
            board.addRobot(r);
        }
        ConsoleRenderer renderer = new ConsoleRenderer();
        AtomicBoolean stopFlag = new AtomicBoolean(false);
        List<Thread> threads = new ArrayList<>();
        // Start robot threads
        for (RoboInteligente r : robots) {
            Thread t = new Thread(() -> {
                while (!stopFlag.get() && r.isAlive() && !r.hasFoundFood()) {
                    try {
                        r.decideAndMove(board);
                    } catch (MovimentoInvalidoException ex) {
                        // this robot can't move anymore; stop its loop
                        break;
                    }
                    Utils.sleepMillis(300 + (int)(Math.random() * 400));
                }
            }, "RobotThread-" + r.getId());
            t.start();
            threads.add(t);
        }
        // Main loop: render periodically and detect termination
        boolean anyFound = false;
        boolean anyAlive = true;
        while (!anyFound && anyAlive) {
            renderer.render(board);
            anyFound = false;
            anyAlive = false;
            for (Robo r : robots) {
                if (r.hasFoundFood()) anyFound = true;
                if (r.isAlive() && !r.hasFoundFood()) anyAlive = true;
            }
            if (anyFound) {
                System.out.println("A robot found the food! Simulation ends.");
                break;
            }
            if (!anyAlive) {
                System.out.println("All robots dead/stopped. Simulation ends.");
                break;
            }
            Utils.sleepMillis(400);
        }
        // Signal threads to stop and join
        stopFlag.set(true);
        for (Thread t : threads) {
            try {
                t.join(200);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
        // Final render and status
        renderer.render(board);
        System.out.println("Final statuses:");
        for (Robo r : robots) {
            System.out.printf("%s | Pos:%s | Valid:%d Invalid:%d | Alive:%s | Found:%s%n",
                    r.getId(), r.getPosition(), r.getValidMoves(), r.getInvalidMoves(), r.isAlive(), r.hasFoundFood());
        }
    }
}