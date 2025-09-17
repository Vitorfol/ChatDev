'''
Simple square: no special rule, but counts as a normal square that increments player's coins.
'''
import java.util.function.Consumer;
public class SimpleSquare extends Square {
    public SimpleSquare(int index) { super(index); }
    @Override
    public String getName() { return "Simple"; }
    @Override
    public void applyEffect(Game game, Player p, int diceSum, Consumer<String> logger) {
        // Increment coins as normal-square reward
        p.addCoin();
        logger.accept(p.getName() + " gains 1 coin (now " + p.getCoins() + ") on Simple square.");
    }
}