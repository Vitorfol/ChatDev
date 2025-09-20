'''
Position: simple immutable pair for row and column, with helpers.
'''
package com.chatdev.robot;
public class Position {
    private final int row;
    private final int col;
    public Position(int row, int col) {
        this.row = row;
        this.col = col;
    }
    public int row() { return row; }
    public int col() { return col; }
    public Position translate(int dr, int dc) {
        return new Position(row + dr, col + dc);
    }
    @Override
    public boolean equals(Object o) {
        if (!(o instanceof Position)) return false;
        Position p = (Position)o;
        return row == p.row && col == p.col;
    }
    @Override
    public int hashCode() {
        return 31 * row + col;
    }
    @Override
    public String toString() {
        return "(" + row + "," + col + ")";
    }
}