'''
RandomSingleCLI: launches a console run where a single RoboInteligente moves autonomously until it finds food or explodes.
'''
package com.chatdev.robot;
public class RandomSingleCLI {
    public static void main(String[] args) {
        final int size = 4;
        Board board = new Board(size);
        board.placeFoodRandom();
        board.placeObstacleRandom(new Bomb(), 1);
        board.placeObstacleRandom(new Rock(), 2);
        // colorIndex 5 = magenta
        RoboInteligente robot = new RoboInteligente("S1", board.getRandomEmptyPosition(), 5);
        board.addRobot(robot);
        ConsoleRenderer renderer = new ConsoleRenderer();
        renderer.render(board);
        System.out.println("Autonomous robot starting. Press Ctrl+C to stop.");
        while (robot.isAlive() && !robot.hasFoundFood()) {
            try {
                robot.decideAndMove(board);
            } catch (MovimentoInvalidoException ex) {
                System.out.println("Robot cannot move: " + ex.getMessage());
                break;
            }
            renderer.render(board);
            Utils.sleepMillis(500);
        }
        if (!robot.isAlive()) {
            System.out.println("Robot exploded!");
        } else if (robot.hasFoundFood()) {
            System.out.println("Robot found the food!");
        } else {
            System.out.println("Robot stopped.");
        }
    }
}