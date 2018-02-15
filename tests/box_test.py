#!/usr/local/bin/python3.6
from ipico.reader import BoxReader
def main():

    # read a data packet
    data = None
    seq = 0
    rdr = BoxReader('Finish', '192.168.2.34')
    for s in rdr:
        print(s)

if __name__ == '__main__':
  main()



