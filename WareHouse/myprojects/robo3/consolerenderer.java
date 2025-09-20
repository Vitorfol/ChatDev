'''
ConsoleRenderer: prints the board to the console as a simple ASCII 4x4 (or NxN) grid.
Uses ANSI colors when available. Provides a clearScreen() helper.
'''
package com.chatdev.robot;
import java.util.List;
import java.util.Map;
public class ConsoleRenderer {
    // ANSI escape codes for colors (foreground). Index mapping 0..7: black, red, green, yellow, blue, magenta, cyan, white
    private static final String[] ANSI_COLORS = {
            "\u001B[30m", // black
            "\u001B[31m", // red
            "\u001B[32m", // green
            "\u001B[33m", // yellow
            "\u001B[34m", // blue
            "\u001B[35m", // magenta
            "\u001B[36m", // cyan
            "\u001B[37m"  // white
    };
    private static final String ANSI_RESET = "\u001B[0m";
    private final boolean useAnsi;
    public ConsoleRenderer() {
        // Attempt to detect ANSI support roughly by checking OS; allow environment override if needed.
        String os = System.getProperty("os.name").toLowerCase();
        useAnsi = !os.contains("win") || System.getenv().containsKey("ANSICON") || System.getenv().containsKey("TERM");
    }
    public void clearScreen() {
        if (useAnsi) {
            System.out.print("\u001B[H\u001B[2J");
            System.out.flush();
        } else {
            // fallback: print a bunch of newlines
            for (int i = 0; i < 30; i++) System.out.println();
        }
    }
    public void render(Board board) {
        clearScreen();
        int size = board.getSize();
        Map<Position, Obstacle> obstacles = board.getObstacles();
        List<Robo> robots = board.getRobots();
        Position food = board.getFoodPosition();
        // Build a quick lookup for robots
        java.util.Map<Position, Robo> robotMap = new java.util.HashMap<>();
        for (Robo r : robots) robotMap.put(r.getPosition(), r);
        // print header
        System.out.println("Board (size=" + size + "):");
        // Each cell will be like "[..]" with width 3.
        for (int r = 0; r < size; r++) {
            StringBuilder line = new StringBuilder();
            for (int c = 0; c < size; c++) {
                Position p = new Position(r, c);
                String cell;
                if (food != null && food.equals(p)) {
                    cell = " F ";
                } else if (robotMap.containsKey(p)) {
                    Robo rb = robotMap.get(p);
                    String id = truncateId(rb.getId());
                    if (useAnsi && rb.getColorIndex() >= 0 && rb.getColorIndex() < ANSI_COLORS.length) {
                        cell = ANSI_COLORS[rb.getColorIndex()] + id + ANSI_RESET;
                    } else {
                        cell = id;
                    }
                } else if (obstacles.containsKey(p)) {
                    Obstacle o = obstacles.get(p);
                    cell = " " + o.label() + " ";
                } else {
                    cell = " . ";
                }
                line.append("[").append(cell).append("]");
            }
            System.out.println(line.toString());
        }
        // Print statuses
        System.out.println();
        System.out.println("Robots:");
        for (Robo rb : robots) {
            System.out.printf("%s | Pos:%s | Valid:%d Invalid:%d | Alive:%s | Found:%s%n",
                    rb.getId(), rb.getPosition(), rb.getValidMoves(), rb.getInvalidMoves(), rb.isAlive(), rb.hasFoundFood());
        }
        System.out.println();
    }
    private String truncateId(String id) {
        if (id == null) return "??";
        if (id.length() == 1) return " " + id + " ";
        if (id.length() == 2) return id + " ";
        return id.substring(0, 3);
    }
}