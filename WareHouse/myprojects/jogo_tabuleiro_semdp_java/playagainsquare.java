'''
PlayAgain square: grants an extra turn to the landing player.
'''
import java.util.function.Consumer;
public class PlayAgainSquare extends Square {
    public PlayAgainSquare(int index) { super(index); }
    @Override
    public String getName() { return "PlayAgain"; }
    @Override
    public void applyEffect(Game game, Player p, int diceSum, Consumer<String> logger) {
        game.grantExtraTurnTo(p);
        logger.accept(p.getName() + " will have an extra turn (PlayAgain square).");
    }
}