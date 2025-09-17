'''
SquareFactory: uses SquareType to build concrete Square instances.
'''
/*
SquareFactory: uses SquareType to build concrete Square instances.
*/
package app;
public class SquareFactory {
    public static Square createSquare(SquareType st) {
        switch (st) {
            case SIMPLE: return new SimpleSquare();
            case SURPRISE: return new SurpriseSquare();
            case PRISON: return new PrisonSquare();
            case LUCKY: return new LuckySquare();
            case UNLUCKY: return new UnluckySquare();
            case REVERSE: return new ReverseSquare();
            case PLAYAGAIN: return new PlayAgainSquare();
            default: return new SimpleSquare();
        }
    }
}