'''
Bomb: when a robot steps on a Bomb, it explodes (robot set to dead and removed from board).
'''
package com.chatdev.robot;
public class Bomb extends Obstacle {
    @Override
    public void interact(Robo robot, Board board, Position previousPos) {
        // Robot explodes: set to dead and remove from board.
        robot.setAlive(false);
        board.removeRobot(robot);
        // Remove bomb after explosion
        board.removeObstacleAt(robot.getPosition());
    }
    @Override
    public String label() {
        return "B";
    }
}