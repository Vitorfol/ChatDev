'''
Game logic and board management for the Robot-Food simulation.
Maintains robot list, obstacle map, food position, and enforces move rules.
'''
DIRS = {
    "UP": (-1, 0),
    "RIGHT": (0, 1),
    "DOWN": (1, 0),
    "LEFT": (0, -1)
}
# Map direction name to an integer code (consistent ordering)
DIR_NAMES = {name: idx for idx, name in enumerate(DIRS.keys())}
class Game:
    def __init__(self, size=4):
        self.size = size
        self.robots = []
        self.obstacles = {}  # dict mapping (x,y) -> Obstacle instance
        self.food = None  # (x,y)
        self.found_food = False
    def in_bounds(self, x, y):
        """Return True if (x,y) is inside the board."""
        return 0 <= x < self.size and 0 <= y < self.size
    def is_occupied(self, x, y):
        """
        A cell is considered occupied if a living (non-exploded) robot is present.
        Exploded robots are not considered to occupy cells for movement blockage.
        """
        for r in self.robots:
            if not r.exploded and r.x == x and r.y == y:
                return True
        return False
    def add_robot(self, robot):
        """
        Add a robot to the game ensuring its starting position is valid and not occupied.
        Raises ValueError on invalid starting position.
        """
        if not self.in_bounds(robot.x, robot.y):
            raise ValueError("Robot position out of bounds.")
        if self.is_occupied(robot.x, robot.y):
            raise ValueError("Another robot occupies the starting position.")
        if (robot.x, robot.y) in self.obstacles:
            raise ValueError("Cannot place robot on an obstacle.")
        # Ensure starting position is not the food (allowed but typical flow avoids it).
        # We allow robot to start on food if desired; detection will mark found_food later.
        self.robots.append(robot)
    def remove_robot(self, robot):
        """
        Mark a robot as removed/exploded. We keep the robot instance in the list for visualization
        but set its exploded flag. The robot's coordinates remain at the explosion site.
        """
        # Ensure robot present in list
        if robot not in self.robots:
            # If robot is not tracked, nothing to do.
            return
        robot.exploded = True
        # Do not remove from self.robots to keep visualization; is_occupied consults exploded.
        # No further action needed here.
    def place_obstacle(self, x, y, obstacle):
        """
        Place an obstacle at (x,y). Raises ValueError if out of bounds or placing on food.
        """
        if not self.in_bounds(x, y):
            raise ValueError("Obstacle out of bounds.")
        if self.food is not None and (x, y) == self.food:
            raise ValueError("Cannot place obstacle on food.")
        self.obstacles[(x, y)] = obstacle
    def apply_interaction(self, robot):
        """
        If the robot stepped on an obstacle, delegate to the obstacle's interact method.
        Obstacles are responsible for updating robot and game state appropriately.
        """
        pos = (robot.x, robot.y)
        if pos in self.obstacles:
            obs = self.obstacles[pos]
            obs.interact(robot, self)
    def check_food(self, robot):
        """
        Return True if the robot is on the food cell.
        """
        return self.food == (robot.x, robot.y)
    def place_food(self, x, y):
        """
        Place food at (x,y). Raises ValueError if out of bounds or if an obstacle exists there.
        """
        if not self.in_bounds(x, y):
            raise ValueError("Food out of bounds.")
        if (x, y) in self.obstacles:
            raise ValueError("Cannot place food on an obstacle.")
        self.food = (x, y)
        # Reset found flag if relocating food mid-game
        self.found_food = False