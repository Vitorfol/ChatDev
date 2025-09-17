package chatdev.boardgame;
/* '''
Simple data container for a dice roll result.
''' */
/**
 * Represents the outcome of two dice.
 */
public class DiceResult {
    public final int die1;
    public final int die2;
    public final int sum;
    public final boolean isDouble;
    public DiceResult(int d1, int d2) {
        this.die1 = d1;
        this.die2 = d2;
        this.sum = d1 + d2;
        this.isDouble = (d1 == d2);
    }
    @Override
    public String toString() {
        return String.format("%d + %d = %d%s", die1, die2, sum, isDouble ? " (Double)" : "");
    }
}