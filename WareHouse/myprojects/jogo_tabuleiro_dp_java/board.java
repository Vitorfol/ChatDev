'''
Board: wraps ordered squares.
'''
/*
Board: wraps ordered squares.
*/
package app;
import java.util.List;
public class Board {
    private List<Square> squares;
    public Board(List<Square> squares) {
        this.squares = squares;
    }
    public Square getSquare(int index) {
        return squares.get(index);
    }
    public int getSize() {
        return squares.size();
    }
}