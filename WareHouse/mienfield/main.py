'''
Main entry point for the Minesweeper application.
Starts the Tkinter root window and launches the Minesweeper GUI.
'''
import tkinter as tk
from gui import MinesweeperGUI
def main():
    root = tk.Tk()
    root.title("Campo Minado - ChatDev")
    app = MinesweeperGUI(root)
    root.mainloop()
if __name__ == "__main__":
    main()