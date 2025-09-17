'''
Abstract square base class and default behaviors.
'''
import java.util.function.Consumer;
public abstract class Square {
    private int index; // 1-based index on board
    public Square(int index) { this.index = index; }
    public int getIndex() { return index; }
    public abstract String getName();
    /**
     * Apply effect of this square for player p.
     * Implementations may manipulate player and game, and should log messages using logger.accept(...).
     *
     * @param game Game facade reference
     * @param p Player landing on this square
     * @param diceSum sum of dice that caused landing (0 in debug mode)
     * @param logger consumer to log messages
     */
    public abstract void applyEffect(Game game, Player p, int diceSum, Consumer<String> logger);
}