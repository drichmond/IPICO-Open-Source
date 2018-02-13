from datetime import datetime, timedelta
from ipico.race import Registration
from ipico.reader import Reader
from bisect import insort
import copy
import warnings
class Race():
    class Result():
        def __init__(self, registrant):
            if((registrant != None) and
               not isinstance(registrant, Registration.Registrant)):
                raise TypeError('Argument registrant must be an instance of '
                                'Registration.registrant')
            
            self.__registrant = registrant
            self.__xings = []

        def log(self, scan):
            if(scan.time < self.__registrant.guntime):
                fname = self.__registrant.name[0]
                lname = self.__registrant.name[1]
                warnings.warn(f'Participant {fname} {lname} '
                              f'has scan before gun time! Dropping Scan!')
            else:
                insort(self.__xings, scan)

        def __str__(self):
            def tostr(delta):
                h = int(delta.seconds / 3600)
                m = int((delta.seconds % 3600) / 60)
                s = int(delta.seconds % 60)
                return (f'{h:0>2}:{m:0>2}:{s:0>2}')
            reg = self.__registrant
            splits = [f'{tostr(t)}'for t in self.splits]
            xings = [f'{str(s.time.strftime("%H:%M:%S"))}'for s in self.xings]
            times = f'Start: {str(reg.guntime.strftime("%H:%M:%S"))} - '
            times += "Splits:"
            for sp in  splits:
                times += f' {sp} | '
            fname = reg.name[0]
            lname = reg.name[1]
            div = reg.division
            if(div == 'Open'):
                div += f' ({reg.age_group})'
            return (f'{fname:20s} {lname:20s} {div:20s} {times}')

        @property
        def splits(self):
            numxings = len(self.__xings)
            ts = [None]*numxings
            last = self.__registrant.guntime
            for i in range(numxings):
                cur = self.__xings[i].time
                split = cur - last
                if(split < timedelta()):
                    name = self.__registrant.name
                    warnings.warn(f'Participant {name[0]} {name[1]} '
                                  f'has negative time split!')
                if(split.days != 0):
                    name = self.__registrant.name
                    warnings.warn(f'Participant {name[0]} {name[1]} '
                                  f'has negative time split!')
                ts[i] = split
                last = cur
            return ts

        @property
        def xings(self):
            return copy.copy(self.__xings)

        def match(self, **kwargs):
            return all(i == True for i in [getattr(self.__registrant, k) == v
                                           for k, v in kwargs.items()])

        def __lt__(self, o):
            if(not isinstance(o, Race.Result)):
                raise TypeError('Argument o must be an instance of Result')
            if(len(self.__xings) != len(o.xings)):
                raise RuntimeError('Invalid results in comparison')
            return self.__xings[-1] < o.xings[-1]

    def __init__(self, reg, readers):

        self.__registration = reg

        self.__results = {registrant.tag : self.Result(registrant)
                          for registrant in self.__registration}

        if(not isinstance(readers, list)):
            raise TypeError('Argument readers must be an instance of list')

            for r in readers:
                if(not isinstance(r, Reader)):
                    raise TypeError('All elements in argument readers (list) '
                                    'must be an instance of '
                                    'ipico.reader.Reader')

        # Nasty mess, can we simplify?
        for rdr in readers:
            for s in self.filter(rdr):
                try:
                    self.__results[s.tag].log(s)
                except KeyError:
                    warnings.warn(f'No registrant matched tag: {s.tag}. Ignoring Tag')

    def matches(self, **kwargs):
        if(kwargs == {}):
            return self.__results.values()
        else:
            return filter(lambda res: res.match(**kwargs), self.__results.values())
        
    class Crossing():
        def __init__(self, head):
            if(not isinstance(head, Reader.Scan)):
                raise RuntimeError('Argument head must be an instance of'
                                   'Reader.Scan')
            self.__head = head
            self.__tail = head

        @property
        def head(self):
            return self.__head

        @property
        def tail(self):
            return self.__tail

        @tail.setter
        def tail(self, t):
            if(not isinstance(t, Reader.Scan)):
                raise RuntimeError('Argument t must be an instance of'
                                   'Reader.Scan')

            if(t.tag != self.head.tag):
                raise RuntimeError('Tag must match!')

            if(t.time < self.tail.time):
                raise RuntimeError('Scan time of t must be after current'
                                   'tail\'s last scan time')

            self.__tail = t

        def __lt__(self, other):
            if(not isinstance(other, Race.Crossing)):
                raise RuntimeError('Argument other must be an instance of'
                                   'Race.Crossing')

            if(other.head.tag != self.tail.tag):
                raise RuntimeError('Invalid comparison: Tags must match')

            if(other.head.time == self.tail.time):
                raise RuntimeError('The head of one group and the tail of another group should not match')

            return self.tail.time < other.head.time

        def __str__(self):
            return (f'Crossing: Tag: {self.head.tag}, Head Time: {self.head.time} '
                    f'Tail Time: {self.tail.time}')
        
    @staticmethod
    def filter(rdr, delta = timedelta(seconds = 30)):
        crossings = dict()
        for scan in rdr:
            if(scan.tag not in crossings.keys()):
                x = Race.Crossing(scan)
                crossings[scan.tag] = [x]
                yield scan
            else:
                tag_xs = crossings[scan.tag]
                mostrecent = tag_xs[-1]
                if(mostrecent.tail.time > scan.time):
                    raise RuntimeError('Tag scan times out of order!')
                
                elif((scan.time - mostrecent.tail.time) > delta):
                    x = Race.Crossing(scan)
                    insort(tag_xs, x) # In a pinch, this could be an append...
                    yield scan
                else:
                    mostrecent.tail = scan
        
