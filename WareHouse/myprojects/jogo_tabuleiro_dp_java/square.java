'''
Abstract Square class and concrete subclasses for each square type.
Each subclass implements onLand(Player, Game) to apply its rule.
'''
/*
Abstract Square class and concrete subclasses for each square type.
Each subclass implements onLand(Player, Game) to apply its rule.
*/
package app;
import java.util.concurrent.ThreadLocalRandom;
public abstract class Square {
    protected String name;
    public Square(String name) { this.name = name; }
    public String getName() { return name; }
    // invoked when a player lands on this square
    public abstract void onLand(Player player, Game game);
}
/* SimpleSquare: no special rule, but awards 1 coin in Game.applySquareEffectForPlayerIndex */
class SimpleSquare extends Square {
    public SimpleSquare() { super("Simple"); }
    @Override
    public void onLand(Player player, Game game) {
        // Nothing extra here (coin given by Game).
    }
}
/* Surprise: changes player type randomly to LUCKY/UNLUCKY/NORMAL */
class SurpriseSquare extends Square {
    public SurpriseSquare() { super("Surprise"); }
    @Override
    public void onLand(Player player, Game game) {
        // Randomly assign a new player type
        PlayerType[] types = PlayerType.values();
        PlayerType newType = types[ThreadLocalRandom.current().nextInt(types.length)];
        player.setType(newType);
        // Notify UI/listener if present
        GameListener listener = (game != null) ? game.getListenerProxy() : null;
        if (listener != null) {
            listener.updateStatus(player.getName() + " is now " + newType + " (Surprise).");
        }
    }
}
/* Prison: miss a turn */
class PrisonSquare extends Square {
    public PrisonSquare() { super("Prison"); }
    @Override
    public void onLand(Player player, Game game) {
        player.setSkipNextTurn(true);
        // Game will inform via its status log
    }
}
/* Lucky square: move forward 3 spaces unless player is Unlucky */
class LuckySquare extends Square {
    public LuckySquare() { super("Lucky"); }
    @Override
    public void onLand(Player player, Game game) {
        if (player.getType() == PlayerType.UNLUCKY) {
            // nothing
            if (game != null && game.getListenerProxy() != null) {
                game.getListenerProxy().updateStatus(player.getName() + " is Unlucky — Lucky square has no effect.");
            }
            return;
        }
        int newPos = player.getPosition() + 3;
        player.setPosition(newPos);
        if (game != null && game.getListenerProxy() != null) {
            game.getListenerProxy().updateStatus(player.getName() + " advances 3 squares (Lucky). Now at " + newPos);
        }
    }
}
/* Unlucky square: move back 3 unless player is Lucky */
class UnluckySquare extends Square {
    public UnluckySquare() { super("Unlucky"); }
    @Override
    public void onLand(Player player, Game game) {
        if (player.getType() == PlayerType.LUCKY) {
            if (game != null && game.getListenerProxy() != null) {
                game.getListenerProxy().updateStatus(player.getName() + " is Lucky — Unlucky square has no effect.");
            }
            return;
        }
        int newPos = player.getPosition() - 3;
        if (newPos < 0) newPos = 0;
        player.setPosition(newPos);
        if (game != null && game.getListenerProxy() != null) {
            game.getListenerProxy().updateStatus(player.getName() + " moves back 3 squares (Unlucky). Now at " + newPos);
        }
    }
}
/* Reverse square: swap with the last-place player, unless already last */
class ReverseSquare extends Square {
    public ReverseSquare() { super("Reverse"); }
    @Override
    public void onLand(Player player, Game game) {
        Player last = game.findLastPlacePlayer();
        if (last == null) return;
        if (last == player) {
            if (game != null && game.getListenerProxy() != null) {
                game.getListenerProxy().updateStatus(player.getName() + " is already in last place; Reverse has no effect.");
            }
            return;
        }
        int pPos = player.getPosition();
        int lPos = last.getPosition();
        player.setPosition(lPos);
        last.setPosition(pPos);
        if (game != null && game.getListenerProxy() != null) {
            game.getListenerProxy().updateStatus(player.getName() + " swaps position with " + last.getName());
        }
    }
}
/* PlayAgain: extra turn */
class PlayAgainSquare extends Square {
    public PlayAgainSquare() { super("PlayAgain"); }
    @Override
    public void onLand(Player player, Game game) {
        // Grant extra turn via Game helper
        if (game != null) {
            game.forceExtraTurnForCurrent();
            if (game.getListenerProxy() != null) {
                game.getListenerProxy().updateStatus(player.getName() + " gets an extra turn (PlayAgain).");
            }
        }
    }
}