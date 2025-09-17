package chatdev.boardgame;
/* '''
Unlucky player: ensures dice sum is always <= 6 by re-rolling until sum <= 6.
''' */
import java.util.Random;
/**
 * Unlucky player: dice sum always <= 6.
 */
public class UnluckyPlayer extends Player {
    private Random rand = new Random();
    public UnluckyPlayer(String name) {
        super(name);
    }
    @Override
    public DiceResult rollDice() {
        int d1, d2;
        do {
            d1 = rand.nextInt(6) + 1;
            d2 = rand.nextInt(6) + 1;
        } while (d1 + d2 > 6);
        return new DiceResult(d1, d2);
    }
}