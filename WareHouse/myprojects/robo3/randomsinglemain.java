'''
RandomSingleMain: launches a GUI where a single RoboInteligente moves autonomously until it finds food or explodes.
'''
/*
DOCSTRING
RandomSingleMain: launches a GUI where a single RoboInteligente moves autonomously until it finds food or explodes.
*/
import javax.swing.*;
import java.awt.*;
public class RandomSingleMain {
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            Board board = new Board(4);
            board.placeFoodRandom();
            board.placeObstacleRandom(new Bomb(), 1);
            board.placeObstacleRandom(new Rock(), 2);
            RoboInteligente robot = new RoboInteligente("Smart1", board.getRandomEmptyPosition(), Color.MAGENTA);
            board.addRobot(robot);
            JFrame frame = new JFrame("Random Single RoboInteligente");
            frame.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
            frame.setSize(600, 700);
            GUIBoard gui = new GUIBoard(board);
            frame.add(gui, BorderLayout.CENTER);
            JPanel infoPanel = new JPanel(new FlowLayout(FlowLayout.LEFT));
            JLabel status = new JLabel();
            infoPanel.add(status);
            frame.add(infoPanel, BorderLayout.NORTH);
            // Start autonomous thread
            new Thread(() -> {
                while (robot.isAlive() && !robot.hasFoundFood()) {
                    try {
                        robot.decideAndMove(board);
                        SwingUtilities.invokeLater(gui::repaint);
                        SwingUtilities.invokeLater(() -> status.setText(getStatusText(robot)));
                        Thread.sleep(500);
                    } catch (InterruptedException ex) {
                        Thread.currentThread().interrupt();
                        break;
                    } catch (MovimentoInvalidoException ex) {
                        // If decideAndMove exhausts possible moves, it'll throw - break.
                        break;
                    }
                }
                SwingUtilities.invokeLater(() -> {
                    gui.repaint();
                    if (!robot.isAlive()) {
                        JOptionPane.showMessageDialog(gui, "Robot exploded!", "Exploded", JOptionPane.ERROR_MESSAGE);
                    } else if (robot.hasFoundFood()) {
                        JOptionPane.showMessageDialog(gui, "Robot found the food!", "Success", JOptionPane.INFORMATION_MESSAGE);
                    } else {
                        JOptionPane.showMessageDialog(gui, "Robot stopped.", "Stopped", JOptionPane.INFORMATION_MESSAGE);
                    }
                });
            }).start();
            Timer t = new Timer(200, e -> status.setText(getStatusText(robot)));
            t.start();
            frame.setVisible(true);
        });
    }
    private static String getStatusText(Robo r) {
        return String.format("Robot: %s | Pos: %s | ValidMoves: %d | InvalidMoves: %d | Alive: %s | FoundFood: %s",
                r.getId(), r.getPosition(), r.getValidMoves(), r.getInvalidMoves(), r.isAlive(), r.hasFoundFood());
    }
}