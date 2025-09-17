'''
Lucky square: move forward 3 spaces unless the player is UNLUCKY.
'''
import java.util.function.Consumer;
public class LuckySquare extends Square {
    public LuckySquare(int index) { super(index); }
    @Override
    public String getName() { return "Lucky"; }
    @Override
    public void applyEffect(Game game, Player p, int diceSum, Consumer<String> logger) {
        if (p.getType() == PlayerType.UNLUCKY) {
            logger.accept(p.getName() + " is UNLUCKY; Lucky square has no forward effect.");
            return;
        }
        int target = p.getPosition() + 3;
        p.setPosition(target);
        logger.accept(p.getName() + " moves forward 3 spaces due to Lucky square to position " + p.getPosition());
    }
}