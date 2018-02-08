#!/usr/local/bin/python3.6
from ipico.reader import USBReader
def main():
    rdr = USBReader()
    while True:
        s = rdr.read()
        print(s)
    
if __name__ == '__main__':
  main()
