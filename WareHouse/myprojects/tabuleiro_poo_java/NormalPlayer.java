package chatdev.boardgame;
/* '''
Normal player: standard dice roll from 1..6 each die.
''' */
import java.util.Random;
/**
 * Normal player: standard dice behavior.
 */
public class NormalPlayer extends Player {
    private Random rand = new Random();
    public NormalPlayer(String name) {
        super(name);
    }
    @Override
    public DiceResult rollDice() {
        int d1 = rand.nextInt(6) + 1;
        int d2 = rand.nextInt(6) + 1;
        return new DiceResult(d1, d2);
    }
}