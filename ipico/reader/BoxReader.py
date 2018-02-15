from . import Reader
import ipaddress
from datetime import datetime
import socket
import warnings
class BoxReader(Reader):

    def __init__(self, name, ip_address):
        """Initialize a new BoxReader object. 

        Parameters
        ----------
        
        ip_address : String
            A IPV4 or IPV6 IP Address 

        """
        if(not (isinstance(name, str))):
            raise RuntimeError('Argument name (Reader Name) must '
                               'be a string')
        self.__name = name

        self.__ip_address = ipaddress.ip_address(ip_address)
        # create an INET, STREAMing socket
        self.__skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__skt.connect((str(self.__ip_address), 10000))

        super(BoxReader, self).__init__(name)
        
    def _get_reader_id(self):
        # Last digits of IP address (should be two digits)
        rid = str(self.__ip_address).split('.')[-1]
        if(not (isinstance(rid, str)) and len(rid) > 2):
            raise RuntimeError(f'Reader ID (last digits of IP) must '
                               f'be at most 2 digits. Got {rid}')
        
        return rid

    def _get_initial_time(self):
        # Readers must be synced before use?
        return datetime.now()

    # TODO: DO Triggers cause any output? 
    def _read(self):
        s = None
        while(s == None):
            c = None
            data = b''
            ss = ''
            while(len(data) < 38):
                byts, _ = self.__skt.recvfrom(4096)
                data += byts
            ss = data[:38]
            data = data[38:]
            ss = ''.join([chr(ssc) for ssc in ss]).strip()
            
            try:
                s = super(BoxReader,self)._read(ss)
            except ValueError:
                warnings.warn(f'Scan malformed: {ss}', \
                              category=self.MalformedWarning)
        return s

    def __next__(self):
        try:
            return self._read()
        except EOFError:
            raise StopIteration()
