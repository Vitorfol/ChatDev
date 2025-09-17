package chatdev.boardgame;
/* '''
Lucky player: ensures dice sum is always >= 7 by re-rolling until sum >=7.
''' */
import java.util.Random;
/**
 * Lucky player: dice sum always >= 7.
 */
public class LuckyPlayer extends Player {
    private Random rand = new Random();
    public LuckyPlayer(String name) {
        super(name);
    }
    @Override
    public DiceResult rollDice() {
        int d1, d2;
        do {
            d1 = rand.nextInt(6) + 1;
            d2 = rand.nextInt(6) + 1;
        } while (d1 + d2 < 7);
        return new DiceResult(d1, d2);
    }
}