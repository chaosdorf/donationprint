#!/usr/bin/python
# ~*~ coding: latin-1 ~*~

import os
import sys
import syslog 
import usb.core
import usb.util
import subprocess
import time

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
    VENDOR_ID = 0x0801
    PRODUCT_ID = 0x0002
    DATA_SIZE = 337
    script_file = os.path.realpath(__file__)
    script_path = os.path.dirname(script_file)

    syslog.syslog("Starting application.")

    def warn(msg, *args, **kwargs):
        msg = msg.format(*args, **kwargs)
        syslog.syslog(syslog.LOG_ERR, msg)
        return msg

    def panic(msg, *args, **kwargs):
        sys.exit(warn(msg, *args, **kwargs))

    device = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
    if device is None:
        panic("Could not find MagTek USB HID Swipe Reader.")


    if device.is_kernel_driver_active(0):
        try:
            device.detach_kernel_driver(0)
        except usb.core.USBError as e:
            panic("Could not detach kernel driver: " + str(e))

    try:
        device.set_configuration()
        device.reset()
    except usb.core.USBError as e:
        fatal("Could not set configuration: " + str(e))
        
    endpoint = device[0][(0,0)][0]

    data = []
    swiped = False
    syslog.syslog("Ready. Awaiting card!")

    def printform(fields=None):
        blinken = subprocess.call([os.path.join(script_path,"statusblink")])
        counter = subprocess.call([os.path.join(script_path,"increment_filled")])
        subprocess.call(["./printtemplate", "", fields.bank, fields.acnt, ""])

    while True:
        try:
            data += device.read(endpoint.bEndpointAddress,
                                endpoint.wMaxPacketSize)
            swiped = True
            if len(data) >= DATA_SIZE:
                newdata = "".join(map(chr, data))
                account = newdata[241:251]
                bank = newdata[232:240]
                if account.isdigit() and bank.isdigit():
                    syslog.syslog("Got working card. Printing form.")
                    printform({
                        "acnt": account,
                        "bank": bank,
                        "date": "", #time.strftime("%d.%m.%Y"),
                        })
                    syslog.syslog("Printed form. Now printing thanks.")
                else:
                    warn("Unreadable card. Printing blank bon.")
                    #printform()
                    #printthanks()
                swiped = False
                data = []

        except usb.core.USBError as e:
            if e.args == ('Operation timed out',) and swiped:
                if len(data) < DATA_SIZE:
                    warn("Bad swipe. ({0} bytes)", len(data))
                    data = []
                    swiped = False
                    continue
                else:
                    warn("Not enough data grabbed. ({0} bytes)", len(data))
                    data = []
                    swiped = False
                    continue

main()
