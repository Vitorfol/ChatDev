'''
Reverse square: swap with the last player (the player with smallest position), unless already last.
'''
import java.util.function.Consumer;
public class ReverseSquare extends Square {
    public ReverseSquare(int index) { super(index); }
    @Override
    public String getName() { return "Reverse"; }
    @Override
    public void applyEffect(Game game, Player p, int diceSum, Consumer<String> logger) {
        Player last = game.findLastOnBoard();
        if (last == null || last == p) {
            logger.accept(p.getName() + " is already last; Reverse has no effect.");
            return;
        }
        game.swapPositions(p, last);
        logger.accept(p.getName() + " swapped positions with " + last.getName() + " due to Reverse square.");
    }
}