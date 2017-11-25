"""
CP750 Volume Controller

Uses PyQt5 and the Webengine module to control
the volume and input mode of a Dolby CP750
Digital Cinema Processor using the TCP/IP-Interface
(called "telnet" in the manual) on Port 61408.

Author: Roland Tapken <roland@bitarbeiter.net>
License: GPLv3
"""

import logging
import signal
import socket

from PyQt5.QtCore import QObject, pyqtSlot

LOGGER = logging.getLogger(__name__)

class Client(QObject):
	def __init__(self, args):
		super(Client, self).__init__()
		self.port = args.port
		self.destination = args.destination
		self.socket = None

#  vim: set fenc=utf-8 ts=4 sw=4 noet :

