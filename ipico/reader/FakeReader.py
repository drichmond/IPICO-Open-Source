from Reader import Reader
import usb.core
import usb.util
from datetime import datetime

class FakeReader(Reader):

        def __init__(self):
