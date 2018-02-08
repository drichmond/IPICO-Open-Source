from . import Reader
import ipaddress
class BoxReader(Reader):

    def __init__(self, ip_address):
        """Initialize a new BoxReader object. 

        Parameters
        ----------
        
        ip_address : String
            A IPV4 or IPV6 IP Address 

        """
        self.ip_address = ipaddress.ip_address(ip_address)
