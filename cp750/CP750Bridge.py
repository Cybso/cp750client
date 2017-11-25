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

class CP750Bridge(QObject):
	def __init__(self, args):
		super(CP750Bridge, self).__init__()
		self.port = args.port
		self.destination = args.destination
		self.socket = None
		self.stream = None
	
	@pyqtSlot(result=str)
	def getState(self):
		if self.socket is None:
			return "disconnected"
		else:
			return "connected"
	
	@pyqtSlot(result=str)
	def connect(self):
		if self.socket is not None:
			self.disconnect()
		LOGGER.info("Connecting to %s:%d" % (self.destination, self.port))
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((self.destination, self.port))
			self.stream = s.makefile("rwb", 0)
			self.socket = s
		except:
			LOGGER.exception("Failed to connect to %s:%d" % (self.destination, self.port))
		return self.getState()
	
	@pyqtSlot(result=str)
	def disconnect(self):
		if self.socket is not None:
			LOGGER.info("Disconnecting from %s:%d" % (self.destination, self.port))
			try:
				self.socket.close()
			except:
				LOGGER.exception("Failed to close connection")
			finally:
				self.socket = None
				self.stream = None
		return self.getState()
	
	@pyqtSlot(str, result=str)
	def send(self, command):
		LOGGER.info("Command: %s" % command)
		if self.socket is None:
			self.connect()
			if self.socket is None:
				LOGGER.warn("Socket is disconnected")
				return self.getState()

		try:
			result=""
			self.stream.write(command.encode('UTF-8') + b"\r\n")
			line=self.stream.readline().decode('UTF-8').strip()
			while line:
				result=result + line + "\n"
				line=self.stream.readline().decode('UTF-8').strip()
			return result.strip()
		except:
			LOGGER.exception("Command '%s' failed" % command)
			return "failed"

#  vim: set fenc=utf-8 ts=4 sw=4 noet :
