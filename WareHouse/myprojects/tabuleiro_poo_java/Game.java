package chatdev.boardgame;
/* '''
Game logic manager. Manages players, turns, applying square effects, and winning condition.
''' */
import java.util.ArrayList;
import java.util.List;
import java.util.Random;
/**
 * Game manager responsible for enforcing rules and turn sequence.
 */
public class Game {
    private List<Player> players = new ArrayList<>();
    private int currentIndex = 0;
    private int totalMoves = 0;
    private boolean finished = false;
    private Player winner = null;
    private Random rand = new Random();
    public Game(List<Player> players) {
        this.players = players;
    }
    public List<Player> getPlayers() {
        return players;
    }
    public int getTotalMoves() {
        return totalMoves;
    }
    public boolean isFinished() {
        return finished;
    }
    public Player getWinner() {
        return winner;
    }
    public Player getCurrentPlayer() {
        if (players.isEmpty()) return null;
        return players.get(currentIndex);
    }
    public String getPlayerPositionsString() {
        StringBuilder sb = new StringBuilder();
        for (Player p : players) {
            sb.append(String.format("%s: %d (%s)%n", p.getName(), p.getPosition(), p.getClass().getSimpleName()));
        }
        return sb.toString();
    }
    public void nextTurnIndex() {
        if (players.isEmpty()) return;
        currentIndex = (currentIndex + 1) % players.size();
    }
    /**
     * Perform a player's turn using a dice roll (normal) or debug destination (if debugMode true and debugDestination != null).
     * Returns messages describing what happened.
     *
     * Note: When debugDestination is provided the move is deterministic and no "double" bonus-turn is simulated.
     */
    public List<String> performTurn(boolean debugMode, Integer debugDestination) {
        List<String> messages = new ArrayList<>();
        if (finished) {
            messages.add("Game already finished.");
            return messages;
        }
        Player current = getCurrentPlayer();
        messages.add("It's " + current.getName() + "'s turn (" + current.getClass().getSimpleName() + ").");
        // Handle skip turn
        if (current.isSkipNextTurn()) {
            current.setSkipNextTurn(false);
            totalMoves++;
            current.incrementMovesMade();
            messages.add(current.getName() + " missed this turn (was supposed to skip).");
            // advance turn
            nextTurnIndex();
            return messages;
        }
        if (debugMode && debugDestination != null) {
            int dest = debugDestination;
            // enforce bounds: no negative destinations
            if (dest < 0) dest = 0;
            messages.add("DEBUG mode: moving " + current.getName() + " directly to " + dest + ".");
            current.moveTo(dest);
            current.incrementMovesMade();
            totalMoves++;
            // apply effects on landing
            messages.addAll(applyLandingEffects(current));
            if (current.getPosition() >= Board.WIN_SQUARE) {
                finishGame(current, messages);
                return messages;
            }
            // In debug mode, no extra-turn behavior is implied by the debug input.
            nextTurnIndex();
            return messages;
        } else {
            // Regular roll
            DiceResult r = current.rollDice();
            messages.add("Rolled: " + r.toString());
            current.moveBy(r.sum);
            current.incrementMovesMade();
            totalMoves++;
            messages.add(current.getName() + " moved to " + current.getPosition() + ".");
            // apply landing effects (including possible extra move)
            messages.addAll(applyLandingEffects(current));
            if (current.getPosition() >= Board.WIN_SQUARE) {
                finishGame(current, messages);
                return messages;
            }
            boolean extraTurn = r.isDouble;
            if (extraTurn) {
                messages.add(current.getName() + " rolled a double and gets a bonus turn!");
                // do not advance currentIndex; same player will play again
                return messages;
            } else {
                // normal advance
                nextTurnIndex();
                return messages;
            }
        }
    }
    private void finishGame(Player player, List<String> messages) {
        finished = true;
        winner = player;
        messages.add("WINNER: " + player.getName() + " reached " + player.getPosition());
        messages.add("Total moves: " + totalMoves);
        messages.add("Final positions:");
        for (Player p : players) {
            messages.add(String.format("%s (%s): %d", p.getName(), p.getClass().getSimpleName(), p.getPosition()));
        }
    }
    /**
     * Apply effects that happen when a player lands on a square.
     * May produce multiple messages. This mutates players' positions/flags as required.
     */
    private List<String> applyLandingEffects(Player current) {
        List<String> messages = new ArrayList<>();
        // We allow chain effects (e.g., forward 3 landing on another special) by looping until no new move occurs in this sequence.
        while (true) {
            int pos = current.getPosition();
            if (Board.isMissTurn(pos)) {
                current.setSkipNextTurn(true);
                messages.add(current.getName() + " landed on " + pos + " and will miss their next turn.");
                break;
            } else if (Board.isSurpriseCard(pos)) {
                messages.add(current.getName() + " landed on Surprise card (13). Changing type...");
                Player newPlayer = randomizePlayerTypeKeepingState(current);
                // replace in list
                int idx = players.indexOf(current);
                players.set(idx, newPlayer);
                current = newPlayer;
                messages.add("Now " + current.getName() + " is " + current.getClass().getSimpleName() + ".");
                // stop after type change per specification
                break;
            } else if (Board.isForward3(pos)) {
                if (current instanceof UnluckyPlayer) {
                    messages.add(current.getName() + " landed on " + pos + " which would move forward 3, but they are Unlucky and do not move.");
                    break;
                } else {
                    current.moveBy(3);
                    messages.add(current.getName() + " landed on " + pos + " and moves forward 3 to " + current.getPosition() + ".");
                    // continue loop to apply effects at the new position
                    continue;
                }
            } else if (Board.isSendOpponentHome(pos)) {
                // find opponent to send home: choose the opponent with highest position (furthest ahead)
                Player target = findOpponentFurthestAhead(current);
                if (target != null) {
                    target.moveTo(0);
                    messages.add(current.getName() + " landed on " + pos + " and sends " + target.getName() + " back to start!");
                } else {
                    messages.add(current.getName() + " landed on " + pos + " but there are no opponents to send home.");
                }
                break;
            } else if (Board.isSwapWithLast(pos)) {
                Player last = findOpponentFurthestBehind(current);
                if (last != null) {
                    int temp = last.getPosition();
                    last.moveTo(current.getPosition());
                    current.moveTo(temp);
                    messages.add(current.getName() + " landed on " + pos + " and swaps place with " + last.getName() + " who was furthest behind.");
                } else {
                    messages.add(current.getName() + " landed on " + pos + " but no opponent to swap with.");
                }
                break;
            } else {
                // No special square
                break;
            }
        }
        return messages;
    }
    private Player findOpponentFurthestAhead(Player current) {
        Player best = null;
        int bestPos = Integer.MIN_VALUE;
        for (Player p : players) {
            if (p == current) continue;
            if (p.getPosition() > bestPos) {
                best = p;
                bestPos = p.getPosition();
            }
        }
        return best;
    }
    private Player findOpponentFurthestBehind(Player current) {
        Player best = null;
        int bestPos = Integer.MAX_VALUE;
        for (Player p : players) {
            if (p == current) continue;
            if (p.getPosition() < bestPos) {
                best = p;
                bestPos = p.getPosition();
            }
        }
        return best;
    }
    private Player randomizePlayerTypeKeepingState(Player old) {
        // randomly pick a type (Normal, Lucky, Unlucky)
        int pick = rand.nextInt(3); // 0 Normal, 1 Lucky, 2 Unlucky
        Player newP;
        if (pick == 0) {
            newP = new NormalPlayer(old.getName());
        } else if (pick == 1) {
            newP = new LuckyPlayer(old.getName());
        } else {
            newP = new UnluckyPlayer(old.getName());
        }
        // copy state
        newP.moveTo(old.getPosition());
        newP.setSkipNextTurn(old.isSkipNextTurn());
        // copy movesMade
        while (newP.getMovesMade() < old.getMovesMade()) newP.incrementMovesMade();
        return newP;
    }
    /**
     * For UI convenience: find index of a given player object (by name) and set currentIndex to that player.
     */
    public void setCurrentIndexToPlayerName(String name) {
        for (int i = 0; i < players.size(); i++) {
            if (players.get(i).getName().equals(name)) {
                currentIndex = i;
                return;
            }
        }
    }
}