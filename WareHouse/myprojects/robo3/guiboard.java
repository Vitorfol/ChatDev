'''
GUIBoard: Swing panel that renders the board as a grid with robots, obstacles, and food.
It uses colors for robots and draws simple labels for obstacles and food.
'''
/*
DOCSTRING
GUIBoard: Swing panel that renders the board as a grid with robots, obstacles, and food.
It uses colors for robots and draws simple labels for obstacles and food.
*/
import javax.swing.*;
import java.awt.*;
import java.util.Map;
public class GUIBoard extends JPanel {
    private final Board board;
    public GUIBoard(Board board) {
        this.board = board;
        setPreferredSize(new Dimension(500, 500));
        setBackground(Color.WHITE);
    }
    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        int size = board.getSize();
        int w = getWidth();
        int h = getHeight();
        int cellW = w / size;
        int cellH = h / size;
        // draw grid
        g.setColor(Color.LIGHT_GRAY);
        for (int i = 0; i <= size; i++) {
            g.drawLine(0, i * cellH, w, i * cellH);
            g.drawLine(i * cellW, 0, i * cellW, h);
        }
        // draw obstacles
        Map<Position, Obstacle> obstacles = board.getObstacles();
        for (Map.Entry<Position, Obstacle> e : obstacles.entrySet()) {
            Position p = e.getKey();
            Obstacle o = e.getValue();
            int x = p.col() * cellW;
            int y = p.row() * cellH;
            g.setColor(Color.DARK_GRAY);
            g.fillRect(x + 2, y + 2, cellW - 4, cellH - 4);
            g.setColor(Color.WHITE);
            g.drawString(o.label(), x + cellW / 2 - 4, y + cellH / 2 + 5);
        }
        // draw food
        Position food = board.getFoodPosition();
        if (food != null) {
            int x = food.col() * cellW;
            int y = food.row() * cellH;
            g.setColor(Color.ORANGE);
            g.fillOval(x + cellW/4, y + cellH/4, cellW/2, cellH/2);
            g.setColor(Color.BLACK);
            g.drawString("F", x + cellW/2 - 4, y + cellH/2 + 5);
        }
        // draw robots
        for (Robo r : board.getRobots()) {
            Position p = r.getPosition();
            int x = p.col() * cellW;
            int y = p.row() * cellH;
            g.setColor(r.getColor());
            g.fillOval(x + 6, y + 6, cellW - 12, cellH - 12);
            g.setColor(Color.BLACK);
            g.drawString(r.getId(), x + 8, y + 16);
            // indicate status
            if (!r.isAlive()) {
                g.setColor(Color.BLACK);
                g.drawString("X", x + cellW - 14, y + cellH - 6);
            } else if (r.hasFoundFood()) {
                g.setColor(Color.GREEN.darker());
                g.drawString("✓", x + cellW - 14, y + cellH - 6);
            }
        }
    }
}