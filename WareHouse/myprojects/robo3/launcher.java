'''
Launcher: A simple GUI launcher that lets the user choose a mode:
- User Controlled (arrow buttons)
- Random Single Robot
- Random Multiple Robots
Each mode has its own Main class (UserMain, RandomSingleMain, RandomMultipleMain).
This file contains the primary main() that opens a small selection window.
'''
/*
DOCSTRING
Launcher: A simple GUI launcher that lets the user choose a mode:
- User Controlled (arrow buttons)
- Random Single Robot
- Random Multiple Robots
Each mode has its own Main class (UserMain, RandomSingleMain, RandomMultipleMain).
This file contains the primary main() that opens a small selection window.
*/
import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
public class Launcher {
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            JFrame frame = new JFrame("Robot Simulator Launcher");
            frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
            frame.setSize(400, 220);
            frame.setLocationRelativeTo(null);
            frame.setLayout(new BorderLayout());
            JLabel label = new JLabel("<html><center>Robot Simulator<br>Choose a mode</center></html>", SwingConstants.CENTER);
            label.setFont(new Font("SansSerif", Font.BOLD, 16));
            frame.add(label, BorderLayout.NORTH);
            JPanel buttons = new JPanel();
            buttons.setLayout(new GridLayout(3, 1, 10, 10));
            JButton userBtn = new JButton("User Controlled (Single Robot)");
            JButton randomSingleBtn = new JButton("Random Single Robot");
            JButton randomMultiBtn = new JButton("Random Multiple Robots");
            userBtn.addActionListener(e -> {
                UserMain.main(new String[0]);
            });
            randomSingleBtn.addActionListener(e -> {
                RandomSingleMain.main(new String[0]);
            });
            randomMultiBtn.addActionListener(e -> {
                RandomMultipleMain.main(new String[0]);
            });
            buttons.add(userBtn);
            buttons.add(randomSingleBtn);
            buttons.add(randomMultiBtn);
            frame.add(buttons, BorderLayout.CENTER);
            frame.setVisible(true);
        });
    }
}