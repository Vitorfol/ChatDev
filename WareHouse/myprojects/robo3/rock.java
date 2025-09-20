'''
Rock: when a robot steps on a Rock, it gets pushed back to its previous position (if available).
The rock remains on the board.
'''
package com.chatdev.robot;
public class Rock extends Obstacle {
    @Override
    public void interact(Robo robot, Board board, Position previousPos) {
        // Push back to previous position if still empty and within bounds
        if (previousPos != null && board.isWithinBounds(previousPos) && board.isCellEmpty(previousPos)) {
            board.updateRobotPosition(robot, previousPos);
        } else {
            // Keep the robot in the rock cell (no-op, since robot already moved there)
        }
    }
    @Override
    public String label() {
        return "R";
    }
}