'''
GridPanel renders the board visually using Swing components (custom painting).
It draws robots, obstacles, and food, and uses colors to distinguish elements.
'''
/* '''
GridPanel renders the board visually using Swing components (custom painting).
It draws robots, obstacles, and food, and uses colors to distinguish elements.
''' */
import javax.swing.*;
import java.awt.*;
import java.util.Map;
public class GridPanel extends JPanel {
    private Board board;
    private int cellSize = 100;
    public GridPanel(Board board) {
        this.board = board;
        setPreferredSize(new Dimension(board.getSize() * cellSize, board.getSize() * cellSize));
        setBackground(Color.WHITE);
    }
    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        int size = board.getSize();
        int w = getWidth();
        int h = getHeight();
        int cs = Math.min(w / size, h / size);
        // draw grid
        g.setColor(Color.LIGHT_GRAY);
        for (int r = 0; r <= size; r++) {
            g.drawLine(0, r * cs, size * cs, r * cs);
        }
        for (int c = 0; c <= size; c++) {
            g.drawLine(c * cs, 0, c * cs, size * cs);
        }
        // draw obstacles
        for (Map.Entry<Position, Obstacle> e : board.getObstacles().entrySet()) {
            Position p = e.getKey();
            Obstacle ob = e.getValue();
            int x = p.col * cs;
            int y = p.row * cs;
            if (ob instanceof Bomb) {
                g.setColor(Color.RED);
                g.fillOval(x + cs/6, y + cs/6, cs*2/3, cs*2/3);
                g.setColor(Color.BLACK);
                g.drawString("BOMB", x + cs/6 + 5, y + cs/6 + 15);
            } else if (ob instanceof Rock) {
                g.setColor(Color.GRAY);
                g.fillRect(x + cs/8, y + cs/8, cs*3/4, cs*3/4);
                g.setColor(Color.BLACK);
                g.drawString("ROCK", x + cs/8 + 5, y + cs/8 + 15);
            }
        }
        // draw food
        Position food = board.getFood();
        if (food != null) {
            int x = food.col * cs;
            int y = food.row * cs;
            g.setColor(Color.ORANGE);
            g.fillOval(x + cs/4, y + cs/4, cs/2, cs/2);
            g.setColor(Color.BLACK);
            g.drawString("FOOD", x + cs/4 + 5, y + cs/4 + 15);
        }
        // draw robots
        for (Robo r : board.getRobots()) {
            Position p = r.getPosition();
            int x = p.col * cs;
            int y = p.row * cs;
            Color c = r.getColor();
            if (!r.isAlive()) c = Color.DARK_GRAY;
            g.setColor(c);
            g.fillRect(x + cs/10, y + cs/10, cs*8/10, cs*8/10);
            g.setColor(Color.WHITE);
            g.drawString(r.getName(), x + cs/10 + 5, y + cs/10 + 15);
        }
    }
}