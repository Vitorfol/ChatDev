'''
Utility functions:
- roll_two_dice(): returns two ints between 1 and 6
- choose_furthest_ahead(players, exclude_player): returns player object furthest ahead except exclude_player
- choose_furthest_behind(players, exclude_player): returns player object furthest behind except exclude_player
- random_other_type(current_type): pick a type different from current_type
'''
import random
def roll_two_dice():
    return random.randint(1,6), random.randint(1,6)
def choose_furthest_ahead(players, exclude_player=None):
    # Exclude by object identity to avoid issues with duplicate names
    candidates = [p for p in players if p is not exclude_player]
    if not candidates:
        return None
    # Furthest ahead means max position
    max_pos = max(c.position for c in candidates)
    ahead = [c for c in candidates if c.position == max_pos]
    # Return first in tie
    return ahead[0] if ahead else None
def choose_furthest_behind(players, exclude_player=None):
    candidates = [p for p in players if p is not exclude_player]
    if not candidates:
        return None
    min_pos = min(c.position for c in candidates)
    behind = [c for c in candidates if c.position == min_pos]
    return behind[0] if behind else None
def random_other_type(current_type):
    types = ["normal", "lucky", "unlucky"]
    others = [t for t in types if t != current_type]
    return random.choice(others)