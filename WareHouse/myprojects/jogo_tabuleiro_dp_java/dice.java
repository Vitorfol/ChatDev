'''
Dice utility to roll a die (1..6).
'''
/*
Dice utility to roll a die (1..6).
*/
package app;
import java.util.concurrent.ThreadLocalRandom;
public class Dice {
    public int rollDie() {
        return ThreadLocalRandom.current().nextInt(1,7);
    }
}