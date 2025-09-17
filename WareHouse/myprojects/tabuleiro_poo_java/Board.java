package chatdev.boardgame;
/* '''
Board constants and helpers (special squares and utility methods).
''' */
import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;
/**
 * Board definition and utilities.
 */
public class Board {
    public static final int WIN_SQUARE = 40;
    public static final Set<Integer> MISS_TURN = new HashSet<>(Arrays.asList(10, 25, 38));
    public static final int SURPRISE_CARD = 13;
    public static final Set<Integer> FORWARD_3 = new HashSet<>(Arrays.asList(5, 15, 30));
    public static final Set<Integer> SEND_OPPONENT_HOME = new HashSet<>(Arrays.asList(17, 27));
    public static final Set<Integer> SWAP_WITH_LAST = new HashSet<>(Arrays.asList(20, 35));
    public static boolean isMissTurn(int pos) {
        return MISS_TURN.contains(pos);
    }
    public static boolean isSurpriseCard(int pos) {
        return pos == SURPRISE_CARD;
    }
    public static boolean isForward3(int pos) {
        return FORWARD_3.contains(pos);
    }
    public static boolean isSendOpponentHome(int pos) {
        return SEND_OPPONENT_HOME.contains(pos);
    }
    public static boolean isSwapWithLast(int pos) {
        return SWAP_WITH_LAST.contains(pos);
    }
}