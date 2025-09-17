'''
Unlucky square: move back 3 spaces unless the player is LUCKY.
'''
import java.util.function.Consumer;
public class UnluckySquare extends Square {
    public UnluckySquare(int index) { super(index); }
    @Override
    public String getName() { return "Unlucky"; }
    @Override
    public void applyEffect(Game game, Player p, int diceSum, Consumer<String> logger) {
        if (p.getType() == PlayerType.LUCKY) {
            logger.accept(p.getName() + " is LUCKY; Unlucky square has no backward effect.");
            return;
        }
        int target = p.getPosition() - 3;
        if (target < 0) target = 0;
        p.setPosition(target);
        logger.accept(p.getName() + " moves back 3 spaces due to Unlucky square to position " + p.getPosition());
    }
}