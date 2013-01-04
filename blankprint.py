#!/usr/bin/python
# ~*~ coding: latin-1 ~*~

import os
import sys
import syslog 
import usb.core
import usb.util
import subprocess
import time
import RPi.GPIO as gpio

cfg = {
    "font_name": "Courier-Bold",
    # available fonts:
    # Courier     Courier-Bold      Courier-BoldOblique    Courier-Oblique
    # Helvetica   Helvetica-Bold    Helvetica-BoldOblique  Helvetica-Oblique
    # Times-Bold  Times-BoldItalic  Times-Italic           Times-Roman
    # Symbol
    "font_size": 15,

    "pos_left": 5,
    # measure for left distances seem to be 100 units ~ 42mm (?!?!)
    "pos_bottom_acnt": 320,
    "pos_bottom_bank": 285,
    "pos_bottom_date": 180,
    # measure for bottom distances seem to be 100 units ~ 36mm (?!?!)
    }

def main():
    script_file = os.path.realpath(__file__)
    script_path = os.path.dirname(script_file)

    syslog.syslog("Ready. Awaiting bytton press")

    def printform(fields=None):
        blinken = subprocess.call([os.path.join(script_path,"statusblink")])
        increment = subprocess.call([os.path.join(script_path,"increment_blank")])
	tmpl = file(os.path.join(script_path, "bon-tmpl.eps"), "r")
        lp = subprocess.Popen(["lp", "-d", "Star_TSP143_"],
                                stdin=subprocess.PIPE).stdin
        for line in tmpl:
            line = line.rstrip()
            if (line == "showpage") and (fields is not None):
                print >>lp, "/{font_name} {font_size} selectfont".format(**cfg)
                for name, text in fields.iteritems():
                    print >>lp, "{left} {bottom} moveto".format(
                        left=cfg["pos_left"], bottom=cfg["pos_bottom_" + name])
                    print >>lp, "(" + text + ") show"
            print >>lp, line
        lp.close()
        tmpl.close()


    gpio.setmode(gpio.BCM)
    gpio.setup(15, gpio.IN, pull_up_down=gpio.PUD_UP)
    pressed = False

    while True:
        if gpio.input(15) == 0:
            syslog.syslog("button pressed")
            if pressed == False:
                pressed = True
                syslog.syslog("printing")
                printform()
        else:
            pressed = False
        time.sleep(0.1)

main()
