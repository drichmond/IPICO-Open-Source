# Readers are scan factories
import abc
from datetime import datetime
import warnings
from ..Tag import TagFactory
class Reader(abc.ABC):
    
    def __init__(self, name):
        #self.scan_selftest()

        self._seq = 0
        
        self._name = name
        if(not isinstance(name, str)):
            raise ValueError('Argument name must be a string!')

        reader = self._get_reader_id()
        if(not(isinstance(reader, str) and reader.isdigit() and len(reader) == 2)):
            raise ValueError('Reader ID must be two-digit string. E.g. \'01\'')
        self.__reader = reader

        first_time = self._get_initial_time()
        if(not(isinstance(first_time, datetime))):
            raise ValueError('Malformed initial time.')
        self.__first_time = first_time
        self.__cur_time = first_time

    def _read(self, ss, dt = None):
        self._seq += 1
        s = self.Scan(self._seq, ss, dt)
        if(s.reader != self.__reader):
            raise RuntimeError('Scan\'s Reader ID did not match Reader ID of '
                               'Scanner')

        # It's okay if two times are equal - just as long as they
        # aren't out of order
        if(s.time < self.__first_time):
            raise self.SequenceError('Scan\'s current time occurs before time '
                                     'of reader\'s first scan')
        if(s.time < self.__cur_time):
            warnings.warn(f'Scan ID {self._seq} and '
                          f'Scan ID {self._seq - 1} out of order',
                          category=self.SequenceWarning)
            self.__cur_time = s.time
        return s

    @abc.abstractmethod
    def _get_reader_id(self):
        pass
    
    @abc.abstractmethod
    def _get_initial_time(self):
        pass

    @abc.abstractmethod
    def __next__(self):
        pass

    def __iter__(self):
        return self

    class Scan():
        __FIELD_HEADER  = slice(0, 2)
        __FIELD_READER  = slice(2, 4)
        __FIELD_TAG_ID  = slice(4, 16)
        __FIELD_MAT_A   = slice(16, 18)
        __FIELD_MAT_B   = slice(18, 20)
        __FIELD_TIMEALL = slice(20, 36)
        __FIELD_YEAR_XX = slice(20, 22)
        __FIELD_MONTH   = slice(22, 24)
        __FIELD_DAY     = slice(24, 26)
        __FIELD_HOUR    = slice(26, 28)
        __FIELD_MINUTE  = slice(28, 30)
        __FIELD_SECOND  = slice(30, 32)
        __FIELD_TENTHS  = slice(32, 33)
        __FIELD_TIMSEQ  = slice(33, 36)
        def __init__(self, seq, s, dt = None):
            def ishex(val):
                try:
                    int(val, 16)
                    return True
                except ValueError:
                    return False
                
            if(not isinstance(seq, int)):
                raise ValueError('Argument seq must be an integer!')
            self.__seq = seq
            
            if(not (isinstance(s, str) and ishex(s) and len(s) == 36)):
                raise ValueError('Argument s (scan data) must be a '
                                 '36-character hexadecimal string!');
            self.__s = s
            
            self.__header = s[self.__FIELD_HEADER]
            
            self.__timseq = s[self.__FIELD_TIMSEQ]
            
            mat_a = s[self.__FIELD_MAT_A]
            if(not(mat_a.isdigit() and len(mat_a) == 2)):
                raise ValueError(f'Mat A field must be one of {self.__VALUES_MAT}. '
                                 f'Got {mat_a}')
            self.__mat_a = mat_a    

            mat_b  = s[self.__FIELD_MAT_B]
            if(not(mat_b.isdigit() and len(mat_b) == 2)):
                raise ValueError(f'Mat B field must be one of {self.__VALUES_MAT}. '
                                 f'Got {mat_b}')
            self.__mat_b = mat_b

            self.__reader = s[self.__FIELD_READER]
            if(not(self.__reader.isdigit() and len(self.__reader) == 2)):
                    raise ValueError('Reader ID must be two-digit string. '
                                     'E.g. \'01\'')
            self.__time = None
            if(dt == None):
                y = 2000 + int(s[self.__FIELD_YEAR_XX])
                mo = int(s[self.__FIELD_MONTH])
                d = int(s[self.__FIELD_DAY])
                h = int(s[self.__FIELD_HOUR  ])
                mi = int(s[self.__FIELD_MINUTE])
                sec = int(s[self.__FIELD_SECOND])
                us = 100000 * int(s[self.__FIELD_TENTHS])
                self.__time = datetime(y, mo, d, h, mi, sec, us)
                if(self.sort_time != s[self.__FIELD_TIMEALL]):
                    raise ValueError(f'Property sort_time and field TIMEALL' \
                                     f'did not match: {self.sort_time} '\
                                     f'{s[self.__FIELD_TIMEALL]}')
            elif(isinstance(dt, datetime)):
                    self.__time = dt
            else:
                raise ValueError('Argument dt must be instance of datetime')

            self.__tag = TagFactory.scan_tag(s[self.__FIELD_TAG_ID], self)
                
        @property
        def seq(self):
            return self.__seq
        
        @property
        def header(self):
            return self.__header
        
        @property
        def reader(self):
            return self.__reader
        
        @property
        def tag(self):
            return self.__tag
        
        @property
        def mat(self):
            if(self.__mat_a != '00'):
                return 'A'
            else:
                return 'B'
            
        @property
        def time(self):
            return self.__time
        
        @property
        def sort_time(self):
            dt = self.__time
            return (f'{dt.year % 100:0>2}{dt.month:0>2}{dt.day:0>2}{dt.hour:0>2}' + 
                    f'{dt.minute:0>2}{dt.second:0>2}{str(dt.microsecond)[0]}' + self.seq_uid)
        
        @property
        def seq_uid(self):
            return self.__timseq

        @property
        def raw(self):
            return self.__s
        
        def __str__(self):
            return (f'Scan Sequence Num: {self.__seq} (Tag: {self.tag}) @ '
                    f'{self.time.strftime("%y-%m-%d %H:%M:%S")} | '
                    f'Scan Unique ID: {self.seq_uid} from {self.mat} on'
                    f'Reader {self.reader}')

        def __lt__(self, r):
            return self.raw[self.__FIELD_TIMEALL] < r.raw[self.__FIELD_TIMEALL]
        
    def scan_selftest(self):
        # self 0: Initialize Scan Object with Valid Scan String
        gold = 'aa00058001e5bf5a010004010101042524ff'
        s = self.Scan(0, gold)
        if(gold != s.raw):
            raise ValueError()
        # Test 1: Initialize Scan Object with invalid Scan String
        # (Include invalid \r\n)
        try:
            s = self.Scan(1, 'aa00058001e5bf5a010004010101042524ff\r\n')
        except ValueError:
            pass
        
        # Test 2: String too short
        try:
            s = self.Scan(2, 'aa00058001e5bf5a010004010101042524f')
        except ValueError:
            pass
        
        # Test 3: Unexpected Characters
        
        try:
            s = self.Scan(3, 'aa00058001e5bf5a010004010101042524fx')
        except ValueError:
            pass

    class MalformedWarning(Warning):
        def __init__(self,*args,**kwargs):
            Warning.__init__(self,*args,**kwargs)

    class SequenceError(Exception):
        def __init__(self,*args,**kwargs):
            Exception.__init__(self,*args,**kwargs)

    class SequenceWarning(Warning):
        def __init__(self,*args,**kwargs):
            Warning.__init__(self,*args,**kwargs)
            
