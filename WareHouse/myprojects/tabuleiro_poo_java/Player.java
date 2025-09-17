package chatdev.boardgame;
/* '''
Abstract Player class. Implements common state and defines an abstract rollDice method which subclasses
(LuckyPlayer, UnluckyPlayer, NormalPlayer) override to implement type-specific dice behavior.
''' */
/**
 * Abstract base class for players.
 */
public abstract class Player {
    protected String name;
    protected int position = 0;
    protected boolean skipNextTurn = false;
    protected int movesMade = 0;
    /**
     * Construct player with a name.
     * @param name player name
     */
    public Player(String name) {
        this.name = name;
    }
    /**
     * Roll dice according to player type rules.
     * Implementations should return a DiceResult including die1, die2, sum and double flag.
     */
    public abstract DiceResult rollDice();
    public String getName() {
        return name;
    }
    public int getPosition() {
        return position;
    }
    public void moveBy(int steps) {
        position += steps;
        if (position < 0) position = 0;
    }
    public void moveTo(int pos) {
        position = pos;
        if (position < 0) position = 0;
    }
    public boolean isSkipNextTurn() {
        return skipNextTurn;
    }
    public void setSkipNextTurn(boolean skipNextTurn) {
        this.skipNextTurn = skipNextTurn;
    }
    public int getMovesMade() {
        return movesMade;
    }
    public void incrementMovesMade() {
        movesMade++;
    }
    @Override
    public String toString() {
        return String.format("%s (%s) - Pos: %d", name, this.getClass().getSimpleName(), position);
    }
}