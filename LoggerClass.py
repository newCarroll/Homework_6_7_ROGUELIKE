import time
import libtcodpy as libtcod
import textwrap

BAR_WIDTH = 20
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
PANEL_HEIGHT = 7
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1


class Logger:

    def __init__(self):
        self.game_msgs = []

    def write_log(self, mes):
        with open('log_file.txt', 'a+') as logfile:
            logfile.write(time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime()))
            logfile.write(' ' + mes + '\n')

    def message(self, new_msg, color=libtcod.white):
        # split the message if necessary, among multiple lines
        new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)
        self.write_log(new_msg)

        for line in new_msg_lines:
            # if the buffer is full, remove the first line to make room for the new one
            if len(self.game_msgs) == MSG_HEIGHT:
                del self.game_msgs[0]

            # add the new line as a tuple, with the text and the color
            self.game_msgs.append((line, color))
