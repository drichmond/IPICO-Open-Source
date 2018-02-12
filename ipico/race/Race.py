from datetime import datetime, timedelta
from ipico.race import Registration
from ipico.reader import Reader
from bisect import insort
import copy
import warnings
class Race():
    class Result():
        def __init__(self, registrant, guntime):
            if((registrant != None) and
               not isinstance(registrant, Registration.Registrant)):
                raise TypeError('Argument registrant must be an instance of '
                                'Registration.registrant')
            if(not isinstance(guntime, datetime)):
                raise TypeError('Argument guntime must be an instance of '
                                'datetime.datetime')
            self.__guntime = guntime

            self.__registrant = registrant
            self.__xings = []
            self.__times = []

        def log(self, scan):
            insort(self.__xings, scan)
            if(self.__registrant != None):
                t = scan.time - self.__guntime - self.__registrant.offset
            else:
                t = scan.time - self.__guntime                
            insort(self.__times, t)

        def __str__(self):
            reg = self.__registrant
            times = [str(time)
                     for time in self.__times]
            if(reg != None):
                fname = reg.name[0]
                lname = reg.name[1] 
            else:
                fname = "Unknown"
                lname = "Racer"
            return (f'{fname:20s} {lname:20s}'
                    f'Times: {times}')
        @property
        def times(self):
            return copy.copy(self.__times)

        def __lt__(self, o):
            if(not isinstance(guntime, datetime)):
                raise TypeError('Argument o must be an instance of'
                                'Result')
            if(len(self.__times) < len(o.times) or
               self.__times[-1] < o.times[-1]):
                return False
                

    def __init__(self, guntime, reg, readers):
        if(not isinstance(guntime, datetime)):
            raise TypeError('Argument guntime must be an instance of'
                               'datetime.datetime')
        self.__guntime = guntime

        self.__registration = reg

        self.__results = {registrant.tag : self.Result(registrant, guntime)
                          for registrant in self.__registration}

        if(not isinstance(readers, list)):
            raise TypeError('Argument readers must be an instance of list')

            for r in readers:
                if(not isinstance(r, Reader)):
                    raise TypeError('All elements in argument readers (list) '
                                    'must be an instance of '
                                    'ipico.reader.Reader')
        for rdr in readers:
            for s in self.filter(rdr):
                try:
                    self.__results[s.tag].log(s)
                except KeyError:
                    print(f'Unknown tag: {s.tag}')
                    warnings.warn(f'No registrant matched tag: {s.tag}. '
                                  'Added to registration table without '
                                  'registrant data')
                    self.__results[s.tag] = self.Result(None, guntime)
                    

        for (k, result) in self.__results.items():
            print(result)
            
                
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
        
