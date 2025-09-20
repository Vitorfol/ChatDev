'''
Main GUI launcher.
This class provides a Swing GUI to run three scenarios:
- User-controlled single robot
- Random single robot
- Random multiple robots
It uses Board, Robo, RoboInteligente, obstacles and renders a 4x4 grid, logs moves and shows colors.
'''
/* '''
Main GUI launcher.
This class provides a Swing GUI to run three scenarios:
- User-controlled single robot
- Random single robot
- Random multiple robots
It uses Board, Robo, RoboInteligente, obstacles and renders a 4x4 grid, logs moves and shows colors.
''' */
import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.util.ArrayList;
public class MainGUI {
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new SimulatorFrame());
    }
}
class SimulatorFrame extends JFrame {
    private Board board;
    private GridPanel gridPanel;
    private JTextArea logArea;
    private JComboBox<String> modeBox;
    private JSlider delaySlider;
    private JButton startBtn, stepBtn, resetBtn;
    private volatile Thread simThread;
    public SimulatorFrame() {
        super("Robot Simulator - 4x4 Grid");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setSize(700, 600);
        setLayout(new BorderLayout());
        board = new Board(4);
        gridPanel = new GridPanel(board);
        add(gridPanel, BorderLayout.CENTER);
        JPanel control = new JPanel();
        control.setLayout(new FlowLayout());
        modeBox = new JComboBox<>(new String[]{
                "User-Controlled Single Robot",
                "Random Single RoboInteligente",
                "Random Multiple Robots"
        });
        control.add(modeBox);
        startBtn = new JButton("Start");
        stepBtn = new JButton("Step");
        resetBtn = new JButton("Reset");
        control.add(startBtn);
        control.add(stepBtn);
        control.add(resetBtn);
        control.add(new JLabel("Delay (ms):"));
        delaySlider = new JSlider(0, 1000, 300);
        delaySlider.setMajorTickSpacing(250);
        delaySlider.setPaintTicks(true);
        control.add(delaySlider);
        add(control, BorderLayout.NORTH);
        logArea = new JTextArea();
        logArea.setEditable(false);
        JScrollPane sp = new JScrollPane(logArea);
        sp.setPreferredSize(new Dimension(200, 0));
        add(sp, BorderLayout.EAST);
        // initial reset
        resetBoardForMode();
        // listeners
        startBtn.addActionListener(e -> startSimulation());
        stepBtn.addActionListener(e -> stepSimulation());
        resetBtn.addActionListener(e -> resetBoardForMode());
        // keyboard control for user mode
        addKeyListener(new KeyAdapter() {
            @Override
            public void keyPressed(KeyEvent e) {
                if (modeBox.getSelectedIndex() == 0) {
                    Robo r = board.getSingleRobot();
                    if (r == null) return;
                    int dir = -1;
                    if (e.getKeyCode() == KeyEvent.VK_UP) dir = 0;
                    if (e.getKeyCode() == KeyEvent.VK_RIGHT) dir = 1;
                    if (e.getKeyCode() == KeyEvent.VK_DOWN) dir = 2;
                    if (e.getKeyCode() == KeyEvent.VK_LEFT) dir = 3;
                    if (dir != -1) {
                        try {
                            boolean moved = r.move(board, dir);
                            if (moved) log("Valid move by " + r.getName());
                            board.checkGameState();
                        } catch (MovimentoInvalidoException ex) {
                            r.incrementInvalid();
                            log("Invalid move: " + ex.getMessage());
                        }
                        gridPanel.repaint();
                        logStats();
                    }
                }
            }
        });
        // allow frame to receive key events
        setFocusable(true);
        setVisible(true);
        // Request focus so arrow keys work reliably
        SwingUtilities.invokeLater(() -> {
            requestFocusInWindow();
        });
    }
    private void log(String s) {
        SwingUtilities.invokeLater(() -> {
            logArea.append(s + "\n");
            logArea.setCaretPosition(logArea.getDocument().getLength());
        });
    }
    private void resetBoardForMode() {
        stopSimulation();
        board.clear();
        logArea.setText("");
        int mode = modeBox.getSelectedIndex();
        if (mode == 0) {
            // user-controlled single robot: one Robo (blue)
            Robo r = new Robo("UserRobo", new Position(3, 0), Color.BLUE);
            board.addRobot(r);
            log("User-controlled robot placed at (3,0). Use arrow keys to move.");
        } else if (mode == 1) {
            // Random single RoboInteligente (green)
            RoboInteligente r = new RoboInteligente("SmartRobo", new Position(3, 0), Color.GREEN);
            board.addRobot(r);
            log("RoboInteligente placed at (3,0). Simulating random intelligent moves.");
        } else {
            // multiple robots: mix of Robo and RoboInteligente
            Robo r1 = new Robo("Robo1", new Position(3, 0), Color.BLUE);
            RoboInteligente r2 = new RoboInteligente("Smart1", new Position(0, 3), Color.GREEN);
            Robo r3 = new Robo("Robo2", new Position(0, 0), Color.MAGENTA);
            board.addRobot(r1);
            board.addRobot(r2);
            board.addRobot(r3);
            log("Multiple robots placed.");
        }
        // place food and obstacles in a deterministic but interesting layout
        board.clearObstacles();
        board.placeFood(new Position(1, 2));
        board.addObstacle(new Bomb(new Position(1, 1)));
        board.addObstacle(new Rock(new Position(2, 1)));
        board.addObstacle(new Rock(new Position(0, 2)));
        gridPanel.repaint();
        log("Food placed at (1,2). Bomb at (1,1). Rocks at (2,1) and (0,2).");
        logStats();
    }
    private void startSimulation() {
        stopSimulation();
        simThread = new Thread(() -> {
            int delay;
            log("Simulation started.");
            while (!board.isFinished()) {
                delay = delaySlider.getValue();
                int mode = modeBox.getSelectedIndex();
                if (mode == 0) {
                    // user control — nothing to automate
                } else if (mode == 1) {
                    // single RoboInteligente random moves attempts
                    Robo r = board.getSingleRobot();
                    if (r == null || !r.isAlive() || r.foundFood()) break;
                    try {
                        int dir = (int) (Math.random() * 4);
                        boolean moved = r.move(board, dir);
                        if (moved) log(r.getName() + " moved (valid).");
                        else log(r.getName() + " move resulted in no progress.");
                    } catch (MovimentoInvalidoException ex) {
                        r.incrementInvalid();
                        log(r.getName() + " invalid: " + ex.getMessage());
                    }
                } else {
                    // multiple robots random step: each tries a random move
                    // iterate over a snapshot to avoid ConcurrentModification if robots die during moves
                    for (Robo r : new ArrayList<>(board.getRobots())) {
                        if (!r.isAlive() || r.foundFood()) continue;
                        try {
                            int dir = (int) (Math.random() * 4);
                            boolean moved = r.move(board, dir);
                            if (moved) log(r.getName() + " moved (valid).");
                        } catch (MovimentoInvalidoException ex) {
                            r.incrementInvalid();
                            log(r.getName() + " invalid: " + ex.getMessage());
                        }
                    }
                }
                board.checkGameState();
                gridPanel.repaint();
                logStats();
                if (board.isFinished()) break;
                try { Thread.sleep(delay); } catch (InterruptedException ignored) {}
            }
            log("Simulation finished.");
        });
        simThread.start();
    }
    private void stepSimulation() {
        stopSimulation();
        log("Step pressed.");
        int mode = modeBox.getSelectedIndex();
        if (mode == 0) {
            log("User mode: press arrow keys to move the user-controlled robot.");
            return;
        } else if (mode == 1) {
            Robo r = board.getSingleRobot();
            if (r == null || !r.isAlive() || r.foundFood()) return;
            try {
                int dir = (int) (Math.random() * 4);
                boolean moved = r.move(board, dir);
                if (moved) log(r.getName() + " moved (valid).");
                else log(r.getName() + " move resulted in no progress.");
            } catch (MovimentoInvalidoException ex) {
                r.incrementInvalid();
                log(r.getName() + " invalid: " + ex.getMessage());
            }
        } else {
            // iterate over a snapshot to avoid ConcurrentModification
            for (Robo r : new ArrayList<>(board.getRobots())) {
                if (!r.isAlive() || r.foundFood()) continue;
                try {
                    int dir = (int) (Math.random() * 4);
                    boolean moved = r.move(board, dir);
                    if (moved) log(r.getName() + " moved (valid).");
                } catch (MovimentoInvalidoException ex) {
                    r.incrementInvalid();
                    log(r.getName() + " invalid: " + ex.getMessage());
                }
            }
        }
        board.checkGameState();
        gridPanel.repaint();
        logStats();
    }
    private void stopSimulation() {
        if (simThread != null && simThread.isAlive()) {
            simThread.interrupt();
        }
        simThread = null;
    }
    private void logStats() {
        StringBuilder sb = new StringBuilder();
        // iterate over a snapshot to avoid concurrent modification while logging
        for (Robo r : new ArrayList<>(board.getRobots())) {
            sb.append(String.format("%s - Pos:%s Alive:%s Food:%s Valid:%d Invalid:%d\n",
                    r.getName(), r.getPosition(), r.isAlive(), r.foundFood(), r.getValidMoves(), r.getInvalidMoves()));
        }
        log(sb.toString());
    }
}