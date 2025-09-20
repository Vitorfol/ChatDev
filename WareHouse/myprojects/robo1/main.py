'''
Main entry point for the Robot-Food simulation application.
Starts the Tkinter GUI defined in ui.py.
'''
from ui import RobotApp
def main():
    app = RobotApp()
    app.run()
if __name__ == "__main__":
    main()