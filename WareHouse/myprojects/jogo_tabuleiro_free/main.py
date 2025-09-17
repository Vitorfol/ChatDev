'''
Main entry point for the customizable board game.
Runs the tkinter GUI which uses Game as a facade for setup and playing.
'''
import tkinter as tk
from gui import GameGUI
def main():
    root = tk.Tk()
    root.title("Custom Board Game")
    app = GameGUI(root)
    root.mainloop()
if __name__ == "__main__":
    main()