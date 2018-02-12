from . import Reader
from datetime import datetime
import warnings
class FileReader(Reader):
    def __init__(self, name):
        if(not (isinstance(name, str))):
            raise RuntimeError('Argument name (Reader Name) must '
                               'be a string')
        self.__name = name

        try:
            self.f = open(f'{name}.txt','r')
        except IOError:
            print('Error: Couldn\'t find file \'{name}.txt\' associated with '
                  'File Reader')
            exit(1)

        super(FileReader, self).__init__('File Reader: {name}')

    def _get_reader_id(self):
        cur = self.f.tell()
        self.f.seek(0)
        ss = self.f.readline().strip()
        if ss == '':
            raise IOError(f'Failure while determining Reader ID. Reading '
                          f'first line of {self.__name} produced no data')
        self.f.seek(cur)
        s = None
        while(s == None and ss != ''):
            try:
                ss = self.f.readline().strip()
                s = self.Scan(0, ss)
            except ValueError:
                warnings.warn(f'Failure while determining Reader ID. Reading '
                              f'line of {self.__name} produced malformed'
                              f'scan string')
        
        if(s == None):
                raise RuntimeError(f'Failure while determining Reader ID. '
                                   f'Could not find valid scan string in file: '
                                   f'{self.__name}')
        return s.reader

    def _get_initial_time(self):
        cur = self.f.tell()
        self.f.seek(0)
        ss = self.f.readline().strip()
        if ss == '':
            raise IOError(f'Failure while determining time of first scan. '
                          f'Reading first line of {self.__name} produced no '
                          f'data')
        self.f.seek(cur)
        s = None
        while(s == None and ss != ''):
            try:
                ss = self.f.readline().strip()
                s = self.Scan(0, ss)
            except ValueError:
                warnings.warn(f'Failure while determining Reader ID. Reading '
                              f'line of {self.__name} produced malformed'
                              f'scan string')
        
        if(s == None):
                raise RuntimeError(f'Failure while determining Reader ID. '
                                   f'Could not find valid scan string in file: '
                                   f'{self.__name}')
        return s.time

    # TODO: DO Triggers cause any output? 
    def _read(self):
        s = None
        while(s == None):
            ss = self.f.readline().strip()
            if ss == '':
                raise EOFError('End of Input File Reached!')
            try:
                s = super(FileReader,self)._read(ss)
            except ValueError:
                warnings.warn(f'Scan malformed: {ss}',
                              category=self.MalformedWarning)
        return s

    def __next__(self):
        try:
            return self._read()
        except EOFError:
            raise StopIteration()
