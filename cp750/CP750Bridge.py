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
import sys
import time

from PyQt5.QtCore import QObject, pyqtSlot

LOGGER = logging.getLogger(__name__)
ERROR_PREFIX='⚠'
SOCKET_TIMEOUT=250

def nonblocking_readline(f, timeout=SOCKET_TIMEOUT):
	""" Waits up to 'timeout' milliseconds for data from f. Otherwise this returns None """
	timeout = timeout + int(round(time.time() * 1000))
	line = b""
	while int(round(time.time() * 1000)) < timeout:
		char = f.read(1)
		if char is None:
			time.sleep(0.01)
			continue
		line += char
		if char == b"\n":
			return line
	raise IOError(0, 'Timeout')

def error_to_str(e):
	""" Converts an Exception to string """
	if hasattr(e, 'message') and e.message is not None:
		return ERROR_PREFIX + e.message
	if hasattr(e, 'strerror') and e.strerror is not None:
		return ERROR_PREFIX + e.strerror
	return ERROR_PREFIX + type(e).__name__

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
			s.settimeout(500)
			s.setblocking(False)
			self.stream = s.makefile("rwb", 0)
			self.socket = s
		except Exception as e:
			LOGGER.exception("Failed to connect to %s:%d" % (self.destination, self.port))
			return error_to_str(e)
		return self.getState()
	
	@pyqtSlot(result=str)
	def disconnect(self):
		if self.socket is not None:
			LOGGER.info("Disconnecting from %s:%d" % (self.destination, self.port))
			try:
				self.socket.close()
			except  Exception as e:
				LOGGER.exception("Failed to close connection")
				return error_to_str(e)
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
			line=nonblocking_readline(self.stream).decode('UTF-8').strip()
			while line:
				result=result + line + "\n"
				line=nonblocking_readline(self.stream).decode('UTF-8').strip()
			return result.strip()
		except Exception as e:
			LOGGER.exception("Command '%s' failed" % command)
			return error_to_str(e)

#  vim: set fenc=utf-8 ts=4 sw=4 noet :
