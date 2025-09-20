'''
UserMainCLI: console main where a single robot is controlled by the user via WASD or UP/DOWN/LEFT/RIGHT words.
A NxN board is displayed with food and obstacles. The user moves the robot until it finds food or explodes.
'''
package com.chatdev.robot;
import java.util.Scanner;
public class UserMainCLI {
    public static void main(String[] args) {
        final int size = 4;
        Board board = new Board(size);
        board.placeFoodRandom();
        board.placeObstacleRandom(new Bomb(), 1);
        board.placeObstacleRandom(new Rock(), 2);
        // choose a color index (0..7). We'll pick 4 = blue by default.
        int colorIndex = 4;
        Robo player = new Robo("P", board.getRandomEmptyPosition(), colorIndex);
        board.addRobot(player);
        ConsoleRenderer renderer = new ConsoleRenderer();
        Scanner scanner = new Scanner(System.in);
        renderer.render(board);
        System.out.println("Controls: w=UP, s=DOWN, a=LEFT, d=RIGHT, q=quit");
        while (player.isAlive() && !player.hasFoundFood()) {
            System.out.print("Command> ");
            String cmd = scanner.nextLine().trim();
            if (cmd.isEmpty()) continue;
            if (cmd.equalsIgnoreCase("q") || cmd.equalsIgnoreCase("quit") || cmd.equalsIgnoreCase("exit")) {
                System.out.println("Exiting.");
                break;
            }
            String dir = mapInputToDirection(cmd);
            if (dir == null) {
                System.out.println("Unknown command. Use w/a/s/d or up/down/left/right.");
                continue;
            }
            try {
                player.move(dir, board);
            } catch (MovimentoInvalidoException ex) {
                System.out.println("Invalid move: " + ex.getMessage());
            }
            renderer.render(board);
        }
        if (!player.isAlive()) {
            System.out.println("Robot exploded! Game over.");
        } else if (player.hasFoundFood()) {
            System.out.println("You found the food! Congrats!");
        }
    }
    private static String mapInputToDirection(String in) {
        String s = in.trim().toLowerCase();
        switch (s) {
            case "w": case "up": return "UP";
            case "s": case "down": return "DOWN";
            case "a": case "left": return "LEFT";
            case "d": case "right": return "RIGHT";
            default: return null;
        }
    }
}