'''
Model classes for robots, exceptions, and obstacles.
Defines MovimentoInvalidoException, Robo base class, RoboInteligente subclass,
Obstacle abstract class and concrete Bomb and Rock obstacles.
'''
from abc import ABC, abstractmethod
import random
from game import DIRS, DIR_NAMES
class MovimentoInvalidoException(Exception):
    """Raised when a robot attempts an invalid move (out of bounds or blocked)."""
    pass
class Obstacle(ABC):
    """Abstract obstacle. Subclasses must implement interact(robot, game)."""
    @abstractmethod
    def interact(self, robot, game):
        pass
class Bomb(Obstacle):
    """Bomb: robot explodes when stepping onto bomb. Bomb is removed afterwards."""
    def interact(self, robot, game):
        # When a robot steps onto a bomb it explodes.
        # Keep robot coordinates at the explosion site for visualization.
        robot.exploded = True
        # Let the game mark/remove the robot appropriately (keeps robot in list but flagged exploded).
        game.remove_robot(robot)
        # Remove the bomb from the board after it explodes (if still present).
        pos = (robot.x, robot.y)
        if pos in game.obstacles:
            del game.obstacles[pos]
class Rock(Obstacle):
    """Rock: pushes robot back to its previous position."""
    def interact(self, robot, game):
        # If the robot has a previous_position recorded, push it back there.
        if robot.previous_position is not None:
            robot.x, robot.y = robot.previous_position
        # Rock remains in place (no removal).
class Robo:
    """
    Basic robot with position and color.
    Provides move methods accepting a direction string or integer code.
    Tracks valid and invalid move counts and can detect food.
    """
    def __init__(self, id, x=0, y=0, color="blue"):
        self.id = id
        self.x = x
        self.y = y
        self.color = color
        self.exploded = False
        self.previous_position = None  # tuple(x,y)
        self.valid_moves = 0
        self.invalid_moves = 0
    def __str__(self):
        return f"Robo#{self.id} at ({self.x},{self.y})"
    def move(self, direction, game):
        """
        Move using a string direction: "UP","DOWN","LEFT","RIGHT".
        Raises MovimentoInvalidoException if move invalid.
        """
        if self.exploded:
            raise MovimentoInvalidoException("Robot exploded and cannot move.")
        dir_upper = direction.upper()
        if dir_upper not in DIRS:
            raise MovimentoInvalidoException(f"Invalid direction '{direction}'.")
        dx, dy = DIRS[dir_upper]
        nx, ny = self.x + dx, self.y + dy
        # check bounds
        if not game.in_bounds(nx, ny):
            self.invalid_moves += 1
            raise MovimentoInvalidoException("Move out of bounds.")
        # check occupancy by other living robots
        if game.is_occupied(nx, ny):
            self.invalid_moves += 1
            raise MovimentoInvalidoException("Cell occupied by another robot.")
        # move is allowed; record previous position and update
        self.previous_position = (self.x, self.y)
        self.x, self.y = nx, ny
        self.valid_moves += 1
        # apply interactions (obstacles may change robot/game state)
        game.apply_interaction(self)
        # check food
        if game.check_food(self):
            game.found_food = True
    def move_code(self, code, game):
        """
        Move using integer code: 0=UP,1=RIGHT,2=DOWN,3=LEFT
        This emulates method overloading for integer parameter.
        """
        try:
            code = int(code)
        except Exception:
            raise MovimentoInvalidoException("Invalid direction code.")
        mapping = {0: "UP", 1: "RIGHT", 2: "DOWN", 3: "LEFT"}
        if code not in mapping:
            raise MovimentoInvalidoException("Invalid direction code.")
        return self.move(mapping[code], game)
    def detect_food(self, game):
        return game.food == (self.x, self.y)
class RoboInteligente(Robo):
    """
    Intelligent robot that will not repeat the same invalid move during a single move attempt.
    If the requested move is invalid, it will try other directions until a valid move occurs.
    """
    def move(self, direction, game):
        if self.exploded:
            raise MovimentoInvalidoException("Robot exploded and cannot move.")
        preferred = direction.upper()
        if preferred not in DIRS:
            raise MovimentoInvalidoException(f"Invalid direction '{direction}'.")
        # Try preferred first, then the remaining directions
        candidates = [preferred] + [d for d in DIRS.keys() if d != preferred]
        last_exception = None
        for d in candidates:
            try:
                super(RoboInteligente, self).move(d, game)
                # successful move
                return
            except MovimentoInvalidoException as e:
                # remember last exception and try next direction
                last_exception = e
                continue
        # If none of the directions worked, raise a composed exception.
        if last_exception:
            raise MovimentoInvalidoException("All directions invalid; no move possible.")
        else:
            # defensive fallback
            raise MovimentoInvalidoException("No valid directions available.")
    def move_code(self, code, game):
        # map code -> direction and reuse intelligent move
        try:
            code = int(code)
        except Exception:
            raise MovimentoInvalidoException("Invalid direction code.")
        mapping = {0: "UP", 1: "RIGHT", 2: "DOWN", 3: "LEFT"}
        if code not in mapping:
            raise MovimentoInvalidoException("Invalid direction code.")
        return self.move(mapping[code], game)