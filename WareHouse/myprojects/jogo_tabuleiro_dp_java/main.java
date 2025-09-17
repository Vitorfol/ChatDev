'''
Main entry point for the board game application.
'''
/*
Main entry point for the board game application.
*/
package app;
import javax.swing.SwingUtilities;
public class Main {
    /*
    Starts the Swing GUI on the Event Dispatch Thread.
    */
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            new GUI();
        });
    }
}