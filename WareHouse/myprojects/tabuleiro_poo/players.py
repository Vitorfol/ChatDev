'''
Player classes with inheritance and polymorphic dice-rolling behavior.
- Player: base class
- LuckyPlayer: overrides roll_dice to ensure a sum >= 7
- UnluckyPlayer: overrides roll_dice to ensure a sum <= 6
- NormalPlayer: default behavior
All players have clone_as() to change type while preserving state.
'''
import random
from utils import roll_two_dice
class Player:
    def __init__(self, name):
        self.name = name
        self.position = 0
        self.skip_next_turn = False
        self.move_count = 0
        self.ptype = "normal"
    def roll_dice(self):
        d1, d2 = roll_two_dice()
        return d1, d2
    def move_by(self, steps):
        self.position += steps
    def clone_as(self, new_type):
        # Create a new instance of requested type, copying state
        if new_type == "normal":
            new_p = NormalPlayer(self.name)
        elif new_type == "lucky":
            new_p = LuckyPlayer(self.name)
        elif new_type == "unlucky":
            new_p = UnluckyPlayer(self.name)
        else:
            new_p = NormalPlayer(self.name)
        new_p.position = self.position
        new_p.skip_next_turn = self.skip_next_turn
        new_p.move_count = self.move_count
        return new_p
class LuckyPlayer(Player):
    def __init__(self, name):
        super().__init__(name)
        self.ptype = "lucky"
    def roll_dice(self):
        # Ensure sum >= 7. Re-roll until satisfied.
        while True:
            d1, d2 = roll_two_dice()
            if d1 + d2 >= 7:
                return d1, d2
class UnluckyPlayer(Player):
    def __init__(self, name):
        super().__init__(name)
        self.ptype = "unlucky"
    def roll_dice(self):
        # Ensure sum <= 6. Re-roll until satisfied.
        while True:
            d1, d2 = roll_two_dice()
            if d1 + d2 <= 6:
                return d1, d2
class NormalPlayer(Player):
    def __init__(self, name):
        super().__init__(name)
        self.ptype = "normal"