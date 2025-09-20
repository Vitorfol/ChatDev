'''
RoboInteligente: subclass of Robo which can autonomously decide moves.
It implements decideAndMove(Board) which tries random directions and never repeats the same invalid move in the same decision cycle.
If all directions are invalid, it throws MovimentoInvalidoException.
'''
package com.chatdev.robot;
import java.util.*;
public class RoboInteligente extends Robo {
    private final Random rand = new Random();
    public RoboInteligente(String id, Position start, int colorIndex) {
        super(id, start, colorIndex);
    }
    // Autonomous method: picks random directions, avoids repeating same invalid move within the attempt,
    // and keeps trying until it executes a valid move or all options exhausted.
    public void decideAndMove(Board board) throws MovimentoInvalidoException {
        List<Integer> directions = new ArrayList<>(Arrays.asList(0,1,2,3));
        Collections.shuffle(directions, rand);
        // Try each direction in random order; if invalid, try another. If one succeeds, return.
        for (int dir : directions) {
            try {
                this.move(dir, board);
                return;
            } catch (MovimentoInvalidoException ex) {
                // don't repeat same invalid move in this attempt
            }
        }
        // If we arrive here, all directions failed
        throw new MovimentoInvalidoException("No valid moves available for robot " + this.getId());
    }
}