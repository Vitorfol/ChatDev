'''
Custom checked exception thrown when a robot attempts an invalid movement (out of bounds, blocked, or robot dead).
'''
package com.chatdev.robot;
public class MovimentoInvalidoException extends Exception {
    public MovimentoInvalidoException(String message) {
        super(message);
    }
}