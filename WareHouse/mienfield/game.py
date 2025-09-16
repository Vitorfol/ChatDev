'''
Game logic for the Minesweeper (Campo Minado).
Implements grid, mine placement (with optional first-click safety), reveal/flag behavior,
and win/loss detection.
'''
import random
from collections import deque
class Minefield:
    def __init__(self, rows, cols, bombs, first_click_safe=True):
        if rows <= 0 or cols <= 0:
            raise ValueError("Rows and columns must be positive integers.")
        max_cells = rows * cols
        if bombs <= 0 or bombs >= max_cells:
            raise ValueError("Bombs must be between 1 and rows*cols - 1.")
        self.rows = rows
        self.cols = cols
        self.bombs = bombs
        self.first_click_safe = first_click_safe
        # Internal state
        self.mines = [[False]*cols for _ in range(rows)]
        self.counts = [[0]*cols for _ in range(rows)]
        self.revealed = [[False]*cols for _ in range(rows)]
        self.flagged = [[False]*cols for _ in range(rows)]
        self.mines_placed = False  # We'll place mines on first reveal if first_click_safe is True
        self.revealed_count = 0
    def in_bounds(self, r, c):
        return 0 <= r < self.rows and 0 <= c < self.cols
    def neighbors(self, r, c):
        for dr in (-1,0,1):
            for dc in (-1,0,1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if self.in_bounds(nr, nc):
                    yield (nr, nc)
    def place_mines(self, first_r=None, first_c=None):
        # Place mines randomly, optionally ensuring (first_r, first_c) and its neighbors are safe
        positions = [(r,c) for r in range(self.rows) for c in range(self.cols)]
        forbidden = set()
        if self.first_click_safe and first_r is not None and first_c is not None:
            forbidden.add((first_r, first_c))
            for nr, nc in self.neighbors(first_r, first_c):
                forbidden.add((nr, nc))
        available = [p for p in positions if p not in forbidden]
        if len(available) < self.bombs:
            # Not enough space to place bombs if forbidden area is large; fall back to placing anywhere except first cell
            available = [p for p in positions if p != (first_r, first_c)]
        chosen = random.sample(available, self.bombs)
        for r, c in chosen:
            self.mines[r][c] = True
        self.calculate_counts()
        self.mines_placed = True
    def calculate_counts(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.mines[r][c]:
                    self.counts[r][c] = -1
                else:
                    cnt = 0
                    for nr, nc in self.neighbors(r, c):
                        if self.mines[nr][nc]:
                            cnt += 1
                    self.counts[r][c] = cnt
    def reveal(self, r, c):
        """
        Reveal cell at (r,c).
        Returns "bomb" if a mine was revealed (game over), or a list of revealed coordinates otherwise.
        """
        if not self.mines_placed:
            # Place mines now; ensure first click safe if configured
            if self.first_click_safe:
                self.place_mines(first_r=r, first_c=c)
            else:
                self.place_mines()
        if self.flagged[r][c] or self.revealed[r][c]:
            return []
        if self.mines[r][c]:
            # Revealed a mine -> game over
            self.revealed[r][c] = True
            self.revealed_count += 1
            return "bomb"
        # Flood-fill reveal for zeros
        revealed = []
        self._reveal_recursive(r, c, revealed)
        return revealed
    def _reveal_recursive(self, r, c, revealed_list):
        queue = deque()
        queue.append((r, c))
        while queue:
            cr, cc = queue.popleft()
            if self.revealed[cr][cc] or self.flagged[cr][cc]:
                continue
            self.revealed[cr][cc] = True
            revealed_list.append((cr, cc))
            self.revealed_count += 1
            if self.counts[cr][cc] == 0:
                for nr, nc in self.neighbors(cr, cc):
                    if not self.revealed[nr][nc] and not self.flagged[nr][nc]:
                        queue.append((nr, nc))
    def toggle_flag(self, r, c):
        if self.revealed[r][c]:
            return
        self.flagged[r][c] = not self.flagged[r][c]
    def is_revealed(self, r, c):
        return self.revealed[r][c]
    def is_flagged(self, r, c):
        return self.flagged[r][c]
    def get_count(self, r, c):
        return self.counts[r][c] if self.counts[r][c] >= 0 else -1
    def get_mine(self, r, c):
        return self.mines[r][c]
    def reveal_all_mines(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.mines[r][c]:
                    self.revealed[r][c] = True
    def is_won(self):
        # Win if all non-mine cells are revealed
        total_cells = self.rows * self.cols
        return self.revealed_count == (total_cells - self.bombs)
    def remaining_flags(self):
        flags = sum(1 for r in range(self.rows) for c in range(self.cols) if self.flagged[r][c])
        return max(0, self.bombs - flags)