'''
Abstract Obstacle class declares interact(Robo, Board, Position previousPosition).
Concrete subclasses implement their own effect.
'''
package com.chatdev.robot;
public abstract class Obstacle {
    // Called when a robot moves into the obstacle's cell.
    // previousPos is the robot's position before the move (so Rock can push back).
    public abstract void interact(Robo robot, Board board, Position previousPos);
    public abstract String label();
}