'''
Model classes for Player, Square and SquareType.
Defines the data structures used by the Game facade and GUI.
'''
from enum import Enum
class SquareType(Enum):
    SIMPLE = 1
    SURPRISE = 2
    PRISON = 3
    LUCKY = 4
    UNLUCKY = 5
    REVERSE = 6
    PLAYAGAIN = 7
class Square:
    def __init__(self, index, stype=SquareType.SIMPLE):
        self.index = index
        self.type = stype
    def __repr__(self):
        return f"Square({self.index}, {self.type.name})"
class Player:
    def __init__(self, name, color, ptype="normal"):
        self.name = name
        self.color = color
        self.coins = 0
        self.position = 0
        self.ptype = ptype  # 'lucky', 'unlucky', 'normal'
        self.skip_turn = False
        self.moves = 0
    def __repr__(self):
        return f"Player({self.name}, pos={self.position}, coins={self.coins}, type={self.ptype})"