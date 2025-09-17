'''
Board logic and special square implementations.
apply_square_effect(player, players) applies effects for the square where `player` currently is.
This implementation resolves chained effects: if a square effect changes the player's position or type
such that the new square should trigger more effects, apply_square_effect will re-evaluate until a stable
state is reached or a safety limit is hit.
Returns (new_player_or_None, messages_list)
- new_player_or_None: a replacement player instance if type changed (caller should replace in player list)
- messages_list: list of strings describing events
Special squares:
- 10, 25, 38: cause the player to miss next turn
- 13: surprise card -> change player type randomly (must differ from current)
- 5, 15, 30: move player forward 3 spaces (unless player is Unlucky)
- 17, 27: force player to send an opponent back to start (we send the furthest ahead opponent)
- 20, 35: swap places with the one furthest behind
Note:
- Only the triggering player's square (and resulting chained squares) are re-evaluated here.
- Opponents affected (sent to start or swapped) will have their positions updated, but we do not
  recursively evaluate their new squares as part of this call (avoids complex cross-trigger recursion).
'''
from utils import choose_furthest_ahead, choose_furthest_behind, random_other_type
class Board:
    def __init__(self):
        self.size = 40
        self.miss_turn_squares = {10, 25, 38}
        self.surprise_square = 13
        self.forward_three = {5, 15, 30}
        self.send_opponent_back = {17, 27}
        self.swap_with_behind = {20, 35}
    def apply_square_effect(self, player, players):
        """
        Resolve all automatic effects triggered by the square the given player currently occupies.
        This will iteratively re-evaluate the player's square if their position or type changes,
        collecting messages describing each step.
        Parameters:
        - player: the Player object who triggered the square (the object from the players list)
        - players: list of all player objects (so we can affect opponents)
        Returns:
        - new_player_or_None: if the player's type changed, return the new Player instance (caller should replace),
                              otherwise None.
        - messages: list of string messages describing what happened.
        """
        messages = []
        new_player = None
        orig_player = player            # KEEP original players-list object for exclusions
        current = player                # we'll operate on current; may be cloned during processing
        visited = set()
        iterations = 0
        MAX_ITER = 10
        while True:
            iterations += 1
            if iterations > MAX_ITER:
                messages.append("Note: too many chained effects; stopping further automatic actions.")
                break
            state_key = (current.position, current.ptype, current.skip_next_turn)
            if state_key in visited:
                messages.append("Note: detected repeated state; stopping chained effects to avoid loop.")
                break
            visited.add(state_key)
            pos = current.position
            changed = False
            # Miss turn squares: set skip flag (no position/type change)
            if pos in self.miss_turn_squares and not current.skip_next_turn:
                current.skip_next_turn = True
                messages.append(f"{current.name} landed on {pos} and will miss the next turn.")
                # don't mark as positional change; continue evaluating same square only if needed
                # (no need to continue loop solely for skip flag; but we leave changed False)
            # Surprise card: change player type randomly (must differ)
            if pos == self.surprise_square:
                other = random_other_type(current.ptype)
                if other != current.ptype:
                    old_type = current.ptype
                    new_current = current.clone_as(other)
                    new_player = new_current  # remember to return replacement
                    current = new_current
                    messages.append(f"{current.name} landed on {pos} (Surprise!) and changes type from {old_type} to {other}.")
                    changed = True
                    # After a type change, it's important to re-evaluate the current square under the new type
                    # so continue to next iteration
                    if changed:
                        continue
            # Move forward 3 spaces unless Unlucky
            if pos in self.forward_three:
                if current.ptype == "unlucky":
                    messages.append(f"{current.name} landed on {pos} but is Unlucky; does not move forward 3 spaces.")
                else:
                    old_pos = current.position
                    current.position += 3
                    messages.append(f"{current.name} landed on {pos} and moves forward 3 spaces to {current.position}.")
                    changed = True
                    # re-evaluate new square
                    if changed:
                        continue
            # Send opponent back to start (furthest ahead)
            if pos in self.send_opponent_back:
                # Exclude the original player object (the one actually present in players list),
                # because current may be a newly cloned object not in that list.
                target = choose_furthest_ahead(players, exclude_player=orig_player)
                if target is not None and target.position > 0:
                    target.position = 0
                    messages.append(f"{current.name} landed on {pos} and sends {target.name} back to start!")
                else:
                    messages.append(f"{current.name} landed on {pos} but no opponent to send back to start.")
                # sending opponent back doesn't change current player's position/type, so no 'changed' needed
            # Swap with furthest behind
            if pos in self.swap_with_behind:
                # Exclude the original player object for the same reason as above.
                target = choose_furthest_behind(players, exclude_player=orig_player)
                if target is not None:
                    messages.append(f"{current.name} landed on {pos} and swaps places with {target.name} (was at {target.position}).")
                    # swap positions
                    current.position, target.position = target.position, current.position
                    messages.append(f"{current.name} is now at {current.position}; {target.name} is now at {target.position}.")
                    changed = True
                    # re-evaluate new square after swap for current player
                    if changed:
                        continue
                else:
                    messages.append(f"{current.name} landed on {pos} but no opponent to swap with.")
            # If no position or type change occurred this iteration, we're stable
            if not changed:
                break
        # Return the new player instance if type changed (caller should replace in players list), and messages
        return new_player, messages