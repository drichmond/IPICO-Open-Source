#!/usr/local/bin/python3.6
from ipico.reader import FileReader
from ipico.race import Registration
from ipico.race import Race
from datetime import date
date = date(2016, 2, 20)
reg = Registration("2016_Tritonman_DL", date, 10)
tin = FileReader("transition_in")
tout = FileReader("transition_out")
fin = FileReader("finish")

race = Race(reg, [tin, tout, fin])
numxings = 5

def tostr(delta):
    h = int(delta.seconds / 3600)
    m = int((delta.seconds % 3600) / 60)
    s = int(delta.seconds % 60)
    return (f'{h:0>2}:{m:0>2}:{s:0>2}')

for sex in reg.sexes:
    for div in reg.divisions:
        results = [res for res in race.matches(sex=sex, division=div)
                   if len(res.xings) == numxings]
        results.sort()

        print(f'\n\nResults for {sex}, {div}\n\n')
        for r in results:
            # Finish times are *explitly* not calculated so that the
            # RD can decide what a valid finish time is. In this case,
            # a valid finish time is a time with 5 crossings
            fin = (f'- Finish: {r.deltatostr(r.finish)}')
            print(str(r) + fin)

        results = [res for res in race.matches(sex=sex, division=div)
                   if len(res.xings) != numxings]

        print(f'\n\nIncomplete Results for {sex}, {div}\n\n')
        for r in results:
            print(r)


