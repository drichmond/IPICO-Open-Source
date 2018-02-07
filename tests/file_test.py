#!/usr/local/bin/python3.6
from FileReader import FileReader
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
    rdr = FileReader("finish")
    for s in rdr:
        print(s)


if __name__ == '__main__':
  main()
