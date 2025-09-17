'''
Game facade class implementing the game logic.
Provides setup(...) and methods to advance turns (next_turn), skip turn, and end the game.
Encapsulates players, board squares, turn order, rules for special squares and debug mode.
'''
import random
from models import Player, Square, SquareType
class Game:
    def __init__(self):
        self.players = []
        self.squares = []
        self.board_size = 0
        self.current_player_index = 0
        self.debug = False
        self.total_moves = 0
        self.finished = False
    def setup(self, board_size, players_list, squares_types=None, debug=False):
        """
        board_size: int number of squares (>=5)
        players_list: list of dicts with keys: name, color, type ('lucky','unlucky','normal')
        squares_types: list of SquareType objects for each square index. If None, generate Simple squares.
        debug: bool, enable debug mode (manual destination input)
        """
        if board_size < 5:
            raise ValueError("Board size must be at least 5")
        if len(players_list) < 2 or len(players_list) > 6:
            raise ValueError("Players must be between 2 and 6")
        # initialize squares
        if squares_types and len(squares_types) != board_size:
            raise ValueError("squares_types length must equal board_size")
        self.board_size = board_size
        self.squares = []
        if squares_types:
            for i, st in enumerate(squares_types):
                self.squares.append(Square(i, st))
        else:
            for i in range(board_size):
                self.squares.append(Square(i, SquareType.SIMPLE))
        # enforce first and last are SIMPLE
        self.squares[0].type = SquareType.SIMPLE
        self.squares[-1].type = SquareType.SIMPLE
        # initialize players
        self.players = []
        for p in players_list:
            player = Player(name=p["name"], color=p["color"], ptype=p.get("type", "normal"))
            self.players.append(player)
        # check types diversity
        types = set([p.ptype for p in self.players])
        if len(types) < 2:
            raise ValueError("There must be at least two different player types among players.")
        self.current_player_index = 0
        self.debug = bool(debug)
        self.total_moves = 0
        self.finished = False
    def roll_dice(self):
        d1 = random.randint(1,6)
        d2 = random.randint(1,6)
        return d1, d2
    def next_turn(self, debug_destination=None):
        """
        Advance the game by one logical turn. If debug_destination is provided and debug mode is enabled,
        move current player directly to that destination square.
        Returns a dict with keys:
          - messages: list of strings
          - dice: (d1,d2) if rolled
          - debug_move: destination if used
          - winner: Player if someone won
          - total_moves: int
          - extra_turn: bool (if same player gets extra turn)
        """
        if self.finished:
            return {"messages": ["Game already finished."]}
        player = self.players[self.current_player_index]
        messages = []
        extra_turn = False
        # Check skip symbol
        if player.skip_turn:
            messages.append(f"{player.name} is in prison and misses this turn.")
            player.skip_turn = False
            player.moves += 1
            self.total_moves += 1
            # advance to next player
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            return {"messages": messages, "dice": None, "extra_turn": False}
        # perform move
        if self.debug and debug_destination is not None:
            dest = debug_destination
            if not isinstance(dest, int):
                messages.append("Invalid debug destination; must be integer.")
                return {"messages": messages}
            # clamp dest
            if dest < 0:
                dest = 0
            # compute steps
            steps = dest - player.position
            # move to destination
            player.position = dest
            messages.append(f"{player.name} (debug) moved to {player.position}.")
            result = self.apply_square_effect(player, messages, dice_sum=None, double=False)
            player.moves += 1
            self.total_moves += 1
            # check win
            if player.position >= self.board_size - 1:
                self.finished = True
                return {"messages": messages, "debug_move": dest, "winner": player, "total_moves": self.total_moves}
            # handle next turn: if extra turn, do not advance current_player_index
            if result.get("extra_turn"):
                extra_turn = True
            else:
                self.current_player_index = (self.current_player_index + 1) % len(self.players)
            return {"messages": messages, "debug_move": dest, "extra_turn": extra_turn}
        # Normal mode: roll dice
        d1, d2 = self.roll_dice()
        s = d1 + d2
        messages.append(f"{player.name} rolled {d1} and {d2} (sum {s}).")
        double = (d1 == d2)
        # Determine roll category by sum (as informational): >=7 lucky, <=6 unlucky
        roll_category = "lucky" if s >= 7 else "unlucky"
        # Move player by sum
        player.position += s
        messages.append(f"{player.name} moves to {player.position}.")
        # apply square effects
        result = self.apply_square_effect(player, messages, dice_sum=s, double=double)
        player.moves += 1
        self.total_moves += 1
        # Check for win (reach or pass final)
        if player.position >= self.board_size - 1:
            self.finished = True
            messages.append(f"{player.name} reached the final square and wins!")
            return {"messages": messages, "dice": (d1,d2), "winner": player, "total_moves": self.total_moves}
        # Determine next player
        if result.get("extra_turn") or double:
            # Extra turn: same player gets another turn
            # double also grants bonus turn per rules
            messages.append(f"{player.name} gets an extra turn{' (double roll)' if double else ''}.")
            extra_turn = True
            # do not advance current_player_index
        else:
            # advance
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
        return {"messages": messages, "dice": (d1,d2), "extra_turn": extra_turn}
    def apply_square_effect(self, player, messages, dice_sum=None, double=False):
        """
        Apply the effects of the square where the player currently stands.
        Modifies player state and messages. Returns dict with extra_turn flag.
        """
        extra_turn = False
        pos = player.position
        # If beyond last square, keep as is (win handled by caller)
        if pos >= self.board_size:
            player.position = self.board_size - 1
            return {"extra_turn": False}
        square = self.squares[pos]
        st = square.type
        messages.append(f"{player.name} landed on square {pos} ({st.name}).")
        if st == SquareType.SIMPLE:
            # normal square increases coins
            player.coins += 1
            messages.append(f"{player.name} collects 1 coin (total {player.coins}).")
        elif st == SquareType.SURPRISE:
            # Randomly change player type
            new_type = random.choice(["lucky","unlucky","normal"])
            old = player.ptype
            player.ptype = new_type
            messages.append(f"Surprise! {player.name} changes type from {old} to {new_type}.")
        elif st == SquareType.PRISON:
            player.skip_turn = True
            messages.append(f"{player.name} goes to prison and will miss next turn.")
        elif st == SquareType.LUCKY:
            # Lucky square moves forward 3 unless player's type is 'unlucky'
            if player.ptype != "unlucky":
                player.position += 3
                messages.append(f"Lucky square! {player.name} moves forward 3 to {player.position}.")
                # If moving lands beyond final, handled by caller's win check
            else:
                messages.append(f"{player.name} is unlucky; no forward bonus on Lucky square.")
        elif st == SquareType.UNLUCKY:
            # Unlucky square moves back 3 unless player.ptype == 'lucky'
            if player.ptype != "lucky":
                player.position -= 3
                if player.position < 0:
                    player.position = 0
                messages.append(f"Unlucky square! {player.name} moves back 3 to {player.position}.")
            else:
                messages.append(f"{player.name} is lucky; avoids moving back on Unlucky square.")
        elif st == SquareType.REVERSE:
            # Swap position with last player in turn order unless already last in turn order
            last_index = len(self.players) - 1
            if self.current_player_index == last_index:
                messages.append(f"{player.name} is already last in order; Reverse has no effect.")
            else:
                # swap positions with last player
                last_player = self.players[last_index]
                player.position, last_player.position = last_player.position, player.position
                messages.append(f"{player.name} swaps position with {last_player.name}. Now at {player.position}.")
        elif st == SquareType.PLAYAGAIN:
            extra_turn = True
            messages.append(f"PlayAgain square! {player.name} gets an extra turn.")
        # Safety clamp
        if player.position < 0:
            player.position = 0
        if player.position >= self.board_size:
            player.position = self.board_size - 1
        return {"extra_turn": extra_turn}
    def skip_current_player(self):
        """
        Allow UI to skip the current player manually (counts as a move).
        """
        if self.finished:
            return {"messages": ["Game already finished."]}
        player = self.players[self.current_player_index]
        messages = [f"{player.name}'s turn skipped by user."]
        player.moves += 1
        self.total_moves += 1
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        return {"messages": messages, "extra_turn": False}
    def end_game(self):
        """
        Ends the game and returns winner (if any) and total moves.
        """
        winner = None
        # winner determined by who is at final or farthest
        max_pos = -1
        for p in self.players:
            if p.position > max_pos:
                max_pos = p.position
                winner = p
        self.finished = True
        return winner, self.total_moves