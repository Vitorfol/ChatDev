'''
Main entry point for the board game application.
Starts the Swing GUI.
'''
public class Main {
    public static void main(String[] args) {
        javax.swing.SwingUtilities.invokeLater(() -> {
            GameGUI gui = new GameGUI();
            gui.show();
        });
    }
}