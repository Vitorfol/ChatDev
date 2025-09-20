'''
RandomMultipleMain: launches a GUI with multiple robots (RoboInteligente) moving concurrently on the same board.
Robots move in separate threads until each finds food or explodes. The simulation stops when food is found or all robots stopped.
'''
/*
DOCSTRING
RandomMultipleMain: launches a GUI with multiple robots (RoboInteligente) moving concurrently on the same board.
Robots move in separate threads until each finds food or explodes. The simulation stops when food is found or all robots stopped.
*/
import javax.swing.*;
import java.awt.*;
import java.util.ArrayList;
import java.util.List;
public class RandomMultipleMain {
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            Board board = new Board(4);
            board.placeFoodRandom();
            board.placeObstacleRandom(new Bomb(), 1);
            board.placeObstacleRandom(new Rock(), 2);
            int robotCount = 3;
            List<RoboInteligente> robots = new ArrayList<>();
            Color[] colors = {Color.RED, Color.GREEN, Color.BLUE};
            for (int i = 0; i < robotCount; i++) {
                RoboInteligente r = new RoboInteligente("R" + (i + 1), board.getRandomEmptyPosition(), colors[i % colors.length]);
                robots.add(r);
                board.addRobot(r);
            }
            JFrame frame = new JFrame("Random Multiple Robots");
            frame.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
            frame.setSize(600, 700);
            GUIBoard gui = new GUIBoard(board);
            frame.add(gui, BorderLayout.CENTER);
            JPanel infoPanel = new JPanel(new GridLayout(robotCount + 1, 1));
            JLabel header = new JLabel("Robots status:");
            infoPanel.add(header);
            JLabel[] statusLabels = new JLabel[robotCount];
            for (int i = 0; i < robotCount; i++) {
                statusLabels[i] = new JLabel();
                infoPanel.add(statusLabels[i]);
            }
            frame.add(infoPanel, BorderLayout.NORTH);
            frame.setVisible(true);
            // Start threads for each robot
            for (int i = 0; i < robotCount; i++) {
                final int idx = i;
                RoboInteligente r = robots.get(i);
                new Thread(() -> {
                    while (r.isAlive() && !r.hasFoundFood()) {
                        try {
                            r.decideAndMove(board);
                            SwingUtilities.invokeLater(gui::repaint);
                            Thread.sleep(500 + (int)(Math.random() * 300));
                        } catch (InterruptedException ex) {
                            Thread.currentThread().interrupt();
                            break;
                        } catch (MovimentoInvalidoException ex) {
                            // no possible moves left for this robot
                            break;
                        }
                    }
                }).start();
            }
            // Update statuses periodically and detect termination
            new Timer(300, e -> {
                boolean anyFound = false;
                boolean anyAlive = false;
                for (int i = 0; i < robotCount; i++) {
                    Robo r = robots.get(i);
                    statusLabels[i].setText(String.format("%s | Pos:%s | Valid:%d Invalid:%d | Alive:%s | Found:%s",
                            r.getId(), r.getPosition(), r.getValidMoves(), r.getInvalidMoves(), r.isAlive(), r.hasFoundFood()));
                    if (r.hasFoundFood()) anyFound = true;
                    if (r.isAlive()) anyAlive = true;
                }
                gui.repaint();
                if (anyFound) {
                    JOptionPane.showMessageDialog(gui, "A robot found the food! Simulation ends.", "Food Found", JOptionPane.INFORMATION_MESSAGE);
                    ((Timer)e.getSource()).stop();
                } else if (!anyAlive) {
                    JOptionPane.showMessageDialog(gui, "All robots dead/stopped. Simulation ends.", "End", JOptionPane.INFORMATION_MESSAGE);
                    ((Timer)e.getSource()).stop();
                }
            }).start();
        });
    }
}