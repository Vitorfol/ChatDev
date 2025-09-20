'''
Simple Position holder (row, col) with utilities.
'''
/* '''
Simple Position holder (row, col) with utilities.
''' */
public class Position {
    public int row;
    public int col;
    public Position(int r, int c) {
        this.row = r;
        this.col = c;
    }
    public Position(Position other) {
        this.row = other.row;
        this.col = other.col;
    }
    @Override
    public boolean equals(Object o) {
        if (!(o instanceof Position)) return false;
        Position p = (Position) o;
        return p.row == row && p.col == col;
    }
    @Override
    public int hashCode() {
        return row * 31 + col;
    }
    @Override
    public String toString() {
        return "(" + row + "," + col + ")";
    }
}