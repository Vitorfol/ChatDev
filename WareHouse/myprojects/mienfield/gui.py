'''
Graphical User Interface for the Minesweeper game using tkinter.
Provides a start/settings screen to select rows, columns, bombs, and difficulty,
and the main game board with mouse interactions (left-click reveal, right-click flag).
Enhancements:
- Scrollable board using a Canvas and scrollbars so large boards (e.g., 30x30) remain usable.
- Spinbox limits for bombs synchronized with rows/columns.
- Tracking when the user manually modifies the bombs value to avoid overwriting their choice.
- Minor robustness around programmatic vs user changes to variables.
- Fixed color names to use hex codes and safe configuration to avoid TclError on some platforms.
'''
import tkinter as tk
from tkinter import ttk, messagebox
import time
from game import Minefield
from config import DIFFICULTY_PRESETS
# Centralized color/map constants using hex codes (portable across Tk implementations)
NUM_COLOR_MAP = {
    1: "#0000FF",  # blue
    2: "#008000",  # green
    3: "#FF0000",  # red
    4: "#00008B",  # darkblue
    5: "#A52A2A",  # brown
    6: "#40E0D0",  # turquoise
    7: "#000000",  # black
    8: "#808080",  # gray
}
BOMB_BG = "#FF4500"       # orange-red
FLAG_FG = "#FF0000"       # red for flag
EXPLODED_BG = "#FF0000"   # red for exploded cell
BUTTON_BG = "#D3D3D3"     # lightgray fallback
BUTTON_REVEALED_BG = "#FFFFFF"  # white
BUTTON_TEXT_FG = "#000000"      # black
# Emojis and textual fallbacks (some environments may not render emojis; textual fallback used on failure)
BOMB_EMOJI = "💣"
FLAG_EMOJI = "🚩"
EXPLODE_EMOJI = "💥"
BOMB_TEXT = "B"
FLAG_TEXT = "F"
EXPLODE_TEXT = "X"
class MinesweeperGUI:
    def __init__(self, root):
        self.root = root
        self.root.resizable(False, False)
        self.main_frame = ttk.Frame(root, padding=10)
        self.main_frame.grid()
        self.game = None
        self.buttons = {}
        self.timer_job = None
        self.start_time = None
        self.elapsed = 0
        # Flags to manage when bombs_var is being set programmatically vs by the user.
        self.bombs_user_modified = False
        self._setting_bombs_programmatically = False
        self.build_start_screen()
    def build_start_screen(self):
        # Garantir estado limpo ao (re)construir a tela de início:
        self.bombs_user_modified = False
        self._setting_bombs_programmatically = False
        # Clear frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        title = ttk.Label(self.main_frame, text="Campo Minado", font=("TkDefaultFont", 16, "bold"))
        title.grid(row=0, column=0, columnspan=3, pady=(0,10))
        # Rows
        ttk.Label(self.main_frame, text="Linhas:").grid(row=1, column=0, sticky="e")
        self.rows_var = tk.IntVar(value=9)
        self.rows_spin = ttk.Spinbox(self.main_frame, from_=5, to=30, textvariable=self.rows_var, width=6)
        self.rows_spin.grid(row=1, column=1, sticky="w")
        # Columns
        ttk.Label(self.main_frame, text="Colunas:").grid(row=2, column=0, sticky="e")
        self.cols_var = tk.IntVar(value=9)
        self.cols_spin = ttk.Spinbox(self.main_frame, from_=5, to=30, textvariable=self.cols_var, width=6)
        self.cols_spin.grid(row=2, column=1, sticky="w")
        # Bombs
        ttk.Label(self.main_frame, text="Bombas:").grid(row=3, column=0, sticky="e")
        self.bombs_var = tk.IntVar(value=10)
        max_bombs_initial = max(1, self.rows_var.get()*self.cols_var.get() - 1)
        self.bombs_spin = ttk.Spinbox(self.main_frame, from_=1, to=max_bombs_initial, textvariable=self.bombs_var, width=8)
        self.bombs_spin.grid(row=3, column=1, sticky="w")
        # Difficulty
        ttk.Label(self.main_frame, text="Dificuldade:").grid(row=4, column=0, sticky="e")
        self.difficulty_var = tk.StringVar(value="Medium")
        self.diff_combo = ttk.Combobox(self.main_frame, textvariable=self.difficulty_var, values=list(DIFFICULTY_PRESETS.keys()), state="readonly", width=10)
        self.diff_combo.grid(row=4, column=1, sticky="w")
        self.diff_combo.bind("<<ComboboxSelected>>", self.on_difficulty_change)
        # Info label
        self.info_label = ttk.Label(self.main_frame, text="Escolha as configurações e clique em Iniciar")
        self.info_label.grid(row=5, column=0, columnspan=3, pady=(8,8))
        # Buttons
        start_btn = ttk.Button(self.main_frame, text="Iniciar", command=self.start_game)
        start_btn.grid(row=6, column=0, pady=(4,0))
        quit_btn = ttk.Button(self.main_frame, text="Sair", command=self.root.quit)
        quit_btn.grid(row=6, column=1, pady=(4,0))
        # Traces to keep spins in sync and detect user edits
        # When rows/cols change update bombs spin maximum and validations
        self.rows_var.trace_add("write", self.on_board_size_change)
        self.cols_var.trace_add("write", self.on_board_size_change)
        # Detect user modification to bombs. Use programmatic flag to avoid marking when we set it from code.
        self.bombs_var.trace_add("write", self._bombs_var_written)
        # Apply default difficulty influence (this uses programmatic set to avoid marking as user change)
        self.on_difficulty_change()
    def _bombs_var_written(self, *args):
        # Called whenever bombs_var changes. If the change was programmatic, ignore. Otherwise mark as user-changed.
        if self._setting_bombs_programmatically:
            return
        # If we get here, a user (or external non-flagged action) changed bombs
        self.bombs_user_modified = True
    def on_board_size_change(self, *args):
        # Called when rows or cols change; update maximum bombs limit and ensure current value is valid.
        try:
            rows = int(self.rows_var.get())
            cols = int(self.cols_var.get())
        except Exception:
            return
        # Clamp rows/cols to allowed bounds
        rows = max(5, min(30, rows))
        cols = max(5, min(30, cols))
        # Ensure variables reflect clamped values (silently programmatic set)
        # Use programmatic flag to avoid marking as user edit
        self._setting_bombs_programmatically = True
        self.rows_var.set(rows)
        self.cols_var.set(cols)
        self._setting_bombs_programmatically = False
        max_bombs = max(1, rows * cols - 1)
        # Update spinbox max limit
        try:
            self.bombs_spin.config(to=max_bombs)
        except Exception:
            # Some tkinter versions or themed widgets may not support config('to'); ignore if so.
            pass
        # Validate current bombs value
        current = None
        try:
            current = int(self.bombs_var.get())
        except Exception:
            current = 1
        if current > max_bombs or current < 1:
            # If user already modified bombs manually, clamp to valid range but keep "user modified" flag true.
            self._setting_bombs_programmatically = True
            self.bombs_var.set(max_bombs if current > max_bombs else 1)
            self._setting_bombs_programmatically = False
            # If this change was necessary because user's value was invalid we keep bombs_user_modified as-is
        # Optionally we could update the info label to reflect new board size
        self.info_label.config(text=f"Tamanho do tabuleiro: {rows}x{cols}")
    def on_difficulty_change(self, event=None):
        diff = self.difficulty_var.get()
        preset = DIFFICULTY_PRESETS.get(diff, {})
        rows = self.rows_var.get()
        cols = self.cols_var.get()
        suggested_fraction = preset.get("suggest_fraction", 0.15)
        suggested = max(1, int(rows * cols * suggested_fraction))
        # Update bombs spin maximum
        max_bombs = max(1, rows * cols - 1)
        try:
            self.bombs_spin.config(to=max_bombs)
        except Exception:
            pass
        # Only overwrite the bombs setting if the user hasn't manually changed it.
        if not self.bombs_user_modified:
            self._setting_bombs_programmatically = True
            # Ensure suggested doesn't exceed max_bombs
            self.bombs_var.set(min(suggested, max_bombs))
            self._setting_bombs_programmatically = False
        else:
            # If user already modified but their value is invalid for the current board size, clamp it.
            current = self.bombs_var.get()
            if current > max_bombs:
                self._setting_bombs_programmatically = True
                self.bombs_var.set(max_bombs)
                self._setting_bombs_programmatically = False
        self.info_label.config(text=f"Dificuldade {diff}: {'Segurança no primeiro clique' if preset.get('first_click_safe') else 'Sem garantia no primeiro clique'}")
    def start_game(self):
        try:
            rows = int(self.rows_var.get())
            cols = int(self.cols_var.get())
            bombs = int(self.bombs_var.get())
        except Exception:
            messagebox.showerror("Erro", "Linhas, colunas e bombas devem ser números inteiros.")
            return
        max_cells = rows * cols
        if rows < 5 or cols < 5 or rows > 30 or cols > 30:
            messagebox.showerror("Erro", "Linhas e colunas devem estar entre 5 e 30.")
            return
        if bombs < 1 or bombs >= max_cells:
            messagebox.showerror("Erro", f"Bombas devem estar entre 1 e {max_cells-1}.")
            return
        diff = self.difficulty_var.get()
        preset = DIFFICULTY_PRESETS.get(diff, {})
        first_click_safe = preset.get("first_click_safe", True)
        # Initialize game
        self.game = Minefield(rows, cols, bombs, first_click_safe=first_click_safe)
        # Build the game UI
        self.build_game_ui()
    def build_game_ui(self):
        # Clear frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        top_frame = ttk.Frame(self.main_frame)
        top_frame.grid(row=0, column=0, columnspan=2, sticky="w")
        self.mines_label = ttk.Label(top_frame, text=f"Bombas restantes: {0 if not self.game else self.game.remaining_flags()}")
        self.mines_label.grid(row=0, column=0, padx=(0,10))
        self.timer_label = ttk.Label(top_frame, text="Tempo: 0s")
        self.timer_label.grid(row=0, column=1, padx=(0,10))
        restart_btn = ttk.Button(top_frame, text="Reiniciar", command=self.restart)
        restart_btn.grid(row=0, column=2, padx=(0,10))
        back_btn = ttk.Button(top_frame, text="Voltar", command=self.build_start_screen)
        back_btn.grid(row=0, column=3, padx=(0,10))
        # Create a canvas + scrollbars to contain the board so large boards remain usable on small screens.
        board_container = ttk.Frame(self.main_frame)
        board_container.grid(row=1, column=0, sticky="nsew")
        # Canvas
        board_canvas = tk.Canvas(board_container, borderwidth=0, highlightthickness=0)
        board_canvas.grid(row=0, column=0, sticky="nsew")
        # Scrollbars
        v_scroll = ttk.Scrollbar(board_container, orient="vertical", command=board_canvas.yview)
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll = ttk.Scrollbar(board_container, orient="horizontal", command=board_canvas.xview)
        h_scroll.grid(row=1, column=0, sticky="ew")
        board_canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        # Inner frame inside canvas where buttons will be placed
        inner_frame = ttk.Frame(board_canvas)
        # Create window
        board_canvas.create_window((0,0), window=inner_frame, anchor="nw")
        # Update scrollregion when inner_frame changes size
        def on_inner_configure(event):
            board_canvas.configure(scrollregion=board_canvas.bbox("all"))
        inner_frame.bind("<Configure>", on_inner_configure)
        # Allow the container to expand if desired (keeps layout stable)
        board_container.rowconfigure(0, weight=1)
        board_container.columnconfigure(0, weight=1)
        self.buttons = {}
        # Create buttons inside inner_frame
        for r in range(self.game.rows):
            for c in range(self.game.cols):
                # Keep buttons compact for performance on larger boards
                btn = tk.Button(inner_frame, width=2, height=1, relief="raised", bg=BUTTON_BG, font=("TkDefaultFont", 9, "bold"))
                btn.grid(row=r, column=c, padx=0, pady=0, sticky="nsew")
                # Bind left and right click. We'll use lambdas capturing r,c
                btn.bind("<Button-1>", lambda e, rr=r, cc=c: self.on_left_click(rr, cc))
                # Bind both Button-2 and Button-3 for right click compatibility
                btn.bind("<Button-3>", lambda e, rr=r, cc=c: self.on_right_click(rr, cc))
                btn.bind("<Button-2>", lambda e, rr=r, cc=c: self.on_right_click(rr, cc))
                self.buttons[(r,c)] = btn
        # Reset timer values
        self.start_time = None
        self.elapsed = 0
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None
        self.update_timer()
        self.update_all_buttons()
        # Ensure initial scrollregion is correct
        board_canvas.update_idletasks()
        board_canvas.configure(scrollregion=board_canvas.bbox("all"))
    def _safe_config(self, btn, **kwargs):
        """
        Try to apply btn.config safely. If an exception occurs (e.g. invalid color name on some TK implementations),
        attempt a minimal, safe fallback configuration (text-only and standard color names).
        """
        try:
            btn.config(**kwargs)
            return
        except Exception:
            # Build a reduced fallback set
            fallback = {}
            # Map emojis to textual fallbacks if necessary
            text_val = kwargs.get("text")
            if text_val is not None:
                if text_val == BOMB_EMOJI:
                    fallback["text"] = BOMB_TEXT
                elif text_val == FLAG_EMOJI:
                    fallback["text"] = FLAG_TEXT
                elif text_val == EXPLODE_EMOJI:
                    fallback["text"] = EXPLODE_TEXT
                else:
                    fallback["text"] = text_val
            # Safe bg/fg choices: prefer known-safe color names if hex fails
            if "bg" in kwargs:
                # prefer hex from kwargs; but if that causes errors, fall back to a basic name
                fallback["bg"] = kwargs.get("bg", None) or BUTTON_BG
            if "fg" in kwargs:
                fallback["fg"] = kwargs.get("fg", None) or BUTTON_TEXT_FG
            # state/relief should be safe mostly
            if "state" in kwargs:
                fallback["state"] = kwargs["state"]
            if "relief" in kwargs:
                fallback["relief"] = kwargs["relief"]
            try:
                # Remove None entries
                fallback = {k: v for k, v in fallback.items() if v is not None}
                if fallback:
                    btn.config(**fallback)
            except Exception:
                # Last-resort: try to only set text
                try:
                    if "text" in fallback:
                        btn.config(text=fallback["text"])
                except Exception:
                    # give up silently to avoid crashing GUI
                    pass
    def on_left_click(self, r, c):
        if self.game is None:
            return
        if self.start_time is None:
            # Start timer on first user action
            self.start_time = time.time()
        if self.game.is_flagged(r, c) or self.game.is_revealed(r, c):
            # Optional: chord behavior if revealed and number equals flags around -> reveal neighbors
            if self.game.is_revealed(r, c):
                count = self.game.get_count(r, c)
                if count > 0:
                    # count flags around
                    flagged = 0
                    neigh = []
                    for nr, nc in self.game.neighbors(r, c):
                        if self.game.is_flagged(nr, nc):
                            flagged += 1
                        else:
                            neigh.append((nr, nc))
                    if flagged == count:
                        # reveal neighbors
                        for nr, nc in neigh:
                            result = self.game.reveal(nr, nc)
                            if result == "bomb":
                                self.update_all_buttons()
                                self.end_game(win=False, exploded=(nr, nc))
                                return
            return
        result = self.game.reveal(r, c)
        if result == "bomb":
            # exploded
            self.update_all_buttons()
            self.end_game(win=False, exploded=(r, c))
            return
        self.update_all_buttons()
        if self.game.is_won():
            self.update_all_buttons()
            self.end_game(win=True)
    def on_right_click(self, r, c):
        if self.game is None:
            return
        if self.start_time is None:
            self.start_time = time.time()
        if self.game.is_revealed(r, c):
            return
        self.game.toggle_flag(r, c)
        self.mines_label.config(text=f"Bombas restantes: {self.game.remaining_flags()}")
        self.update_cell_button(r, c)
        if self.game.is_won():
            self.end_game(win=True)
    def update_cell_button(self, r, c):
        btn = self.buttons.get((r,c))
        if btn is None:
            return
        if self.game.is_revealed(r, c):
            # Revealed look
            try:
                btn.config(relief="sunken", state="disabled", bg=BUTTON_REVEALED_BG, fg=BUTTON_TEXT_FG)
            except Exception:
                # If config fails, try safe fallback
                self._safe_config(btn, relief="sunken", state="disabled", bg=BUTTON_REVEALED_BG, fg=BUTTON_TEXT_FG)
            if self.game.get_mine(r, c):
                # Show mine
                try:
                    self._safe_config(btn, text=BOMB_EMOJI, bg=BOMB_BG, fg=BUTTON_TEXT_FG)
                except Exception:
                    self._safe_config(btn, text=BOMB_TEXT, bg="red", fg=BUTTON_TEXT_FG)
            else:
                cnt = self.game.get_count(r, c)
                text_to_show = str(cnt) if cnt > 0 else ""
                # Set number and color if applicable
                try:
                    if cnt in NUM_COLOR_MAP:
                        self._safe_config(btn, text=text_to_show, fg=NUM_COLOR_MAP[cnt], bg=BUTTON_REVEALED_BG)
                    else:
                        self._safe_config(btn, text=text_to_show, fg=BUTTON_TEXT_FG, bg=BUTTON_REVEALED_BG)
                except Exception:
                    # fallback to simple text
                    self._safe_config(btn, text=text_to_show, fg=BUTTON_TEXT_FG, bg=BUTTON_REVEALED_BG)
        else:
            # Hidden look
            if self.game.is_flagged(r, c):
                try:
                    self._safe_config(btn, text=FLAG_EMOJI, fg=FLAG_FG, bg=BUTTON_BG, relief="raised", state="normal")
                except Exception:
                    self._safe_config(btn, text=FLAG_TEXT, fg="red", bg=BUTTON_BG, relief="raised", state="normal")
            else:
                try:
                    self._safe_config(btn, text="", fg=BUTTON_TEXT_FG, bg=BUTTON_BG, relief="raised", state="normal")
                except Exception:
                    self._safe_config(btn, text="", fg=BUTTON_TEXT_FG, bg=BUTTON_BG, relief="raised", state="normal")
    def update_all_buttons(self):
        for (r,c), btn in self.buttons.items():
            self.update_cell_button(r, c)
        self.mines_label.config(text=f"Bombas restantes: {self.game.remaining_flags()}")
    def end_game(self, win, exploded=None):
        # Stop timer
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None
        # Reveal all mines
        self.game.reveal_all_mines()
        self.update_all_buttons()
        # Highlight exploded cell if any
        if exploded:
            r, c = exploded
            btn = self.buttons.get((r,c))
            if btn:
                try:
                    self._safe_config(btn, bg=EXPLODED_BG, text=EXPLODE_EMOJI, fg=BUTTON_TEXT_FG)
                except Exception:
                    self._safe_config(btn, bg="red", text=EXPLODE_TEXT, fg=BUTTON_TEXT_FG)
        if win:
            messagebox.showinfo("Parabéns!", f"Você ganhou! Tempo: {self.elapsed} segundos")
        else:
            messagebox.showinfo("Fim de jogo", "Você perdeu! Tente novamente.")
        # Disable all buttons to prevent further interaction
        for btn in self.buttons.values():
            try:
                btn.config(state="disabled")
            except Exception:
                try:
                    btn.configure(state="disabled")
                except Exception:
                    pass
    def update_timer(self):
        if self.start_time:
            self.elapsed = int(time.time() - self.start_time)
            self.timer_label.config(text=f"Tempo: {self.elapsed}s")
        else:
            self.timer_label.config(text=f"Tempo: {self.elapsed}s")
        # schedule next update
        self.timer_job = self.root.after(1000, self.update_timer)
    def restart(self):
        # Simply rebuild the same game settings
        if not self.game:
            return
        rows = self.game.rows
        cols = self.game.cols
        bombs = self.game.bombs
        first_click_safe = self.game.first_click_safe
        self.game = Minefield(rows, cols, bombs, first_click_safe=first_click_safe)
        # Reset UI
        for (r,c), btn in self.buttons.items():
            try:
                btn.config(relief="raised", state="normal", bg=BUTTON_BG, text="", fg=BUTTON_TEXT_FG)
            except Exception:
                self._safe_config(btn, relief="raised", state="normal", bg=BUTTON_BG, text="", fg=BUTTON_TEXT_FG)
        self.start_time = None
        self.elapsed = 0
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None
        self.update_timer()
        self.mines_label.config(text=f"Bombas restantes: {self.game.remaining_flags()}")