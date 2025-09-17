'''
Main GUI and game flow for the 40-square board game.
This file implements a Tkinter-based GUI. It uses classes defined in players.py, board.py, and utils.py.
The GameGUI class handles setup, player turns, dice rolling (or debug destination input),
special square effects, bonus turns for doubles, skip-turns, and game end display.
'''
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import random
from players import Player, LuckyPlayer, UnluckyPlayer, NormalPlayer
from board import Board
from utils import roll_two_dice, random_other_type
class GameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Forty-Square Board Game")
        self.board = Board()
        self.players = []
        self.current_idx = 0
        self.total_moves = 0
        self.game_over = False
        self.setup_window()
    def setup_window(self):
        # Setup frame for player configuration
        self.setup_win = tk.Toplevel(self.root)
        self.setup_win.title("Game Setup")
        self.setup_win.grab_set()
        tk.Label(self.setup_win, text="Number of players (2-6):").grid(row=0, column=0, sticky="w")
        self.num_players_var = tk.IntVar(value=2)
        num_spin = tk.Spinbox(self.setup_win, from_=2, to=6, textvariable=self.num_players_var, width=5, command=self.render_player_rows)
        num_spin.grid(row=0, column=1, sticky="w")
        self.player_rows_frame = tk.Frame(self.setup_win)
        self.player_rows_frame.grid(row=1, column=0, columnspan=3, pady=5)
        self.player_name_vars = []
        self.player_type_vars = []
        self.render_player_rows()
        start_btn = tk.Button(self.setup_win, text="Start Game", command=self.start_game)
        start_btn.grid(row=10, column=0, pady=5)
        cancel_btn = tk.Button(self.setup_win, text="Cancel", command=self.root.quit)
        cancel_btn.grid(row=10, column=1, pady=5)
    def render_player_rows(self):
        for widget in self.player_rows_frame.winfo_children():
            widget.destroy()
        self.player_name_vars = []
        self.player_type_vars = []
        n = self.num_players_var.get()
        options = ["normal", "lucky", "unlucky"]
        for i in range(n):
            tk.Label(self.player_rows_frame, text=f"Player {i+1} Name:").grid(row=i, column=0, sticky="w")
            name_var = tk.StringVar(value=f"P{i+1}")
            tk.Entry(self.player_rows_frame, textvariable=name_var, width=12).grid(row=i, column=1, sticky="w")
            tk.Label(self.player_rows_frame, text="Type:").grid(row=i, column=2, sticky="w")
            type_var = tk.StringVar(value=options[i % 3])
            ttk.Combobox(self.player_rows_frame, textvariable=type_var, values=options, width=10, state="readonly").grid(row=i, column=3, sticky="w")
            self.player_name_vars.append(name_var)
            self.player_type_vars.append(type_var)
    def start_game(self):
        # Build players from config
        types_present = set()
        self.players = []
        for name_var, type_var in zip(self.player_name_vars, self.player_type_vars):
            name = name_var.get().strip() or "Player"
            ptype = type_var.get()
            types_present.add(ptype)
            if ptype == "normal":
                p = NormalPlayer(name)
            elif ptype == "lucky":
                p = LuckyPlayer(name)
            elif ptype == "unlucky":
                p = UnluckyPlayer(name)
            else:
                p = NormalPlayer(name)
            self.players.append(p)
        if len(types_present) < 2:
            messagebox.showerror("Invalid Setup", "Please select at least two different player types.")
            return
        # Setup complete
        self.setup_win.destroy()
        self.build_main_ui()
        self.update_ui()
    def build_main_ui(self):
        # Top frame: board representation (simple)
        board_frame = tk.Frame(self.root)
        board_frame.pack(padx=5, pady=5, fill="x")
        self.square_labels = []
        for i in range(0, self.board.size + 1):
            lbl = tk.Label(board_frame, text=str(i), borderwidth=1, relief="ridge", width=4)
            lbl.grid(row=0, column=i, padx=1, pady=1)
            self.square_labels.append(lbl)
        # Middle frame: player status
        status_frame = tk.Frame(self.root)
        status_frame.pack(padx=5, pady=5, fill="x")
        tk.Label(status_frame, text="Players:").grid(row=0, column=0, sticky="w")
        self.players_text = tk.Text(status_frame, height=6, width=60, state="disabled")
        self.players_text.grid(row=1, column=0, columnspan=4)
        # Right frame: controls and info
        control_frame = tk.Frame(self.root)
        control_frame.pack(padx=5, pady=5, fill="x")
        self.turn_label = tk.Label(control_frame, text="Turn: ")
        self.turn_label.grid(row=0, column=0, sticky="w")
        self.dice_label = tk.Label(control_frame, text="Dice: ")
        self.dice_label.grid(row=1, column=0, sticky="w")
        self.roll_btn = tk.Button(control_frame, text="Roll Dice", command=self.on_roll)
        self.roll_btn.grid(row=2, column=0, pady=3)
        self.debug_var = tk.BooleanVar(value=False)
        self.debug_check = tk.Checkbutton(control_frame, text="Debug mode (input dest)", variable=self.debug_var, command=self.on_debug_toggle)
        self.debug_check.grid(row=3, column=0, sticky="w")
        tk.Label(control_frame, text="Destination:").grid(row=4, column=0, sticky="w")
        self.dest_entry = tk.Entry(control_frame, width=6)
        self.dest_entry.grid(row=4, column=1, sticky="w")
        self.dest_entry.config(state="disabled")
        self.set_dest_btn = tk.Button(control_frame, text="Set Destination", command=self.on_set_destination, state="disabled")
        self.set_dest_btn.grid(row=5, column=0, pady=3)
        # Message log
        tk.Label(self.root, text="Messages:").pack(anchor="w")
        self.msg_text = tk.Text(self.root, height=8, width=100, state="disabled")
        self.msg_text.pack(padx=5, pady=5)
    def log(self, msg):
        self.msg_text.config(state="normal")
        self.msg_text.insert("end", msg + "\n")
        self.msg_text.see("end")
        self.msg_text.config(state="disabled")
    def update_ui(self):
        # Update board labels to show players on squares
        # Reset board labels to their square indices and default background
        default_bg = self.root.cget("bg")  # platform default background
        for idx, lbl in enumerate(self.square_labels):
            lbl.config(bg=default_bg, text=str(idx))
        # Mark players on board: show initials
        positions_map = {}
        for p in self.players:
            pos = min(p.position, self.board.size)
            positions_map.setdefault(pos, []).append(p.name)
        for pos, names in positions_map.items():
            display = f"{pos}\n" + ",".join([n for n in names])
            self.square_labels[pos].config(text=display, bg="#e6f7ff")
        # Update players text
        self.players_text.config(state="normal")
        self.players_text.delete("1.0", "end")
        for i, p in enumerate(self.players):
            skip = " (skip next)" if p.skip_next_turn else ""
            self.players_text.insert("end", f"{i+1}. {p.name} [{p.ptype}] - Pos: {p.position}{skip} - Moves: {p.move_count}\n")
        self.players_text.config(state="disabled")
        if not self.game_over:
            current = self.players[self.current_idx]
            self.turn_label.config(text=f"Turn: {current.name} [{current.ptype}]")
        else:
            self.turn_label.config(text="Game Over")
    def on_debug_toggle(self):
        if self.debug_var.get():
            self.dest_entry.config(state="normal")
            self.set_dest_btn.config(state="normal")
            self.roll_btn.config(state="disabled")
        else:
            self.dest_entry.config(state="disabled")
            self.set_dest_btn.config(state="disabled")
            self.roll_btn.config(state="normal")
    def on_roll(self):
        if self.game_over:
            return
        current = self.players[self.current_idx]
        # Check skip turn
        if current.skip_next_turn:
            self.log(f"{current.name} misses this turn.")
            current.skip_next_turn = False
            self.advance_turn()
            return
        d1, d2 = current.roll_dice()
        dice_sum = d1 + d2
        self.dice_label.config(text=f"Dice: {d1} + {d2} = {dice_sum}")
        self.total_moves += 1
        current.move_count += 1
        self.log(f"{current.name} rolled {d1} and {d2} (sum {dice_sum}).")
        # Move player
        current.move_by(dice_sum)
        self.log(f"{current.name} moves to {current.position}.")
        # Apply square effects (this function now resolves chained effects and returns final player instance if type changed)
        new_player, messages = self.board.apply_square_effect(current, self.players)
        # Handle player type change (may return a new player instance)
        if new_player is not None:
            # Replace current in players list
            self.players[self.current_idx] = new_player
            current = new_player
            self.log(f"{current.name} is now of type [{current.ptype}].")
        for m in messages:
            self.log(m)
        # Check win after all chained effects are resolved
        if current.position >= self.board.size:
            self.end_game(winner=current)
            return
        self.update_ui()
        # Bonus turn for doubles
        if d1 == d2:
            self.log(f"{current.name} rolled doubles and gets a bonus turn!")
            # Do NOT advance turn; bonus turn occurs.
            return
        else:
            self.advance_turn()
    def on_set_destination(self):
        # Debug mode: let user set position directly
        if self.game_over:
            return
        try:
            dest = int(self.dest_entry.get())
        except ValueError:
            messagebox.showerror("Invalid input", "Please enter an integer destination square.")
            return
        if dest < 0:
            messagebox.showerror("Invalid input", "Destination cannot be negative.")
            return
        current = self.players[self.current_idx]
        # Check skip turn
        if current.skip_next_turn:
            self.log(f"{current.name} misses this turn.")
            current.skip_next_turn = False
            self.advance_turn()
            return
        # Set as move
        self.total_moves += 1
        current.move_count += 1
        old_pos = current.position
        current.position = dest
        self.dice_label.config(text=f"Debug dest set to {dest}")
        self.log(f"{current.name} (debug) moved from {old_pos} to {current.position}.")
        # Apply square effects for the destination square (resolves chained effects)
        new_player, messages = self.board.apply_square_effect(current, self.players)
        if new_player is not None:
            self.players[self.current_idx] = new_player
            current = new_player
            self.log(f"{current.name} is now of type [{current.ptype}].")
        for m in messages:
            self.log(m)
        # Check win
        if current.position >= self.board.size:
            self.end_game(winner=current)
            return
        self.update_ui()
        # Debug move does not grant bonus turns; advance
        self.advance_turn()
    def advance_turn(self):
        # Advance current_idx to next player who exists
        n = len(self.players)
        self.current_idx = (self.current_idx + 1) % n
        self.update_ui()
    def end_game(self, winner):
        self.game_over = True
        self.update_ui()
        self.log(f"*** {winner.name} wins by reaching {winner.position}! ***")
        self.log(f"Total moves: {self.total_moves}")
        self.log("Final positions:")
        for p in self.players:
            self.log(f"- {p.name} [{p.ptype}] at {p.position} (Moves: {p.move_count})")
        msg = f"Winner: {winner.name}\nTotal moves: {self.total_moves}\n\nFinal positions:\n"
        for p in self.players:
            msg += f"{p.name} [{p.ptype}] - {p.position}\n"
        messagebox.showinfo("Game Over", msg)
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide main until setup finishes
    app = GameGUI(root)
    root.deiconify()
    root.mainloop()