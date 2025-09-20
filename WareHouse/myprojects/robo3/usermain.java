'''
UserMain: GUI where a single robot is controlled by the user via arrow buttons.
A 4x4 board is displayed with food and obstacles. The user moves the robot until it finds food or explodes.
'''
/*
DOCSTRING
UserMain: GUI where a single robot is controlled by the user via arrow buttons.
A 4x4 board is displayed with food and obstacles. The user moves the robot until it finds food or explodes.
*/
import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
public class UserMain {
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            Board board = new Board(4);
            // Place food and obstacles
            board.placeFoodRandom();
            board.placeObstacleRandom(new Bomb(), 1);
            board.placeObstacleRandom(new Rock(), 2);
            // Create single robot at a random empty spot
            Robo player = new Robo("Player", board.getRandomEmptyPosition(), Color.BLUE);
            board.addRobot(player);
            JFrame frame = new JFrame("User Controlled Robot");
            frame.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
            frame.setSize(600, 700);
            frame.setLayout(new BorderLayout());
            GUIBoard gui = new GUIBoard(board);
            frame.add(gui, BorderLayout.CENTER);
            JPanel controlPanel = new JPanel();
            controlPanel.setLayout(new GridBagLayout());
            JButton up = new JButton("Up");
            JButton down = new JButton("Down");
            JButton left = new JButton("Left");
            JButton right = new JButton("Right");
            up.addActionListener(e -> doMove(player, "UP", board, gui));
            down.addActionListener(e -> doMove(player, "DOWN", board, gui));
            left.addActionListener(e -> doMove(player, "LEFT", board, gui));
            right.addActionListener(e -> doMove(player, "RIGHT", board, gui));
            GridBagConstraints gbc = new GridBagConstraints();
            gbc.gridx = 1; gbc.gridy = 0; controlPanel.add(up, gbc);
            gbc.gridx = 0; gbc.gridy = 1; controlPanel.add(left, gbc);
            gbc.gridx = 2; gbc.gridy = 1; controlPanel.add(right, gbc);
            gbc.gridx = 1; gbc.gridy = 2; controlPanel.add(down, gbc);
            frame.add(controlPanel, BorderLayout.SOUTH);
            JPanel info = new JPanel(new FlowLayout(FlowLayout.LEFT));
            JLabel status = new JLabel(getStatusText(player));
            info.add(status);
            frame.add(info, BorderLayout.NORTH);
            // Update status when GUI repainted
            Timer t = new Timer(200, ev -> {
                status.setText(getStatusText(player));
                gui.repaint();
            });
            t.start();
            frame.setVisible(true);
        });
    }
    private static void doMove(Robo r, String dir, Board board, GUIBoard gui) {
        if (!r.isAlive() || r.hasFoundFood()) return;
        try {
            r.move(dir, board);
        } catch (MovimentoInvalidoException ex) {
            // show a small popup
            JOptionPane.showMessageDialog(gui, "Invalid move: " + ex.getMessage(), "Invalid", JOptionPane.WARNING_MESSAGE);
        }
        gui.repaint();
        if (!r.isAlive()) {
            JOptionPane.showMessageDialog(gui, "Robot exploded! Game over.", "Exploded", JOptionPane.ERROR_MESSAGE);
        } else if (r.hasFoundFood()) {
            JOptionPane.showMessageDialog(gui, "You found the food! Congrats!", "Found Food", JOptionPane.INFORMATION_MESSAGE);
        }
    }
    private static String getStatusText(Robo r) {
        return String.format("Robot: %s | Pos: %s | ValidMoves: %d | InvalidMoves: %d | Alive: %s | FoundFood: %s",
                r.getId(), r.getPosition(), r.getValidMoves(), r.getInvalidMoves(), r.isAlive(), r.hasFoundFood());
    }
}