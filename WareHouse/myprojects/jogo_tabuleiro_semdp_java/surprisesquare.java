'''
Surprise square: changes player type according to the dice sum of the move.
According to spec: dice sum >= 7 -> LUCKY, <=6 -> UNLUCKY, else NORMAL.
'''
import java.util.function.Consumer;
public class SurpriseSquare extends Square {
    public SurpriseSquare(int index) { super(index); }
    @Override
    public String getName() { return "Surprise"; }
    @Override
    public void applyEffect(Game game, Player p, int diceSum, Consumer<String> logger) {
        PlayerType newType = Game.getTypeFromDiceSum(diceSum);
        p.setType(newType);
        logger.accept(p.getName() + " type changed to " + newType + " by Surprise square (diceSum=" + diceSum + ").");
    }
}