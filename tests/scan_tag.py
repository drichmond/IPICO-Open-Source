#!/usr/local/bin/python3.6
import usb.core
import usb.util
import time
from Scan import Scan
from USBReader import USBReader
from datetime import datetime
def main():
    """
    device = usb.core.find(idVendor=0x0483, idProduct=0x3490)

    # use the first/default configuration
    device.set_configuration()

    # first endpoint
    endpoint = device[0][(1,0)][1]
"""
    #print(device[0])
    #print(endpoint.bEndpointAddress)

    # read a data packet
    data = None
    seq = 0
    rdr = USBReader()
    while True:
        s = rdr.read()
        print(s)
    
"""
        try:
            data = device.read(endpoint.bEndpointAddress,
                               endpoint.wMaxPacketSize)
            tag_read = {}
            d = ""
            for h in data:
                d += chr(h)
            d = d.strip()
            s = Scan(seq, d)
            seq += 1
            print(s)
        except usb.core.USBError as e:
            data = None
            if e.args == ('Operation timed out',):

                continue
"""


if __name__ == '__main__':
  main()
