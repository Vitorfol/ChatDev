'''
RoboInteligente extends Robo: overrides move so it never repeats the same invalid move in one attempt.
It will keep trying other directions until a valid move occurs or all directions exhausted.
'''
/* '''
RoboInteligente extends Robo: overrides move so it never repeats the same invalid move in one attempt.
It will keep trying other directions until a valid move occurs or all directions exhausted.
''' */
import java.awt.Color;
import java.util.HashSet;
import java.util.Set;
public class RoboInteligente extends Robo {
    public RoboInteligente(String name, Position start, Color color) {
        super(name, start, color);
    }
    // choose the passed dir as first attempt, but if invalid, try other directions (never repeat same invalid).
    @Override
    public boolean move(Board board, int initialDir) throws MovimentoInvalidoException {
        if (!alive) throw new MovimentoInvalidoException(name + " is dead and cannot move.");
        Set<Integer> tried = new HashSet<>();
        int attempts = 0;
        int dir = initialDir;
        while (attempts < 4) {
            if (tried.contains(dir)) {
                dir = (dir + 1) % 4;
                attempts++;
                continue;
            }
            try {
                // attempt move using parent logic but catch invalid exceptions to try alternatives
                boolean moved = super.move(board, dir);
                // if move succeeded or robot died, return accordingly
                return moved;
            } catch (MovimentoInvalidoException ex) {
                // remember invalid and try another direction
                tried.add(dir);
                incrementInvalid();
                board.log(name + " intelligent avoided repeating invalid move: " + ex.getMessage());
                // pick next direction not attempted
                dir = (dir + 1) % 4;
                attempts++;
            }
        }
        // all directions exhausted
        throw new MovimentoInvalidoException(name + " could not find any valid move (all directions invalid).");
    }
}