from . import Reader
import usb.core
import usb.util
from datetime import datetime

class USBReader(Reader):
    __IPICO_VENDOR_ID = 0x0483
    __IPICO_PRODUCT_ID = 0x3490
    def __init__(self):
        usb_dev = usb.core.find(idVendor=self.__IPICO_VENDOR_ID,
                                idProduct=self.__IPICO_PRODUCT_ID)
        if(usb_dev == None):
            raise IOError('IPICO USB Reader Not Found')
        self.__usb_dev = usb_dev
        self.__usb_dev.set_configuration()
        self.__endpoint = self.__usb_dev[0][(1,0)][1]

        super(USBReader, self).__init__('IPICO USB Reader')

    def __scan(self):
        while(d == ''):
            try:
                data = self.__usb_dev.read(self.__endpoint.bEndpointAddress,
                                           self.__endpoint.wMaxPacketSize)
                d = ''.join([chr(c) for c in data]).strip()
            except usb.core.USBError as e:
                # Todo: Handle USB Disconnection gracefully
                if e.args == ('Operation timed out',):
                    continue
        return d

    def _read(self):
        while(s == None):
            ss = self.__scan()
            try:
                s = super(FileReader,self)._read(ss)
            except ValueError:
                warnings.warn(f'Scan malformed: {ss}',
                              category=self.MalformedWarning)
        return s

    def __next__(self):
        try:
            return self._read()
        # Todo: Handle USB Disconnection gracefully
        except EOFError:
            raise StopIteration()

    # Do USB readers always return Reader ID of 0?
    def _get_reader_id(self):
        return '00'

    def _get_initial_time(self):
        return datetime.now()
