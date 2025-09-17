package chatdev.boardgame;
/* '''
Swing GUI for the board game. Presents setup dialogs, displays players and their positions,
lets user roll dice or input debug destination, and shows messages and game progress.
''' */
import javax.swing.*;
import javax.swing.border.EmptyBorder;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.util.ArrayList;
import java.util.List;
/**
 * GUI class uses Swing to provide an interactive board game interface.
 */
public class GameGUI {
    private JFrame frame;
    private JTextArea messageArea;
    private JList<String> playersList;
    private DefaultListModel<String> playersModel;
    private JLabel currentPlayerLabel;
    private JLabel diceLabel;
    private JButton rollButton;
    private JButton endTurnButton;
    private JCheckBox debugCheck;
    private JTextField debugDestinationField;
    private JLabel totalMovesLabel;
    private Game game;
    public GameGUI() {
        initializeGui();
    }
    public void showSetupDialogAndStart() {
        // Setup: ask number of players and their names/types, ensure at least two different types
        int numPlayers = askForNumberOfPlayers();
        if (numPlayers < 2) {
            JOptionPane.showMessageDialog(frame, "At least 2 players required. Exiting.");
            System.exit(0);
        }
        List<Player> players = new ArrayList<>();
        for (int i = 1; i <= numPlayers; i++) {
            Player p = askForPlayerInfo(i);
            if (p == null) {
                JOptionPane.showMessageDialog(frame, "Player creation canceled. Exiting.");
                System.exit(0);
            }
            players.add(p);
        }
        // Validate at least two different types
        boolean hasLucky = false, hasUnlucky = false, hasNormal = false;
        for (Player p : players) {
            if (p instanceof LuckyPlayer) hasLucky = true;
            if (p instanceof UnluckyPlayer) hasUnlucky = true;
            if (p instanceof NormalPlayer) hasNormal = true;
        }
        int distinctTypes = 0;
        if (hasLucky) distinctTypes++;
        if (hasUnlucky) distinctTypes++;
        if (hasNormal) distinctTypes++;
        if (distinctTypes < 2) {
            JOptionPane.showMessageDialog(frame, "You must select at least two different player types. Please restart.");
            showSetupDialogAndStart();
            return;
        }
        this.game = new Game(players);
        refreshPlayersList();
        updateStatusLabels("Game started. " + game.getCurrentPlayer().getName() + " goes first.");
        appendMessage("Game started with " + players.size() + " players.");
        frame.setVisible(true);
    }
    private int askForNumberOfPlayers() {
        while (true) {
            String s = JOptionPane.showInputDialog(frame, "Enter number of players (2-6):", "Players", JOptionPane.QUESTION_MESSAGE);
            if (s == null) return 0;
            try {
                int n = Integer.parseInt(s.trim());
                if (n >= 2 && n <= 6) return n;
            } catch (NumberFormatException ignored) {}
            JOptionPane.showMessageDialog(frame, "Invalid number. Please enter an integer between 2 and 6.");
        }
    }
    private Player askForPlayerInfo(int idx) {
        JPanel panel = new JPanel(new GridLayout(0, 1));
        JTextField nameField = new JTextField("Player" + idx);
        String[] types = {"Normal", "Lucky", "Unlucky"};
        JComboBox<String> typeBox = new JComboBox<>(types);
        panel.add(new JLabel("Player " + idx + " name:"));
        panel.add(nameField);
        panel.add(new JLabel("Type:"));
        panel.add(typeBox);
        int result = JOptionPane.showConfirmDialog(frame, panel, "Enter player " + idx + " info", JOptionPane.OK_CANCEL_OPTION, JOptionPane.PLAIN_MESSAGE);
        if (result != JOptionPane.OK_OPTION) return null;
        String name = nameField.getText().trim();
        if (name.isEmpty()) name = "Player" + idx;
        String type = (String) typeBox.getSelectedItem();
        switch (type) {
            case "Lucky": return new LuckyPlayer(name);
            case "Unlucky": return new UnluckyPlayer(name);
            default: return new NormalPlayer(name);
        }
    }
    private void initializeGui() {
        frame = new JFrame("ChatDev Board Game - 40 Squares");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setSize(800, 600);
        JPanel main = new JPanel(new BorderLayout(10, 10));
        main.setBorder(new EmptyBorder(10, 10, 10, 10));
        // Left panel: players and controls
        JPanel left = new JPanel(new BorderLayout(5,5));
        playersModel = new DefaultListModel<>();
        playersList = new JList<>(playersModel);
        playersList.setFont(new Font(Font.MONOSPACED, Font.PLAIN, 12));
        left.add(new JScrollPane(playersList), BorderLayout.CENTER);
        JPanel controlPanel = new JPanel(new GridLayout(0,1,5,5));
        currentPlayerLabel = new JLabel("Current: -");
        diceLabel = new JLabel("Dice: -");
        totalMovesLabel = new JLabel("Total moves: 0");
        rollButton = new JButton("Roll Dice");
        rollButton.addActionListener((ActionEvent e) -> onRoll());
        endTurnButton = new JButton("End Turn");
        endTurnButton.addActionListener((ActionEvent e) -> onEndTurn());
        debugCheck = new JCheckBox("DEBUG mode (input destination)");
        debugDestinationField = new JTextField();
        debugDestinationField.setEnabled(false);
        debugCheck.addActionListener((e) -> debugDestinationField.setEnabled(debugCheck.isSelected()));
        controlPanel.add(currentPlayerLabel);
        controlPanel.add(diceLabel);
        controlPanel.add(totalMovesLabel);
        controlPanel.add(rollButton);
        controlPanel.add(endTurnButton);
        controlPanel.add(debugCheck);
        controlPanel.add(new JLabel("Destination (0 or greater):"));
        controlPanel.add(debugDestinationField);
        left.add(controlPanel, BorderLayout.SOUTH);
        // Right panel: messages
        messageArea = new JTextArea();
        messageArea.setEditable(false);
        JScrollPane msgScroll = new JScrollPane(messageArea);
        msgScroll.setPreferredSize(new Dimension(450, 400));
        main.add(left, BorderLayout.WEST);
        main.add(msgScroll, BorderLayout.CENTER);
        frame.getContentPane().add(main);
        frame.setLocationRelativeTo(null);
    }
    private void onRoll() {
        if (game == null || game.isFinished()) {
            appendMessage("Game not running or already finished.");
            return;
        }
        boolean debugMode = debugCheck.isSelected();
        Integer dest = null;
        if (debugMode) {
            String txt = debugDestinationField.getText().trim();
            if (txt.isEmpty()) {
                JOptionPane.showMessageDialog(frame, "Please enter a destination square (0 or greater) in debug mode.");
                return;
            }
            try {
                int d = Integer.parseInt(txt);
                if (d < 0) { JOptionPane.showMessageDialog(frame, "Destination must be >= 0."); return; }
                dest = d;
            } catch (NumberFormatException ex) {
                JOptionPane.showMessageDialog(frame, "Invalid destination; enter integer 0 or greater.");
                return;
            }
        }
        List<String> messages = game.performTurn(debugMode, dest);
        // Display messages and set diceLabel appropriately
        String lastRolled = null;
        boolean wasDebug = false;
        for (String m : messages) {
            appendMessage(m);
            if (m.startsWith("Rolled:")) {
                lastRolled = m.substring("Rolled:".length()).trim();
            } else if (m.startsWith("DEBUG mode:")) {
                wasDebug = true;
            }
        }
        // Update dice label
        if (lastRolled != null) {
            diceLabel.setText("Dice: " + lastRolled);
        } else if (wasDebug) {
            diceLabel.setText("Dice: DEBUG");
        } else {
            diceLabel.setText("Dice: -");
        }
        refreshPlayersList();
        updateStatusLabels(null);
        if (game.isFinished()) {
            rollButton.setEnabled(false);
            endTurnButton.setEnabled(false);
            appendMessage("Game finished. Winner: " + game.getWinner().getName());
        }
    }
    private void onEndTurn() {
        if (game == null || game.isFinished()) return;
        // Force advance to next player (useful if user wants to skip bonus)
        game.nextTurnIndex();
        appendMessage("Turn ended by user. Now it's " + game.getCurrentPlayer().getName() + "'s turn.");
        refreshPlayersList();
        updateStatusLabels(null);
        if (game.isFinished()) {
            rollButton.setEnabled(false);
            endTurnButton.setEnabled(false);
            appendMessage("Game finished. Winner: " + game.getWinner().getName());
        }
    }
    private void refreshPlayersList() {
        playersModel.clear();
        if (game == null) return;
        for (Player p : game.getPlayers()) {
            playersModel.addElement(String.format("%s (%s) - Pos: %d %s", p.getName(), p.getClass().getSimpleName(), p.getPosition(), p.isSkipNextTurn() ? "[SkipNext]" : ""));
        }
    }
    private void updateStatusLabels(String overrideMsg) {
        if (game == null) return;
        Player current = game.getCurrentPlayer();
        if (current != null) {
            currentPlayerLabel.setText("Current: " + current.getName() + " (" + current.getPosition() + ")");
        } else {
            currentPlayerLabel.setText("Current: -");
        }
        totalMovesLabel.setText("Total moves: " + game.getTotalMoves());
        if (overrideMsg != null) appendMessage(overrideMsg);
    }
    private void appendMessage(String s) {
        messageArea.append(s + "\n");
        messageArea.setCaretPosition(messageArea.getDocument().getLength());
    }
}