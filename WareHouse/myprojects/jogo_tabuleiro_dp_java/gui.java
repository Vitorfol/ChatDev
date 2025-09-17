'''
GUI: setup screen and runtime interaction.
Provides:
 - board size selection (10..30)
 - configure each square's type via comboboxes (scrollable)
 - select number of players (2..6), assign colors & types
 - debug mode checkbox
 - Start Game button that initializes Game facade
During play:
 - shows board textual view and player positions
 - status log area
 - roll dice button (or debug destination field + Move button)
 - displays dice sum and messages from Game
'''
/*
GUI: setup screen and runtime interaction.
Provides:
 - board size selection (10..30)
 - configure each square's type via comboboxes (scrollable)
 - select number of players (2..6), assign colors & types
 - debug mode checkbox
 - Start Game button that initializes Game facade
During play:
 - shows board textual view and player positions
 - status log area
 - roll dice button (or debug destination field + Move button)
 - displays dice sum and messages from Game
*/
package app;
import javax.swing.*;
import javax.swing.border.TitledBorder;
import java.awt.*;
import java.awt.event.*;
import java.util.*;
import java.util.List;
public class GUI implements GameListener {
    private JFrame frame;
    private JPanel setupPanel;
    private JPanel playPanel;
    private JComboBox<Integer> sizeCombo;
    private JPanel squaresConfigPanel;
    private JScrollPane squaresScroll;
    private List<JComboBox<SquareType>> squareTypeCombos;
    private JComboBox<Integer> playerCountCombo;
    private JPanel playersPanel;
    private List<JComboBox<String>> playerColorCombos;
    private List<JComboBox<PlayerType>> playerTypeCombos;
    private JCheckBox debugCheck;
    private JButton startButton;
    // play components
    private JTextArea statusArea;
    private JButton rollButton;
    private JTextField debugDestField;
    private JLabel diceLabel;
    private JList<String> boardList;
    private DefaultListModel<String> boardListModel;
    private Game game;
    private static final String[] COLORS = {"Red", "Blue", "Green", "Yellow", "Magenta", "Cyan"};
    public GUI() {
        frame = new JFrame("Multi-player Board Game");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setSize(1000, 700);
        frame.setLayout(new CardLayout());
        buildSetupPanel();
        buildPlayPanel();
        frame.add(setupPanel, "setup");
        frame.add(playPanel, "play");
        frame.setVisible(true);
    }
    private void buildSetupPanel() {
        setupPanel = new JPanel(new BorderLayout());
        JPanel top = new JPanel(new FlowLayout(FlowLayout.LEFT));
        top.setBorder(new TitledBorder("Game Configuration"));
        top.add(new JLabel("Board size:"));
        Integer[] sizes = new Integer[21];
        for (int i = 0; i < sizes.length; i++) sizes[i] = i + 10; // 10..30
        sizeCombo = new JComboBox<>(sizes);
        sizeCombo.setSelectedIndex(5); // default 15
        top.add(sizeCombo);
        JButton configureSquaresBtn = new JButton("Configure Board Squares");
        top.add(configureSquaresBtn);
        top.add(new JLabel("Players:"));
        Integer[] pcounts = new Integer[]{2,3,4,5,6};
        playerCountCombo = new JComboBox<>(pcounts);
        playerCountCombo.setSelectedIndex(0);
        top.add(playerCountCombo);
        top.add(new JLabel("Debug mode:"));
        debugCheck = new JCheckBox();
        top.add(debugCheck);
        startButton = new JButton("Start Game");
        startButton.setEnabled(false); // enabled after configure
        top.add(startButton);
        setupPanel.add(top, BorderLayout.NORTH);
        squaresConfigPanel = new JPanel();
        squaresConfigPanel.setLayout(new BoxLayout(squaresConfigPanel, BoxLayout.Y_AXIS));
        squaresScroll = new JScrollPane(squaresConfigPanel);
        squaresScroll.setPreferredSize(new Dimension(800, 300));
        setupPanel.add(squaresScroll, BorderLayout.CENTER);
        playersPanel = new JPanel();
        playersPanel.setBorder(new TitledBorder("Players"));
        playersPanel.setLayout(new GridBagLayout());
        setupPanel.add(playersPanel, BorderLayout.SOUTH);
        // listeners
        configureSquaresBtn.addActionListener(e -> buildSquaresConfig());
        playerCountCombo.addActionListener(e -> buildPlayersPanel());
        sizeCombo.addActionListener(e -> {}); // can rebuild if desired
        buildSquaresConfig();
        buildPlayersPanel();
        startButton.addActionListener(e -> onStart());
    }
    private void buildSquaresConfig() {
        squaresConfigPanel.removeAll();
        squareTypeCombos = new ArrayList<>();
        int size = (Integer) sizeCombo.getSelectedItem();
        SquareType[] types = SquareType.values();
        for (int i = 0; i < size; i++) {
            JPanel row = new JPanel(new FlowLayout(FlowLayout.LEFT));
            row.add(new JLabel(String.format("Square %d:", i)));
            JComboBox<SquareType> cb = new JComboBox<>(types);
            cb.setSelectedItem(SquareType.SIMPLE);
            row.add(cb);
            squareTypeCombos.add(cb);
            squaresConfigPanel.add(row);
        }
        squaresConfigPanel.revalidate();
        squaresConfigPanel.repaint();
        startButton.setEnabled(true);
    }
    private void buildPlayersPanel() {
        playersPanel.removeAll();
        playerColorCombos = new ArrayList<>();
        playerTypeCombos = new ArrayList<>();
        int pcount = (Integer) playerCountCombo.getSelectedItem();
        GridBagConstraints gbc = new GridBagConstraints();
        gbc.insets = new Insets(3,3,3,3);
        gbc.gridx = 0; gbc.gridy = 0;
        playersPanel.add(new JLabel("Player #"), gbc);
        gbc.gridx = 1;
        playersPanel.add(new JLabel("Color"), gbc);
        gbc.gridx = 2;
        playersPanel.add(new JLabel("Type"), gbc);
        for (int i = 0; i < pcount; i++) {
            gbc.gridy = i+1;
            gbc.gridx = 0;
            playersPanel.add(new JLabel("P" + (i+1)), gbc);
            gbc.gridx = 1;
            JComboBox<String> colorCb = new JComboBox<>(COLORS);
            colorCb.setSelectedIndex(i % COLORS.length);
            playersPanel.add(colorCb, gbc);
            playerColorCombos.add(colorCb);
            gbc.gridx = 2;
            JComboBox<PlayerType> typeCb = new JComboBox<>(PlayerType.values());
            typeCb.setSelectedItem(PlayerType.NORMAL);
            playersPanel.add(typeCb, gbc);
            playerTypeCombos.add(typeCb);
        }
        playersPanel.revalidate();
        playersPanel.repaint();
    }
    private void buildPlayPanel() {
        playPanel = new JPanel(new BorderLayout());
        JPanel left = new JPanel(new BorderLayout());
        left.setBorder(new TitledBorder("Board"));
        boardListModel = new DefaultListModel<>();
        boardList = new JList<>(boardListModel);
        boardList.setFont(new Font(Font.MONOSPACED, Font.PLAIN, 12));
        JScrollPane bscroll = new JScrollPane(boardList);
        left.add(bscroll, BorderLayout.CENTER);
        playPanel.add(left, BorderLayout.CENTER);
        JPanel right = new JPanel();
        right.setLayout(new BoxLayout(right, BoxLayout.Y_AXIS));
        right.setBorder(new TitledBorder("Controls & Status"));
        diceLabel = new JLabel("Dice: -");
        diceLabel.setAlignmentX(Component.LEFT_ALIGNMENT);
        right.add(diceLabel);
        rollButton = new JButton("Roll Dice");
        rollButton.setAlignmentX(Component.LEFT_ALIGNMENT);
        right.add(rollButton);
        JPanel debugPanel = new JPanel(new FlowLayout(FlowLayout.LEFT));
        debugPanel.setAlignmentX(Component.LEFT_ALIGNMENT);
        debugPanel.add(new JLabel("Debug dest (idx):"));
        debugDestField = new JTextField(4);
        debugPanel.add(debugDestField);
        right.add(debugPanel);
        statusArea = new JTextArea(20, 30);
        statusArea.setEditable(false);
        JScrollPane sscroll = new JScrollPane(statusArea);
        sscroll.setAlignmentX(Component.LEFT_ALIGNMENT);
        right.add(sscroll);
        playPanel.add(right, BorderLayout.EAST);
        // roll button action added when game starts
    }
    private void onStart() {
        // validate at least two different player types
        Set<PlayerType> types = new HashSet<>();
        for (JComboBox<PlayerType> cb : playerTypeCombos) {
            types.add((PlayerType) cb.getSelectedItem());
        }
        if (types.size() < 2) {
            JOptionPane.showMessageDialog(frame, "You must choose at least two different player types among players.", "Configuration Error", JOptionPane.ERROR_MESSAGE);
            return;
        }
        int size = (Integer) sizeCombo.getSelectedItem();
        List<SquareType> configured = new ArrayList<>();
        for (JComboBox<SquareType> cb : squareTypeCombos) {
            configured.add((SquareType) cb.getSelectedItem());
        }
        List<Player> players = new ArrayList<>();
        for (int i = 0; i < playerColorCombos.size(); i++) {
            String color = (String) playerColorCombos.get(i).getSelectedItem();
            PlayerType ptype = (PlayerType) playerTypeCombos.get(i).getSelectedItem();
            players.add(new Player("P" + (i+1) + "-" + color, color, ptype));
        }
        boolean debug = debugCheck.isSelected();
        // Create game config via Game facade
        game = new Game();
        game.setListener(this);
        game.setup(configured, players, debug);
        // switch to play panel
        CardLayout cl = (CardLayout) frame.getContentPane().getLayout();
        cl.show(frame.getContentPane(), "play");
        // initialize board list UI
        refreshBoardView();
        // attach roll button action
        // safely remove any existing listeners
        for (ActionListener al : rollButton.getActionListeners()) {
            rollButton.removeActionListener(al);
        }
        rollButton.addActionListener(e -> {
            if (game.isDebugMode()) {
                // if debug mode, read destination index
                String txt = debugDestField.getText().trim();
                if (txt.isEmpty()) {
                    appendStatus("Enter destination square index in debug mode.");
                    return;
                }
                try {
                    int dest = Integer.parseInt(txt);
                    game.debugMoveTo(dest);
                } catch (NumberFormatException ex) {
                    appendStatus("Invalid destination index.");
                }
            } else {
                game.rollAndMove();
            }
            refreshBoardView();
        });
        appendStatus("Game started.");
        updateHeaderDice("-");
    }
    @Override
    public void updateStatus(String message) {
        appendStatus(message);
    }
    @Override
    public void updateBoard() {
        refreshBoardView();
    }
    @Override
    public void updateDice(int d1, int d2) {
        updateHeaderDice(String.format("%d + %d = %d %s", d1, d2, d1+d2, (d1==d2 ? "(Double)" : "")));
    }
    @Override
    public void gameEnded(String summary) {
        appendStatus("GAME ENDED:");
        appendStatus(summary);
        rollButton.setEnabled(false);
        updateHeaderDice("-");
    }
    private void appendStatus(String s) {
        statusArea.append(s + "\n");
        statusArea.setCaretPosition(statusArea.getDocument().getLength());
    }
    private void updateHeaderDice(String s) {
        diceLabel.setText("Dice: " + s);
    }
    private void refreshBoardView() {
        boardListModel.clear();
        Board board = game.getBoard();
        List<Player> players = game.getPlayersSnapshot();
        int size = board.getSize();
        // Build textual lines for each square
        for (int i = 0; i < size; i++) {
            Square sq = board.getSquare(i);
            StringBuilder line = new StringBuilder();
            line.append(String.format("[%2d] %-10s : ", i, sq.getName()));
            // list players on that square
            List<String> tokens = new ArrayList<>();
            for (Player p : players) {
                if (p.getPosition() == i) {
                    tokens.add(p.getName() + "(" + p.getCoins() + "c," + p.getType() + ")");
                }
            }
            line.append(String.join(", ", tokens));
            boardListModel.addElement(line.toString());
        }
        // also add final off-board lines for players past end
        int finalIndex = board.getSize();
        List<String> past = new ArrayList<>();
        for (Player p : players) {
            if (p.getPosition() >= finalIndex) {
                past.add(p.getName() + "(FINISHED at " + p.getPosition() + "," + p.getCoins() + "c," + p.getType() + ")");
            }
        }
        if (!past.isEmpty()) {
            boardListModel.addElement("=== Finished Players ===");
            for (String s : past) boardListModel.addElement(s);
        }
    }
}