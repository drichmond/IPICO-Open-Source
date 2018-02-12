#!/usr/local/bin/python3.6
from ipico.reader import FileReader
from ipico.race import Registration
from ipico.race import Race
from datetime import datetime, timedelta
reg = Registration("2016_Tritonman_DL", 10)
tin = FileReader("transition_in")
tout = FileReader("transition_out")
fin = FileReader("finish")
gun = datetime(2016, 2, 20, 6, 58, 59)

Race(gun, reg, [tin, tout, fin])
