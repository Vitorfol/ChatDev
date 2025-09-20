'''
Tkinter-based GUI for the Robot-Food simulation.
Provides controls for user-controlled and automatic simulations,
draws a 4x4 board, displays robots, food, obstacles, and logs.
'''
import tkinter as tk
from tkinter import ttk, messagebox
import random
from game import Game, DIRS, DIR_NAMES
from models import Robo, RoboInteligente, Bomb, Rock
CELL_SIZE = 100
GRID = 4
PADDING = 10
class RobotApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Robot-Food Simulation (4x4)")
        self.game = None
        self.canvas = None
        self.info_text = None
        self.controls_frame = None
        self.selected_robot = None
        self.delay_ms = tk.IntVar(value=300)
        self.intelligent_var = tk.BooleanVar(value=False)
        self.num_robots = tk.IntVar(value=1)
        self.random_mode = tk.StringVar(value="single")  # 'single' or 'multi'
        self._build_ui()
    def _build_ui(self):
        top = ttk.Frame(self.root, padding=8)
        top.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        # Left: board
        board_frame = ttk.Frame(top)
        board_frame.pack(side=tk.LEFT, padx=8, pady=8)
        self.canvas = tk.Canvas(board_frame, width=CELL_SIZE*GRID, height=CELL_SIZE*GRID, bg="white")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        # Right: controls and log
        right = ttk.Frame(top, width=300)
        right.pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=8)
        # Options
        opts = ttk.LabelFrame(right, text="Options", padding=6)
        opts.pack(fill=tk.X, pady=4)
        ttk.Checkbutton(opts, text="Intelligent Robots (RoboInteligente)", variable=self.intelligent_var).pack(anchor=tk.W)
        ttk.Label(opts, text="Number of Robots (multi):").pack(anchor=tk.W, pady=(6,0))
        num_spin = ttk.Spinbox(opts, from_=1, to=4, textvariable=self.num_robots, width=5)
        num_spin.pack(anchor=tk.W)
        ttk.Label(opts, text="Animation delay (ms):").pack(anchor=tk.W, pady=(6,0))
        ttk.Scale(opts, from_=0, to=1000, variable=self.delay_ms, orient=tk.HORIZONTAL).pack(fill=tk.X)
        # Mode buttons
        mode = ttk.LabelFrame(right, text="Modes", padding=6)
        mode.pack(fill=tk.X, pady=4)
        ttk.Button(mode, text="User-controlled (Single Robot)", command=self.start_user_controlled).pack(fill=tk.X, pady=2)
        ttk.Button(mode, text="Random Single Robot", command=self.start_random_single).pack(fill=tk.X, pady=2)
        ttk.Button(mode, text="Random Multiple Robots", command=self.start_random_multi).pack(fill=tk.X, pady=2)
        # Movement buttons for user control
        move_frame = ttk.LabelFrame(right, text="Move (User)", padding=6)
        move_frame.pack(fill=tk.X, pady=4)
        btn_up = ttk.Button(move_frame, text="↑ Up", command=lambda: self.on_move_cmd("UP"))
        btn_up.pack(fill=tk.X, pady=2)
        btn_left = ttk.Button(move_frame, text="← Left", command=lambda: self.on_move_cmd("LEFT"))
        btn_left.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,4))
        btn_right = ttk.Button(move_frame, text="Right →", command=lambda: self.on_move_cmd("RIGHT"))
        btn_right.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(4,0))
        btn_down = ttk.Button(move_frame, text="↓ Down", command=lambda: self.on_move_cmd("DOWN"))
        btn_down.pack(fill=tk.X, pady=(6,2))
        # Action buttons
        acts = ttk.Frame(right)
        acts.pack(fill=tk.X, pady=4)
        ttk.Button(acts, text="Reset Board", command=self.reset_board).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        ttk.Button(acts, text="Step Random Move", command=self.step_random_move).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        # Log
        log_frame = ttk.LabelFrame(self.root, text="Log", padding=6)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0,8))
        self.info_text = tk.Text(log_frame, height=12, state=tk.DISABLED, wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        # Key bindings
        self.root.bind("<Up>", lambda e: self.on_move_cmd("UP"))
        self.root.bind("<Down>", lambda e: self.on_move_cmd("DOWN"))
        self.root.bind("<Left>", lambda e: self.on_move_cmd("LEFT"))
        self.root.bind("<Right>", lambda e: self.on_move_cmd("RIGHT"))
        self.reset_board()
    def log(self, *parts):
        text = " ".join(str(p) for p in parts)
        self.info_text.configure(state=tk.NORMAL)
        self.info_text.insert(tk.END, text + "\n")
        self.info_text.see(tk.END)
        self.info_text.configure(state=tk.DISABLED)
    def on_canvas_click(self, event):
        # Determine clicked cell -> select robot if present
        col = event.x // CELL_SIZE
        row = event.y // CELL_SIZE
        if not (0 <= row < GRID and 0 <= col < GRID):
            return
        found = None
        for r in (self.game.robots if self.game else []):
            if r.x == row and r.y == col and not r.exploded:
                found = r
                break
        if found:
            self.selected_robot = found
            self.log(f"Selected robot {found.id}")
            self.draw()
        else:
            self.selected_robot = None
            self.log("No robot at clicked cell")
    def _first_free_cell(self):
        """Return first cell (row,col) that has no obstacle and no living robot."""
        for r in range(GRID):
            for c in range(GRID):
                if (r, c) in self.game.obstacles:
                    continue
                occupied = False
                for rob in self.game.robots:
                    if not rob.exploded and rob.x == r and rob.y == c:
                        occupied = True
                        break
                if occupied:
                    continue
                return (r, c)
        # If all cells have obstacles or robots (unlikely), return (0,0)
        return (0, 0)
    def reset_board(self):
        self.game = Game(size=GRID)
        # Place food at random location not (0,0) (but allow anywhere)
        fx, fy = random.choice([(r, c) for r in range(GRID) for c in range(GRID)])
        self.game.place_food(fx, fy)
        # Place some obstacles fixed or random
        # For determinism keep fixed obstacles unless random started
        # Place one bomb and one rock at different positions not food
        positions = [(r, c) for r in range(GRID) for c in range(GRID) if (r, c) != (fx, fy)]
        random.shuffle(positions)
        bpos = positions.pop()
        rpos = positions.pop()
        # Ensure we don't accidentally place robot start on obstacle later by leaving some space.
        self.game.place_obstacle(bpos[0], bpos[1], Bomb())
        self.game.place_obstacle(rpos[0], rpos[1], Rock())
        self.log("Board reset")
        self.selected_robot = None
        self.draw()
    def start_user_controlled(self):
        self.reset_board()
        # Single robot starting at top-left (0,0) unless occupied; find a free cell
        robot_cls = RoboInteligente if self.intelligent_var.get() else Robo
        sx, sy = (0, 0)
        if (sx, sy) in self.game.obstacles:
            sx, sy = self._first_free_cell()
        r = robot_cls(id=1, x=sx, y=sy, color="blue")
        try:
            self.game.add_robot(r)
        except Exception as e:
            self.log(f"Failed to add robot: {e}")
            return
        self.selected_robot = r
        self.log("User-controlled mode. Use arrow keys or buttons to move the selected robot.")
        self.draw()
    def start_random_single(self):
        self.reset_board()
        robot_cls = RoboInteligente if self.intelligent_var.get() else Robo
        sx, sy = (0, 0)
        if (sx, sy) in self.game.obstacles:
            sx, sy = self._first_free_cell()
        r = robot_cls(id=1, x=sx, y=sy, color="purple")
        try:
            self.game.add_robot(r)
        except Exception as e:
            self.log(f"Failed to add robot: {e}")
            return
        self.log("Starting random single-robot simulation")
        self.draw()
        self.root.after(200, lambda: self._run_random([r]))
    def start_random_multi(self):
        self.reset_board()
        count = max(1, min(4, self.num_robots.get()))
        robot_cls = RoboInteligente if self.intelligent_var.get() else Robo
        colors = ["blue", "red", "green", "orange"]
        # Place robots in different corners, but if an obstacle is at a corner pick next free
        starts = [(0,0),(0,3),(3,0),(3,3)]
        for i in range(count):
            sx, sy = starts[i]
            if (sx, sy) in self.game.obstacles:
                sx, sy = self._first_free_cell()
            r = robot_cls(id=i+1, x=sx, y=sy, color=colors[i])
            try:
                self.game.add_robot(r)
            except Exception as e:
                self.log(f"Failed to add robot {i+1}: {e}")
                continue
        self.log(f"Starting random multi-robot simulation with {count} robots")
        self.draw()
        self.root.after(200, lambda: self._run_random(self.game.robots.copy()))
    def _run_random(self, robots):
        # Continue moves until food found or all robots exploded or user interrupts
        if self.game.found_food:
            self.log("Simulation ended: Food already found.")
            return
        active = [r for r in robots if not r.exploded and not self.game.found_food]
        if not active:
            self.log("Simulation ended: No active robots.")
            return
        # Each robot makes one move (random) per round
        for r in active:
            if r.exploded or self.game.found_food:
                continue
            # choose a random direction index code using DIR_NAMES values (0..3)
            idx = random.choice(list(DIR_NAMES.values()))
            try:
                # If robot is intelligent it will try alternatives internally
                r.move_code(idx, self.game)
                self.log(f"Robot {r.id} moved to ({r.x},{r.y})")
            except Exception as e:
                self.log(f"Robot {r.id}: {e}")
            # apply interaction and checks are done by move methods / game
            self.draw()
            if self.game.found_food:
                self.log(f"Robot {r.id} found the food! Position: ({r.x},{r.y})")
                break
        # schedule next round if still ongoing
        if not self.game.found_food and any(not r.exploded for r in robots):
            self.root.after(max(50, self.delay_ms.get()), lambda: self._run_random(robots))
        else:
            self.log("Random simulation ended.")
            self.draw()
    def step_random_move(self):
        # Single step across all robots: each chooses one random move
        if not self.game:
            return
        active = [r for r in self.game.robots if not r.exploded and not self.game.found_food]
        if not active:
            self.log("No active robots to step.")
            return
        for r in active:
            idx = random.choice(list(DIR_NAMES.values()))
            try:
                r.move_code(idx, self.game)
                self.log(f"Robot {r.id} moved to ({r.x},{r.y})")
            except Exception as e:
                self.log(f"Robot {r.id}: {e}")
            self.draw()
            if self.game.found_food:
                self.log(f"Robot {r.id} found the food!")
                break
        self.draw()
    def on_move_cmd(self, direction):
        if not self.selected_robot:
            self.log("No robot selected for user control.")
            return
        try:
            # user control uses string movement
            self.selected_robot.move(direction, self.game)
            self.log(f"Robot {self.selected_robot.id} moved to ({self.selected_robot.x},{self.selected_robot.y})")
        except Exception as e:
            self.log(f"Move failed: {e}")
        self.draw()
        if self.game.found_food:
            messagebox.showinfo("Food Found", f"Robot {self.selected_robot.id} found the food!")
    def draw(self):
        self.canvas.delete("all")
        # draw grid
        for i in range(GRID):
            for j in range(GRID):
                x0 = j * CELL_SIZE
                y0 = i * CELL_SIZE
                self.canvas.create_rectangle(x0, y0, x0+CELL_SIZE, y0+CELL_SIZE, outline="black", fill="#f2f2f2")
        # draw obstacles
        for (x,y), obs in self.game.obstacles.items():
            cx = y*CELL_SIZE + CELL_SIZE/2
            cy = x*CELL_SIZE + CELL_SIZE/2
            if isinstance(obs, Bomb):
                self.canvas.create_oval(cx-20, cy-20, cx+20, cy+20, fill="red", outline="black")
                self.canvas.create_text(cx, cy, text="B", fill="white", font=("TkDefaultFont", 14, "bold"))
            elif isinstance(obs, Rock):
                self.canvas.create_rectangle(cx-20, cy-12, cx+20, cy+12, fill="gray", outline="black")
                self.canvas.create_text(cx, cy, text="R", fill="white", font=("TkDefaultFont", 12, "bold"))
        # draw food
        if self.game.food:
            fx, fy = self.game.food
            cx = fy*CELL_SIZE + CELL_SIZE/2
            cy = fx*CELL_SIZE + CELL_SIZE/2
            self.canvas.create_oval(cx-12, cy-12, cx+12, cy+12, fill="green", outline="darkgreen")
        # draw robots
        for r in self.game.robots:
            cx = r.y*CELL_SIZE + CELL_SIZE/2
            cy = r.x*CELL_SIZE + CELL_SIZE/2
            if r.exploded:
                self.canvas.create_text(cx, cy, text="X", font=("TkDefaultFont", 24), fill="black")
            else:
                self.canvas.create_oval(cx-20, cy-20, cx+20, cy+20, fill=r.color, outline="black", width=2)
                self.canvas.create_text(cx, cy, text=str(r.id), fill="white", font=("TkDefaultFont", 12, "bold"))
                if r is self.selected_robot:
                    # highlight
                    self.canvas.create_rectangle(r.y*CELL_SIZE+2, r.x*CELL_SIZE+2, r.y*CELL_SIZE+CELL_SIZE-2, r.x*CELL_SIZE+CELL_SIZE-2, outline="gold", width=3)
        # draw stats in log
        self.log_state()
    def log_state(self):
        # print small summary in log
        lines = []
        for r in self.game.robots:
            status = "exploded" if r.exploded else "alive"
            lines.append(f"Robot {r.id} [{status}] pos=({r.x},{r.y}) valid={r.valid_moves} invalid={r.invalid_moves}")
        # Append summary line only
        if lines:
            self.log(" | ".join(lines))
    def run(self):
        self.root.mainloop()