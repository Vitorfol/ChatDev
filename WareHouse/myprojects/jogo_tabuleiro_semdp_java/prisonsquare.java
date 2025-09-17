'''
Prison square: player misses their next turn.
'''
import java.util.function.Consumer;
public class PrisonSquare extends Square {
    public PrisonSquare(int index) { super(index); }
    @Override
    public String getName() { return "Prison"; }
    @Override
    public void applyEffect(Game game, Player p, int diceSum, Consumer<String> logger) {
        p.setSkipNextTurn(true);
        logger.accept(p.getName() + " will miss their next turn (Prison).");
    }
}