'''
Represents a player: name, display color, type, position, coins, skip-turn and extra-turn flags.
'''
import java.awt.Color;
public class Player {
    private String name;
    private Color color;
    private PlayerType type;
    private int position = 0;
    private int coins = 0;
    private boolean skipNextTurn = false;
    private boolean finished = false;
    private boolean hasExtraTurn = false;
    public Player(String name, Color color, PlayerType type) {
        this.name = name;
        this.color = color;
        this.type = type;
    }
    public String getName() { return name; }
    public Color getColor() { return color; }
    public PlayerType getType() { return type; }
    public void setType(PlayerType t) { this.type = t; }
    public int getPosition() { return position; }
    public void setPosition(int pos) {
        this.position = Math.max(0, pos);
    }
    public int getCoins() { return coins; }
    public void setCoins(int c) { this.coins = c; }
    public void addCoin() { this.coins++; }
    public boolean isSkipNextTurn() { return skipNextTurn; }
    public void setSkipNextTurn(boolean skip) { this.skipNextTurn = skip; }
    public boolean isFinished() { return finished; }
    public void setFinished(boolean f) { this.finished = f; }
    public boolean isHasExtraTurn() { return hasExtraTurn; }
    public void setHasExtraTurn(boolean has) { this.hasExtraTurn = has; }
}