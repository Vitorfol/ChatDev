'''
Game facade: setup, turn logic, applying square effects, debug mode handling.
Uses SquareFactory to build board squares.
Notifies GameListener (GUI) about updates.
Provides helper methods that Square classes can call to notify UI or enforce extra turns.
'''
/*
Game facade: setup, turn logic, applying square effects, debug mode handling.
Uses SquareFactory to build board squares.
Notifies GameListener (GUI) about updates.
Provides helper methods that Square classes can call to notify UI or enforce extra turns.
*/
package app;
import java.util.*;
import java.util.concurrent.ThreadLocalRandom;
public class Game {
    private Board board;
    private List<Player> players;
    private int currentPlayerIndex;
    private int totalMoves;
    private boolean debugMode;
    private GameListener listener;
    private Dice dice;
    private boolean extraTurnFlagForCurrent = false;
    public Game() {
        dice = new Dice();
    }
    public void setListener(GameListener l) {
        this.listener = l;
    }
    public void setup(List<SquareType> configuredSquares, List<Player> playersConfig, boolean debugMode) {
        List<Square> squares = new ArrayList<>();
        for (SquareType st : configuredSquares) {
            squares.add(SquareFactory.createSquare(st));
        }
        this.board = new Board(squares);
        this.players = new ArrayList<>();
        for (Player p : playersConfig) {
            Player cp = new Player(p.getName(), p.getColor(), p.getType());
            this.players.add(cp);
        }
        this.debugMode = debugMode;
        this.currentPlayerIndex = 0;
        this.totalMoves = 0;
    }
    public Board getBoard() { return board; }
    public List<Player> getPlayersSnapshot() {
        List<Player> snap = new ArrayList<>();
        for (Player p : players) snap.add(p.copy());
        return snap;
    }
    public boolean isDebugMode() { return debugMode; }
    // Expose a safe copy of listener for squares to use
    public GameListener getListenerProxy() {
        return listener;
    }
    // helper to allow Square classes to set an extra-turn for current
    public void forceExtraTurnForCurrent() {
        extraTurnFlagForCurrent = true;
    }
    // roll mode
    public void rollAndMove() {
        if (isGameOver()) return;
        Player p = getCurrentPlayer();
        if (p.isSkipNextTurn()) {
            p.setSkipNextTurn(false);
            if (listener != null) listener.updateStatus(p.getName() + " was in prison and skips this turn.");
            advanceTurn();
            return;
        }
        int d1 = dice.rollDie();
        int d2 = dice.rollDie();
        if (listener != null) listener.updateDice(d1, d2);
        int sum = d1 + d2;
        movePlayerBySteps(currentPlayerIndex, sum);
        totalMoves++;
        boolean doubleRoll = (d1 == d2);
        if (extraTurnFlagForCurrent) {
            // PlayAgain square granted extra turn
            extraTurnFlagForCurrent = false;
            if (listener != null) listener.updateStatus(getCurrentPlayer().getName() + " was granted an extra turn!");
            // do not advance currentPlayerIndex
            return;
        }
        if (doubleRoll) {
            if (listener != null) listener.updateStatus(getCurrentPlayer().getName() + " rolled a double and gets a bonus turn!");
            return;
        }
        advanceTurn();
    }
    public void debugMoveTo(int destIndex) {
        if (!debugMode) {
            if (listener != null) listener.updateStatus("Not in debug mode.");
            return;
        }
        if (isGameOver()) return;
        Player p = getCurrentPlayer();
        if (p.isSkipNextTurn()) {
            p.setSkipNextTurn(false);
            if (listener != null) listener.updateStatus(p.getName() + " was in prison and skips this turn.");
            advanceTurn();
            return;
        }
        if (destIndex < 0) destIndex = 0;
        p.setPosition(destIndex);
        if (listener != null) listener.updateStatus(p.getName() + " debug-moved to " + destIndex);
        applySquareEffectForPlayerIndex(currentPlayerIndex);
        totalMoves++;
        if (!extraTurnFlagForCurrent) {
            advanceTurn();
        } else {
            extraTurnFlagForCurrent = false;
            if (listener != null) listener.updateStatus(getCurrentPlayer().getName() + " was granted an extra turn!");
        }
    }
    private void movePlayerBySteps(int playerIndex, int steps) {
        Player p = players.get(playerIndex);
        int newPos = p.getPosition() + steps;
        p.setPosition(newPos);
        if (listener != null) listener.updateStatus(p.getName() + " moves to " + newPos + " (+" + steps + ")");
        applySquareEffectForPlayerIndex(playerIndex);
    }
    private void applySquareEffectForPlayerIndex(int playerIndex) {
        if (isGameOver()) return;
        Player p = players.get(playerIndex);
        int pos = p.getPosition();
        if (pos >= board.getSize()) {
            if (listener != null) listener.updateStatus(p.getName() + " has reached or passed the final square and wins!");
            endGameWithWinner(p);
            return;
        }
        Square sq = board.getSquare(pos);
        if (!(sq instanceof SimpleSquare)) {
            if (listener != null) listener.updateStatus(p.getName() + " landed on " + sq.getName());
        } else {
            // Simple square coin
            p.addCoins(1);
            if (listener != null) listener.updateStatus(p.getName() + " gets 1 coin (now " + p.getCoins() + ").");
        }
        sq.onLand(p, this);
        if (listener != null) listener.updateBoard();
        if (p.getPosition() >= board.getSize()) {
            endGameWithWinner(p);
        }
    }
    private void endGameWithWinner(Player winner) {
        StringBuilder sb = new StringBuilder();
        sb.append("Winner: ").append(winner.getName()).append("\n");
        sb.append("Total moves: ").append(totalMoves).append("\n");
        sb.append("Final positions:\n");
        for (Player pl : players) {
            sb.append(String.format(" - %s : pos=%d, coins=%d, type=%s\n", pl.getName(), pl.getPosition(), pl.getCoins(), pl.getType()));
        }
        if (listener != null) listener.gameEnded(sb.toString());
    }
    public void advanceTurn() {
        if (isGameOver()) return;
        currentPlayerIndex = (currentPlayerIndex + 1) % players.size();
        int tries = 0;
        while (players.get(currentPlayerIndex).getPosition() >= board.getSize() && tries < players.size()) {
            currentPlayerIndex = (currentPlayerIndex + 1) % players.size();
            tries++;
        }
    }
    public boolean isGameOver() {
        for (Player p : players) {
            if (p.getPosition() >= board.getSize()) return true;
        }
        return false;
    }
    public Player getCurrentPlayer() {
        return players.get(currentPlayerIndex);
    }
    public List<Player> getPlayers() {
        return players;
    }
    public Player findLastPlacePlayer() {
        Player last = null;
        for (Player pl : players) {
            if (last == null || pl.getPosition() < last.getPosition()) last = pl;
        }
        return last;
    }
    public int getTotalMoves() { return totalMoves; }
}