import time
import sys
import os

import pyperclip



























while True:
    tmp_value = pyperclip.paste()


    if tmp_value != recent_value:
        recent_value = tmp_value
        print("Value changed: %s" % str(recent_value))
        with open('output.txt', 'a') as ofh:
            ofh.write("<CLIP>\n")
            ofh.write(recent_value)
            ofh.write("\n</CLIP>\n")


    time.sleep(0.1)