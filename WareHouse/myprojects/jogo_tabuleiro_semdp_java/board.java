'''
Board holds the list of squares and provides accessors.
'''
import java.util.List;
public class Board {
    private List<Square> squares;
    public Board(List<Square> squares) {
        this.squares = squares;
    }
    public int getSize() { return squares.size(); }
    // squares are 1-based indices (square index i corresponds to squares.get(i-1))
    public Square getSquareAt(int position) {
        if (position <= 0) return null; // start
        if (position > squares.size()) return null;
        return squares.get(position - 1);
    }
    public List<Square> getSquares() { return squares; }
}