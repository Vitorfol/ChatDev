'''
Player: holds name, color, position, coins, type, and skipNextTurn flag.
'''
/*
Player: holds name, color, position, coins, type, and skipNextTurn flag.
*/
package app;
public class Player {
    private String name;
    private String color;
    private int position;
    private int coins;
    private PlayerType type;
    private boolean skipNextTurn;
    public Player(String name, String color, PlayerType type) {
        this.name = name;
        this.color = color;
        this.type = type;
        this.position = 0;
        this.coins = 0;
        this.skipNextTurn = false;
    }
    public Player copy() {
        Player p = new Player(this.name, this.color, this.type);
        p.position = this.position;
        p.coins = this.coins;
        p.skipNextTurn = this.skipNextTurn;
        return p;
    }
    public String getName() { return name; }
    public String getColor() { return color; }
    public int getPosition() { return position; }
    public void setPosition(int pos) { this.position = pos; }
    public int getCoins() { return coins; }
    public void addCoins(int n) { this.coins += n; }
    public PlayerType getType() { return type; }
    public void setType(PlayerType type) { this.type = type; }
    public boolean isSkipNextTurn() { return skipNextTurn; }
    public void setSkipNextTurn(boolean v) { this.skipNextTurn = v; }
}