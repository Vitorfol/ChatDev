package chatdev.boardgame;
/* '''
Main entry point for the Board Game application. Starts the GUI.
''' */
import javax.swing.SwingUtilities;
/**
 * Main class to launch the Board Game GUI.
 */
public class Main {
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            GameGUI gui = new GameGUI();
            gui.showSetupDialogAndStart();
        });
    }
}