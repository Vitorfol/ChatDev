'''
Facade Game class: holds board and players, coordinates turns, applies square effects,
exposes methods that GUI can call to play a turn (roll or debug).
'''
import java.util.*;
import java.util.function.Consumer;
public class Game {
    private Board board;
    private List<Player> players;
    private int currentPlayerIndex = 0;
    private boolean debugMode;
    private Consumer<String> logger;
    private Runnable uiUpdater;
    private boolean finished = false;
    private Player winner = null;
    private int totalMoves = 0;
    public Game(List<Player> players, Board board, boolean debugMode, Consumer<String> logger, Runnable uiUpdater) {
        this.players = players;
        this.board = board;
        this.debugMode = debugMode;
        this.logger = logger;
        this.uiUpdater = uiUpdater;
        // ensure initial positions are 0 and coins 0
        for (Player p : players) {
            p.setPosition(0);
            p.setCoins(0);
            p.setSkipNextTurn(false);
            p.setFinished(false);
        }
        logger.accept("Game initialized.");
    }
    // Getters used by GUI
    public List<Player> getPlayers() { return players; }
    public boolean isDebugMode() { return debugMode; }
    public boolean isFinished() { return finished; }
    public Player getWinner() { return winner; }
    public int getTotalMoves() { return totalMoves; }
    public Player getCurrentPlayer() { return players.get(currentPlayerIndex); }
    // Called by GUI to play a normal roll-based turn
    public void playTurnRoll() {
        if (finished) return;
        Player p = players.get(currentPlayerIndex);
        if (p.isFinished()) {
            advanceToNext();
            uiUpdater.run();
            return;
        }
        if (p.isSkipNextTurn()) {
            logger.accept(p.getName() + " skips this turn (was in prison).");
            p.setSkipNextTurn(false);
            advanceToNext();
            uiUpdater.run();
            return;
        }
        Random r = new Random();
        int d1 = r.nextInt(6) + 1;
        int d2 = r.nextInt(6) + 1;
        int sum = d1 + d2;
        logger.accept(p.getName() + " rolled " + d1 + " and " + d2 + " (sum = " + sum + ")");
        totalMoves++;
        int oldPos = p.getPosition();
        int newPos = oldPos + sum;
        logger.accept(p.getName() + " moves from " + oldPos + " to " + newPos);
        p.setPosition(newPos);
        // Check win
        if (newPos >= board.getSize()) {
            p.setFinished(true);
            finished = true;
            winner = p;
            logger.accept(p.getName() + " reached/passed final square and wins!");
            uiUpdater.run();
            return;
        }
        // Apply square effect
        Square sq = board.getSquareAt(p.getPosition());
        if (sq != null) {
            logger.accept(p.getName() + " landed on square " + sq.getIndex() + " (" + sq.getName() + ").");
            sq.applyEffect(this, p, sum, logger);
        } else {
            // position 0 (start) or invalid
            logger.accept(p.getName() + " is at start or on an empty cell.");
        }
        // After effects, check if someone reached or passed final
        if (p.getPosition() >= board.getSize()) {
            p.setFinished(true);
            finished = true;
            winner = p;
            logger.accept(p.getName() + " reached/passed final square and wins!");
            uiUpdater.run();
            return;
        }
        // Double roll grants an extra turn
        boolean gotExtraTurn = d1 == d2;
        if (gotExtraTurn) {
            logger.accept(p.getName() + " rolled a double and gets a bonus turn!");
        }
        // If square granted a PlayAgain effect, it should have set a flag or moved p; implementation uses logger messages and may adjust position
        // For extra turn behavior: if gotExtraTurn or player was granted extra turn by square, do NOT advance currentPlayerIndex.
        // We'll rely on a temporary marker on player for an extra-turn that squares can set: playAgainCount (implemented via attributes? To keep things simple, PlayAgainSquare will call this method to grant immediate extra turn by not advancing currentPlayerIndex.)
        // Implementation approach: PlayAgainSquare will call grantExtraTurnOnCurrent() if it needs to.
        // Decide whether to advance to next player
        if (!gotExtraTurn && !p.isHasExtraTurn()) {
            advanceToNext();
        } else {
            // consume extra-turn flag if set by square (persist until used)
            if (p.isHasExtraTurn()) {
                logger.accept(p.getName() + " uses an extra turn from square effect.");
                p.setHasExtraTurn(false); // consume
            }
            // currentPlayerIndex remains same
        }
        uiUpdater.run();
    }
    // Called by GUI to play a debug-based turn: user directly inputs destination index (1..boardSize or 0)
    public void playTurnDebug(int destination) {
        if (finished) return;
        Player p = players.get(currentPlayerIndex);
        if (p.isFinished()) {
            advanceToNext();
            uiUpdater.run();
            return;
        }
        if (p.isSkipNextTurn()) {
            logger.accept(p.getName() + " skips this turn (was in prison).");
            p.setSkipNextTurn(false);
            advanceToNext();
            uiUpdater.run();
            return;
        }
        // destination is absolute square index (0..board.getSize())
        if (destination < 0) destination = 0;
        // destination could be greater than board size meaning win
        logger.accept(p.getName() + " (DEBUG) moves to " + destination);
        totalMoves++;
        p.setPosition(destination);
        // No dice sum in debug mode, so treat diceSum as 0 when applying Surprise; respond accordingly.
        int dummySum = 0;
        if (p.getPosition() >= board.getSize()) {
            p.setFinished(true);
            finished = true;
            winner = p;
            logger.accept(p.getName() + " reached/passed final square and wins (DEBUG)!");
            uiUpdater.run();
            return;
        }
        Square sq = board.getSquareAt(p.getPosition());
        if (sq != null) {
            logger.accept(p.getName() + " landed on square " + sq.getIndex() + " (" + sq.getName() + ").");
            sq.applyEffect(this, p, dummySum, logger);
        } else {
            logger.accept(p.getName() + " is at start or on an empty cell.");
        }
        if (p.getPosition() >= board.getSize()) {
            p.setFinished(true);
            finished = true;
            winner = p;
            logger.accept(p.getName() + " reached/passed final square and wins (DEBUG)!");
            uiUpdater.run();
            return;
        }
        // After debug move we always advance to next player unless player has extra-turn flag
        if (!p.isHasExtraTurn()) {
            advanceToNext();
        } else {
            logger.accept(p.getName() + " uses an extra turn from square effect.");
            p.setHasExtraTurn(false);
        }
        uiUpdater.run();
    }
    // Advance currentPlayerIndex to next non-finished player
    private void advanceToNext() {
        int attempts = 0;
        do {
            currentPlayerIndex = (currentPlayerIndex + 1) % players.size();
            attempts++;
            if (attempts > players.size()+5) break;
        } while (players.get(currentPlayerIndex).isFinished());
    }
    // Utility methods available to squares to interact with game
    public Board getBoard() { return board; }
    // grant an immediate extra turn to current player (used by PlayAgainSquare)
    public void grantExtraTurnTo(Player p) {
        // set a flag on player that indicates they can take an immediate extra turn (consumed when used)
        p.setHasExtraTurn(true);
        logger.accept(p.getName() + " gains an extra turn from square effect.");
    }
    // swap positions between two players
    public void swapPositions(Player a, Player b) {
        int ta = a.getPosition();
        int tb = b.getPosition();
        a.setPosition(tb);
        b.setPosition(ta);
        logger.accept("Swapped positions: " + a.getName() + " <-> " + b.getName());
    }
    // find player who is currently last on board (smallest position)
    public Player findLastOnBoard() {
        Player last = null;
        for (Player p : players) {
            if (last == null || p.getPosition() < last.getPosition()) {
                last = p;
            }
        }
        return last;
    }
    // Determine roll-derived type from dice sum (used by Surprise square and as helper)
    // According to spec: dice sum >= 7 -> LUCKY, <=6 -> UNLUCKY, else NORMAL
    public static PlayerType getTypeFromDiceSum(int diceSum) {
        if (diceSum >= 7) return PlayerType.LUCKY;
        if (diceSum <= 6) return PlayerType.UNLUCKY;
        return PlayerType.NORMAL;
    }
}