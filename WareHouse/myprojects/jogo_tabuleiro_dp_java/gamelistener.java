'''
GameListener: interface for GUI to implement so Game can push updates.
'''
/*
GameListener: interface for GUI to implement so Game can push updates.
*/
package app;
public interface GameListener {
    void updateStatus(String message);
    void updateBoard();
    void updateDice(int d1, int d2);
    void gameEnded(String summary);
}