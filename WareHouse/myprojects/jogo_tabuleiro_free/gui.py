'''
Graphical User Interface using tkinter.
Provides setup interface to choose players, board size and customize square types,
then starts the Game facade and runs the play interface where users roll dice
or use debug input to move players to a chosen destination square.
'''
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from functools import partial
import random
from game import Game
from models import SquareType
MAX_PLAYERS = 6
DEFAULT_BOARD_SIZE = 20
COLOR_OPTIONS = ["red", "blue", "green", "yellow", "orange", "purple"]
class GameGUI:
    def __init__(self, master):
        self.master = master
        self.master.geometry("1000x650")
        self.game = None
        self.setup_frame = ttk.Frame(master)
        self.setup_frame.pack(fill=tk.BOTH, expand=True)
        self.build_setup_ui()
    def build_setup_ui(self):
        frm = self.setup_frame
        # Top configuration
        config_frame = ttk.LabelFrame(frm, text="Game Configuration")
        config_frame.pack(fill=tk.X, padx=10, pady=8)
        ttk.Label(config_frame, text="Board Size (squares):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.board_size_var = tk.IntVar(value=DEFAULT_BOARD_SIZE)
        ttk.Entry(config_frame, textvariable=self.board_size_var, width=6).grid(row=0, column=1, sticky=tk.W, padx=5)
        ttk.Label(config_frame, text="Number of Players:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.num_players_var = tk.IntVar(value=2)
        num_spin = ttk.Spinbox(config_frame, from_=2, to=MAX_PLAYERS, textvariable=self.num_players_var, width=4, command=self.refresh_players_ui)
        num_spin.grid(row=0, column=3, sticky=tk.W, padx=5)
        self.debug_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(config_frame, text="Debug mode (manual destination input)", variable=self.debug_var).grid(row=0, column=4, padx=10)
        # Players section
        players_frame = ttk.LabelFrame(frm, text="Players (choose color and initial type)")
        players_frame.pack(fill=tk.X, padx=10, pady=8)
        self.player_rows = []
        self.players_frame_inner = ttk.Frame(players_frame)
        self.players_frame_inner.pack(fill=tk.X, padx=5, pady=5)
        self.refresh_players_ui()
        # Board squares editor
        squares_frame = ttk.LabelFrame(frm, text="Board Squares (select index to edit)")
        squares_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)
        top_sq_editor = ttk.Frame(squares_frame)
        top_sq_editor.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(top_sq_editor, text="Initialize board with default special squares?").pack(side=tk.LEFT, padx=5)
        ttk.Button(top_sq_editor, text="Auto-fill some special squares", command=self.autofill_squares).pack(side=tk.LEFT, padx=5)
        board_size_btn = ttk.Button(top_sq_editor, text="Reset squares to default Simple", command=self.reset_squares)
        board_size_btn.pack(side=tk.LEFT, padx=5)
        self.squares_canvas_frame = ttk.Frame(squares_frame)
        self.squares_canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        # Scrollable area with per-square editor
        self.squares_canvas = tk.Canvas(self.squares_canvas_frame)
        self.squares_scrollbar = ttk.Scrollbar(self.squares_canvas_frame, orient="vertical", command=self.squares_canvas.yview)
        self.squares_inner = ttk.Frame(self.squares_canvas)
        self.squares_inner.bind(
            "<Configure>",
            lambda e: self.squares_canvas.configure(scrollregion=self.squares_canvas.bbox("all"))
        )
        self.squares_canvas.create_window((0, 0), window=self.squares_inner, anchor="nw")
        self.squares_canvas.configure(yscrollcommand=self.squares_scrollbar.set)
        self.squares_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.squares_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.square_widgets = []
        self.build_squares_editor()
        start_btn = ttk.Button(frm, text="Start Game", command=self.start_game)
        start_btn.pack(pady=8)
    def refresh_players_ui(self):
        # Clear existing rows
        for widget in self.players_frame_inner.winfo_children():
            widget.destroy()
        self.player_rows = []
        n = self.num_players_var.get()
        for i in range(n):
            row = {}
            lbl = ttk.Label(self.players_frame_inner, text=f"Player {i+1} name:")
            lbl.grid(row=i, column=0, padx=5, pady=3, sticky=tk.W)
            name_var = tk.StringVar(value=f"P{i+1}")
            entry = ttk.Entry(self.players_frame_inner, textvariable=name_var, width=12)
            entry.grid(row=i, column=1, padx=5)
            row['name'] = name_var
            ttk.Label(self.players_frame_inner, text="Color:").grid(row=i, column=2, padx=5)
            color_var = tk.StringVar(value=COLOR_OPTIONS[i % len(COLOR_OPTIONS)])
            color_menu = ttk.Combobox(self.players_frame_inner, values=COLOR_OPTIONS, textvariable=color_var, width=10, state="readonly")
            color_menu.grid(row=i, column=3, padx=5)
            row['color'] = color_var
            ttk.Label(self.players_frame_inner, text="Type:").grid(row=i, column=4, padx=5)
            type_var = tk.StringVar(value="normal" if i>1 else ("lucky" if i%2==0 else "unlucky"))
            type_menu = ttk.Combobox(self.players_frame_inner, values=["lucky","unlucky","normal"], textvariable=type_var, width=10, state="readonly")
            type_menu.grid(row=i, column=5, padx=5)
            row['type'] = type_var
            self.player_rows.append(row)
    def build_squares_editor(self):
        # initialize squares widgets according to board_size
        for widget in self.squares_inner.winfo_children():
            widget.destroy()
        self.square_widgets = []
        size = max(5, int(self.board_size_var.get()))
        self.board_size_var.set(size)
        for i in range(size):
            lbl = ttk.Label(self.squares_inner, text=f"{i}", width=6)
            lbl.grid(row=i, column=0, padx=3, pady=1)
            type_var = tk.StringVar(value="SIMPLE")
            dd = ttk.Combobox(self.squares_inner, values=[t.name for t in SquareType], textvariable=type_var, width=20, state="readonly")
            dd.grid(row=i, column=1, padx=3, pady=1)
            # Make start (0) and final (size-1) always SIMPLE and disabled
            if i==0 or i==size-1:
                type_var.set("SIMPLE")
                dd.state(["disabled"])
            self.square_widgets.append((type_var, dd))
    def reset_squares(self):
        self.build_squares_editor()
    def autofill_squares(self):
        # Randomly set some special squares but keep start & final simple
        size = self.board_size_var.get()
        if size < 5:
            messagebox.showwarning("Board too small", "Please choose board size >= 5")
            return
        special = [SquareType.SURPRISE, SquareType.PRISON, SquareType.LUCKY, SquareType.UNLUCKY, SquareType.REVERSE, SquareType.PLAYAGAIN]
        for i, (type_var, dd) in enumerate(self.square_widgets):
            if i==0 or i==size-1:
                type_var.set("SIMPLE")
                continue
            choice = random.choice(special + [SquareType.SIMPLE]*3)
            type_var.set(choice.name)
    def start_game(self):
        # Validate players
        n = self.num_players_var.get()
        if n < 2 or n > MAX_PLAYERS:
            messagebox.showerror("Invalid players", f"Number of players must be between 2 and {MAX_PLAYERS}")
            return
        players = []
        used_colors = set()
        types_set = set()
        for i, row in enumerate(self.player_rows):
            name = row['name'].get().strip() or f"P{i+1}"
            color = row['color'].get()
            ptype = row['type'].get()
            if color in used_colors:
                messagebox.showerror("Color clash", f"Color {color} used by more than one player. Choose distinct colors.")
                return
            used_colors.add(color)
            types_set.add(ptype)
            players.append({"name": name, "color": color, "type": ptype})
        if len(types_set) < 2:
            messagebox.showerror("Player types", "Please choose at least two different player types among players.")
            return
        # Build squares_types list
        squares_types = []
        size = self.board_size_var.get()
        if size != len(self.square_widgets):
            self.build_squares_editor()
        for i, (type_var, dd) in enumerate(self.square_widgets):
            # convert type_var string to SquareType
            st_name = type_var.get().upper()
            try:
                st = SquareType[st_name]
            except Exception:
                st = SquareType.SIMPLE
            squares_types.append(st)
        # instantiate game
        self.game = Game()
        try:
            self.game.setup(board_size=size, players_list=players, squares_types=squares_types, debug=self.debug_var.get())
        except Exception as e:
            messagebox.showerror("Setup error", str(e))
            return
        # Hide setup frame and show game UI
        self.setup_frame.pack_forget()
        self.build_game_ui()
    def build_game_ui(self):
        self.game_frame = ttk.Frame(self.master)
        self.game_frame.pack(fill=tk.BOTH, expand=True)
        top_frame = ttk.Frame(self.game_frame)
        top_frame.pack(fill=tk.X, pady=5)
        self.info_label = ttk.Label(top_frame, text="Game started")
        self.info_label.pack(side=tk.LEFT, padx=8)
        self.turn_label = ttk.Label(top_frame, text="")
        self.turn_label.pack(side=tk.LEFT, padx=12)
        # Canvas for board
        board_frame = ttk.Frame(self.game_frame)
        board_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=5)
        self.canvas = tk.Canvas(board_frame, height=120, bg="white")
        self.canvas.pack(fill=tk.X, padx=5, pady=5)
        self.draw_board()
        # Side info and controls
        side_frame = ttk.Frame(self.game_frame)
        side_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=5)
        left_side = ttk.Frame(side_frame)
        left_side.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ttk.Label(left_side, text="Players:").pack(anchor=tk.W)
        self.players_listbox = tk.Listbox(left_side, height=8)
        self.players_listbox.pack(fill=tk.X, padx=5, pady=3)
        self.update_players_listbox()
        ttk.Label(left_side, text="Messages:").pack(anchor=tk.W, pady=(6,0))
        self.msg_area = scrolledtext.ScrolledText(left_side, height=12, state="disabled")
        self.msg_area.pack(fill=tk.BOTH, padx=5, pady=3, expand=True)
        # Controls
        ctrl_frame = ttk.Frame(side_frame)
        ctrl_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        self.roll_btn = ttk.Button(ctrl_frame, text="Roll Dice", command=self.on_roll)
        self.roll_btn.pack(fill=tk.X, pady=3)
        self.debug_entry_var = tk.StringVar()
        self.debug_entry = ttk.Entry(ctrl_frame, textvariable=self.debug_entry_var)
        self.debug_entry.pack(fill=tk.X, pady=3)
        self.debug_entry.insert(0, "destination index (debug)")
        self.debug_btn = ttk.Button(ctrl_frame, text="Use Debug Destination", command=self.on_debug_move)
        self.debug_btn.pack(fill=tk.X, pady=3)
        self.next_btn = ttk.Button(ctrl_frame, text="Next (skip turn)", command=self.on_next_skip)
        self.next_btn.pack(fill=tk.X, pady=3)
        self.end_btn = ttk.Button(ctrl_frame, text="End Game", command=self.on_end_game)
        self.end_btn.pack(fill=tk.X, pady=12)
        # Initialize labels
        self.update_turn_label()
        self.log("Game started. First player: " + self.game.players[self.game.current_player_index].name)
    def draw_board(self):
        # Draw squares horizontally
        self.canvas.delete("all")
        width = self.canvas.winfo_width() or 900
        if width < 200:
            width = 900
        size = self.game.board_size
        margin = 10
        available_w = max(600, width-2*margin)
        sq_w = available_w / size
        sq_h = 80
        self.square_coords = []
        for i in range(size):
            x1 = margin + i*sq_w
            y1 = 10
            x2 = x1 + sq_w - 4
            y2 = y1 + sq_h
            rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill="#f0f0f0")
            label = self.canvas.create_text((x1+x2)/2, y1+10, text=str(i), anchor="n", font=("Arial",9))
            # color special squares
            st = self.game.squares[i].type
            color = "#ffffff"
            if st == SquareType.SURPRISE:
                color = "#d0f7d0"
            elif st == SquareType.PRISON:
                color = "#f7d0d0"
            elif st == SquareType.LUCKY:
                color = "#d0e0ff"
            elif st == SquareType.UNLUCKY:
                color = "#ffd0d0"
            elif st == SquareType.REVERSE:
                color = "#f2d9ff"
            elif st == SquareType.PLAYAGAIN:
                color = "#fff0b3"
            self.canvas.itemconfig(rect, fill=color)
            self.square_coords.append((x1, y1, x2, y2))
        self.draw_tokens()
    def draw_tokens(self):
        # Remove existing tokens
        self.canvas.delete("token")
        # For each player, draw a small oval on their square with offset
        for idx, p in enumerate(self.game.players):
            pos = p.position
            if pos >= self.game.board_size:
                pos = self.game.board_size-1
            x1,y1,x2,y2 = self.square_coords[pos]
            spacing = 8
            cx = x1 + 12 + (idx * spacing)
            cy = y2 - 18
            r = 6
            color = p.color
            self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill=color, tags="token", outline="black")
    def update_players_listbox(self):
        self.players_listbox.delete(0, tk.END)
        for p in self.game.players:
            self.players_listbox.insert(tk.END, f"{p.name} ({p.color}) - Pos: {p.position} Coins: {p.coins} Type: {p.ptype} Moves: {p.moves}")
    def update_turn_label(self):
        p = self.game.players[self.game.current_player_index]
        txt = f"Turn: {p.name} (Type: {p.ptype})"
        self.turn_label.config(text=txt)
    def log(self, text):
        self.msg_area.config(state="normal")
        self.msg_area.insert(tk.END, text + "\n")
        self.msg_area.see(tk.END)
        self.msg_area.config(state="disabled")
    def on_roll(self):
        if not self.game:
            return
        if self.game.finished:
            messagebox.showinfo("Game over", "Game already finished.")
            return
        result = self.game.next_turn()
        self.handle_turn_result(result)
    def on_debug_move(self):
        if not self.game:
            return
        if not self.game.debug:
            messagebox.showinfo("Not in debug mode", "Enable debug mode in setup to use this feature.")
            return
        val = self.debug_entry_var.get().strip()
        try:
            dest = int(val)
        except:
            messagebox.showerror("Invalid input", "Please enter a valid integer destination index.")
            return
        result = self.game.next_turn(debug_destination=dest)
        self.handle_turn_result(result)
    def on_next_skip(self):
        # Allow user to skip current player's turn (counts as a move)
        if not self.game or self.game.finished:
            return
        res = self.game.skip_current_player()
        self.handle_turn_result(res)
    def on_end_game(self):
        if not self.game:
            return
        winner, total_moves = self.game.end_game()
        summary = f"Game ended by user. "
        if winner:
            summary += f"Winner: {winner.name}\n"
        summary += f"Total moves: {total_moves}\nFinal positions:\n"
        for p in self.game.players:
            summary += f"- {p.name}: Pos {p.position}, Coins {p.coins}, Type {p.ptype}, Moves {p.moves}\n"
        messagebox.showinfo("Game Ended", summary)
        self.master.destroy()
    def handle_turn_result(self, result):
        # result contains messages, dice, winner info, extra_turn flag, moved_player index etc
        msgs = result.get("messages", [])
        for m in msgs:
            self.log(m)
        dice = result.get("dice")
        if dice:
            d1, d2 = dice
            self.log(f"Dice: {d1} + {d2} = {d1+d2} {'(Double)' if d1==d2 else ''}")
        elif "debug_move" in result:
            d = result["debug_move"]
            self.log(f"Debug move to {d}")
        # Update UI
        self.update_players_listbox()
        self.update_turn_label()
        self.draw_board()
        if result.get("winner"):
            w = result["winner"]
            total_moves = result.get("total_moves", self.game.total_moves)
            summary = f"Winner: {w.name}\nTotal moves: {total_moves}\nFinal positions:\n"
            for p in self.game.players:
                summary += f"- {p.name}: Pos {p.position}, Coins {p.coins}, Type {p.ptype}, Moves {p.moves}\n"
            messagebox.showinfo("Game Over", summary)
            self.game.finished = True
            return
        # If the result indicates an extra immediate turn for the same player (double or PlayAgain),
        # do not advance the GUI's turn indicator (Game already handled current player index).
        if result.get("extra_turn"):
            self.log("Extra turn granted to same player.")
        else:
            # Next player's turn will be indicated
            pass
        # Keep focus on roll button
        self.roll_btn.focus_set()