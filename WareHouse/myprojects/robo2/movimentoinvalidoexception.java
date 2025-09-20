'''
Exception class thrown when a robot attempts an invalid movement.
'''
/* '''
Exception class thrown when a robot attempts an invalid movement.
''' */
public class MovimentoInvalidoException extends Exception {
    public MovimentoInvalidoException(String message) {
        super(message);
    }
}