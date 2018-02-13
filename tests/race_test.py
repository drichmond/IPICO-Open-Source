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

race = Race(gun, reg, [tin, tout, fin])
results = race.matches(sex='Male')
numxings = 5
# Can't sort all entries unless you remove the ones that have less
# crossings than expected -- This is more common in DL and I don't
# have a good way of handling it
results = list(filter(lambda x: len(x.splits) == numxings, results))
results.sort()
for r in results:
    print(r)
results = race.matches()
for r in results:
    print(r)

results = race.matches(name=("Johanna", "Gartman"))
res = list(results)[0]
for r in res.xings:
    print(r)

