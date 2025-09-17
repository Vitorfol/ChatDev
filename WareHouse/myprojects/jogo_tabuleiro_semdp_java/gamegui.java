'''
Swing GUI: setup panel for players and board and the main gameplay panel.
Interacts with Game facade to set up and step through turns.
'''
import javax.swing.*;
import javax.swing.border.EmptyBorder;
import java.awt.*;
import java.awt.event.*;
import java.util.*;
import java.util.List;
public class GameGUI {
    private JFrame frame;
    private JPanel setupPanel;
    private JPanel gamePanel;
    private JTextArea logArea;
    private JLabel statusLabel;
    private JLabel positionsLabel;
    private JButton rollButton;
    private JButton nextButton;
    private JTextField debugDestField;
    private JCheckBox debugModeCheck;
    private Game game;
    // Setup components
    private JComboBox<Integer> playerCountBox;
    private java.util.List<JTextField> nameFields = new ArrayList<>();
    private java.util.List<JComboBox<String>> colorBoxes = new ArrayList<>();
    private java.util.List<JComboBox<String>> typeBoxes = new ArrayList<>();
    private JTextField boardSizeField;
    private JPanel squareConfigPanel;
    private java.util.List<JComboBox<String>> squareTypeCombos = new ArrayList<>();
    private JButton randomizeBoardButton;
    // Colors map
    private static final String[] colorNames = {"Red","Blue","Green","Yellow","Magenta","Cyan","Black","Orange"};
    private static final java.util.Map<String, Color> namedColors = new HashMap<>();
    static {
        namedColors.put("Red", Color.RED);
        namedColors.put("Blue", Color.BLUE);
        namedColors.put("Green", Color.GREEN);
        namedColors.put("Yellow", Color.YELLOW);
        namedColors.put("Magenta", Color.MAGENTA);
        namedColors.put("Cyan", Color.CYAN);
        namedColors.put("Black", Color.BLACK);
        namedColors.put("Orange", Color.ORANGE);
    }
    private static final String[] squareTypes = {
            "Simple",
            "Surprise",
            "Prison",
            "Lucky",
            "Unlucky",
            "Reverse",
            "PlayAgain"
    };
    public GameGUI() {
        frame = new JFrame("ChatDev Board Game");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setSize(900, 700);
        frame.setLocationRelativeTo(null);
        frame.setLayout(new BorderLayout());
        buildSetupPanel();
        buildGamePanel();
        frame.add(setupPanel, BorderLayout.CENTER);
    }
    public void show() {
        frame.setVisible(true);
    }
    private void buildSetupPanel() {
        setupPanel = new JPanel(new BorderLayout(10,10));
        setupPanel.setBorder(new EmptyBorder(10,10,10,10));
        JPanel topPanel = new JPanel(new FlowLayout(FlowLayout.LEFT));
        topPanel.add(new JLabel("Players (2-6):"));
        playerCountBox = new JComboBox<>();
        for (int i=2;i<=6;i++) playerCountBox.addItem(i);
        playerCountBox.setSelectedItem(2);
        topPanel.add(playerCountBox);
        topPanel.add(new JLabel("Board size (10-50):"));
        boardSizeField = new JTextField("20",4);
        topPanel.add(boardSizeField);
        setupPanel.add(topPanel, BorderLayout.NORTH);
        JPanel center = new JPanel(new BorderLayout(5,5));
        JPanel playersPanel = new JPanel();
        playersPanel.setLayout(new GridLayout(6,1,5,5));
        playersPanel.setBorder(BorderFactory.createTitledBorder("Players (configure up to 6)"));
        for (int i=0;i<6;i++) {
            JPanel p = new JPanel(new FlowLayout(FlowLayout.LEFT));
            p.add(new JLabel("P"+(i+1)+" Name:"));
            JTextField nameField = new JTextField("Player"+(i+1),8);
            nameFields.add(nameField);
            p.add(nameField);
            p.add(new JLabel("Color:"));
            JComboBox<String> colorBox = new JComboBox<>(colorNames);
            colorBox.setSelectedIndex(i % colorNames.length);
            colorBoxes.add(colorBox);
            p.add(colorBox);
            p.add(new JLabel("Type:"));
            JComboBox<String> typeBox = new JComboBox<>(new String[]{"Normal","Lucky","Unlucky"});
            if (i==0) typeBox.setSelectedItem("Normal");
            typeBoxes.add(typeBox);
            p.add(typeBox);
            playersPanel.add(p);
        }
        center.add(playersPanel, BorderLayout.NORTH);
        squareConfigPanel = new JPanel();
        squareConfigPanel.setLayout(new BoxLayout(squareConfigPanel, BoxLayout.Y_AXIS));
        squareConfigPanel.setBorder(BorderFactory.createTitledBorder("Board squares configuration"));
        randomizeBoardButton = new JButton("Generate Square Config");
        randomizeBoardButton.addActionListener(e -> regenerateSquareConfig());
        center.add(randomizeBoardButton, BorderLayout.SOUTH);
        center.add(new JScrollPane(squareConfigPanel), BorderLayout.CENTER);
        setupPanel.add(center, BorderLayout.CENTER);
        JPanel bottom = new JPanel(new FlowLayout(FlowLayout.RIGHT));
        debugModeCheck = new JCheckBox("Debug mode (allow manual destination)");
        bottom.add(debugModeCheck);
        JButton startButton = new JButton("Start Game");
        startButton.addActionListener(e -> onStart());
        bottom.add(startButton);
        setupPanel.add(bottom, BorderLayout.SOUTH);
        // regenerate default square config
        regenerateSquareConfig();
        playerCountBox.addActionListener(e -> updatePlayerDisplay());
    }
    private void updatePlayerDisplay() {
        int cnt = (int)playerCountBox.getSelectedItem();
        for (int i=0;i<6;i++) {
            boolean enabled = i < cnt;
            nameFields.get(i).setEnabled(enabled);
            colorBoxes.get(i).setEnabled(enabled);
            typeBoxes.get(i).setEnabled(enabled);
        }
    }
    private void regenerateSquareConfig() {
        squareConfigPanel.removeAll();
        squareTypeCombos.clear();
        int boardSize = 20;
        try {
            boardSize = Integer.parseInt(boardSizeField.getText().trim());
            if (boardSize < 10) boardSize = 10;
            if (boardSize > 50) boardSize = 50;
        } catch (NumberFormatException ex) {
            boardSize = 20;
        }
        for (int i=1;i<=boardSize;i++) {
            JPanel p = new JPanel(new FlowLayout(FlowLayout.LEFT));
            p.add(new JLabel("Square "+i+":"));
            JComboBox<String> combo = new JComboBox<>(squareTypes);
            // make first and last simple squares to avoid surprises at very end
            if (i==boardSize) combo.setSelectedItem("Simple");
            else if (i==1) combo.setSelectedItem("Simple");
            else {
                // random selection
                combo.setSelectedIndex((i*31 + 7) % squareTypes.length);
            }
            squareTypeCombos.add(combo);
            p.add(combo);
            squareConfigPanel.add(p);
        }
        squareConfigPanel.revalidate();
        squareConfigPanel.repaint();
    }
    private void buildGamePanel() {
        gamePanel = new JPanel(new BorderLayout(10,10));
        gamePanel.setBorder(new EmptyBorder(10,10,10,10));
        JPanel top = new JPanel(new BorderLayout());
        statusLabel = new JLabel("Status");
        top.add(statusLabel, BorderLayout.NORTH);
        positionsLabel = new JLabel("Positions");
        top.add(positionsLabel, BorderLayout.SOUTH);
        gamePanel.add(top, BorderLayout.NORTH);
        logArea = new JTextArea();
        logArea.setEditable(false);
        JScrollPane scroll = new JScrollPane(logArea);
        gamePanel.add(scroll, BorderLayout.CENTER);
        JPanel controls = new JPanel(new FlowLayout(FlowLayout.LEFT));
        rollButton = new JButton("Roll Dice");
        rollButton.addActionListener(e -> onRollOrDebug());
        controls.add(rollButton);
        controls.add(new JLabel("Debug dest (index):"));
        debugDestField = new JTextField(4);
        controls.add(debugDestField);
        JButton backToSetup = new JButton("Back to Setup");
        backToSetup.addActionListener(e -> backToSetup());
        controls.add(backToSetup);
        gamePanel.add(controls, BorderLayout.SOUTH);
    }
    private void backToSetup() {
        frame.getContentPane().removeAll();
        frame.add(setupPanel, BorderLayout.CENTER);
        frame.revalidate();
        frame.repaint();
        logArea.setText("");
    }
    private void onStart() {
        // read configuration
        int playerCount = (int)playerCountBox.getSelectedItem();
        int boardSize = 20;
        try {
            boardSize = Integer.parseInt(boardSizeField.getText().trim());
            if (boardSize < 5) boardSize = 5;
            if (boardSize > 50) boardSize = 50;
        } catch (NumberFormatException ex) {
            JOptionPane.showMessageDialog(frame, "Invalid board size. Using 20.");
            boardSize = 20;
        }
        List<Player> players = new ArrayList<>();
        Set<String> usedNames = new HashSet<>();
        for (int i=0;i<playerCount;i++) {
            String name = nameFields.get(i).getText().trim();
            if (name.isEmpty()) name = "Player"+(i+1);
            if (usedNames.contains(name)) name = name + "_" + (i+1);
            usedNames.add(name);
            String colorName = (String)colorBoxes.get(i).getSelectedItem();
            Color c = namedColors.getOrDefault(colorName, Color.BLACK);
            String t = (String)typeBoxes.get(i).getSelectedItem();
            PlayerType pt = PlayerType.NORMAL;
            if ("Lucky".equalsIgnoreCase(t)) pt = PlayerType.LUCKY;
            if ("Unlucky".equalsIgnoreCase(t)) pt = PlayerType.UNLUCKY;
            Player p = new Player(name, c, pt);
            players.add(p);
        }
        // enforce at least two different player types present
        boolean hasLucky = players.stream().anyMatch(p -> p.getType()==PlayerType.LUCKY);
        boolean hasUnlucky = players.stream().anyMatch(p -> p.getType()==PlayerType.UNLUCKY);
        boolean hasNormal = players.stream().anyMatch(p -> p.getType()==PlayerType.NORMAL);
        int distinctTypes = 0;
        if (hasLucky) distinctTypes++;
        if (hasUnlucky) distinctTypes++;
        if (hasNormal) distinctTypes++;
        if (distinctTypes < 2) {
            JOptionPane.showMessageDialog(frame, "Game must have at least two different player types. Please adjust player types in setup.");
            return;
        }
        // build board squares
        java.util.List<Square> squares = new ArrayList<>();
        int sz = Math.max(5, Math.min(50, boardSize));
        for (int i=0;i<sz;i++) {
            String selected = "Simple";
            if (i < squareTypeCombos.size()) selected = (String)squareTypeCombos.get(i).getSelectedItem();
            Square s;
            switch (selected) {
                case "Surprise": s = new SurpriseSquare(i+1); break;
                case "Prison": s = new PrisonSquare(i+1); break;
                case "Lucky": s = new LuckySquare(i+1); break;
                case "Unlucky": s = new UnluckySquare(i+1); break;
                case "Reverse": s = new ReverseSquare(i+1); break;
                case "PlayAgain": s = new PlayAgainSquare(i+1); break;
                default: s = new SimpleSquare(i+1); break;
            }
            squares.add(s);
        }
        Board board = new Board(squares);
        boolean debug = debugModeCheck.isSelected();
        // instantiate game
        game = new Game(players, board, debug, this::appendLog, this::updateUIOnStateChange);
        // switch to game panel
        frame.getContentPane().removeAll();
        frame.add(gamePanel, BorderLayout.CENTER);
        frame.revalidate();
        frame.repaint();
        logArea.setText("");
        appendLog("Game started with " + players.size() + " players. Board size: " + board.getSize() + " squares.");
        updateUIOnStateChange();
    }
    private void appendLog(String msg) {
        SwingUtilities.invokeLater(() -> {
            logArea.append(msg + "\n");
            logArea.setCaretPosition(logArea.getDocument().getLength());
        });
    }
    private void updateUIOnStateChange() {
        SwingUtilities.invokeLater(() -> {
            if (game == null) return;
            // show positions
            StringBuilder sb = new StringBuilder("<html>");
            for (Player p : game.getPlayers()) {
                sb.append(String.format("<font color='rgb(%d,%d,%d)'>%s</font>: pos=%d coins=%d type=%s%s<br/>",
                        p.getColor().getRed(), p.getColor().getGreen(), p.getColor().getBlue(),
                        p.getName(), p.getPosition(), p.getCoins(), p.getType().name(),
                        p.isSkipNextTurn() ? " (skip)" : ""));
            }
            sb.append("</html>");
            positionsLabel.setText(sb.toString());
            if (game.isFinished()) {
                Player winner = game.getWinner();
                statusLabel.setText("Game over. Winner: " + (winner != null ? winner.getName() : "none"));
                appendLog("=== GAME OVER ===");
                if (winner != null) appendLog("Winner: " + winner.getName());
                appendLog("Total moves: " + game.getTotalMoves());
                appendLog("Final positions:");
                for (Player p : game.getPlayers()) {
                    appendLog(String.format("%s - pos=%d coins=%d type=%s", p.getName(), p.getPosition(), p.getCoins(), p.getType()));
                }
                rollButton.setEnabled(false);
                return;
            } else {
                Player cur = game.getCurrentPlayer();
                statusLabel.setText("Current turn: " + cur.getName() + " (type=" + cur.getType() + ")");
                rollButton.setEnabled(true);
            }
        });
    }
    private void onRollOrDebug() {
        if (game == null || game.isFinished()) return;
        if (game.isDebugMode()) {
            String s = debugDestField.getText().trim();
            if (s.isEmpty()) {
                JOptionPane.showMessageDialog(frame, "Enter a destination square index in debug mode.");
                return;
            }
            try {
                int dest = Integer.parseInt(s);
                game.playTurnDebug(dest);
            } catch (NumberFormatException ex) {
                JOptionPane.showMessageDialog(frame, "Invalid integer destination.");
                return;
            }
        } else {
            game.playTurnRoll();
        }
    }
}