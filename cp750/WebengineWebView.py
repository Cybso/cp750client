"""
CP750 Volume Controller

Uses PyQt5 and the Webengine module to control
the volume and input mode of a Dolby CP750
Digital Cinema Processor using the TCP/IP-Interface
(called "telnet" in the manual) on Port 61408.

Author: Roland Tapken <roland@bitarbeiter.net>
License: GPLv3
"""

import os
import logging

from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtCore import QUrl, QVariant, QTimer, QByteArray, QBuffer, QIODevice, pyqtSlot
from PyQt5.QtWebChannel import QWebChannel

QTWEBENGINE_REMOTE_DEBUGGING_PORT='26512'
LOGGER = logging.getLogger(__name__)

class Inspector(QWebEngineView):
	""" QWebEngine does not include an inspector. Instead,
	open a second QWebEngineView that points to the remote
	debugging view.
	"""
	def __init__(self, parent, view):
		QWebEngineView.__init__(self, parent)
		self.setVisible(False)
		if os.environ.get('QTWEBENGINE_REMOTE_DEBUGGING'):
			self.load(QUrl('http://localhost:' + os.environ['QTWEBENGINE_REMOTE_DEBUGGING']))
		else:
			self.setHtml('Web Inspector not available. Please start the application with debugging enabled (-d/--debug).')

class WebView(QWebEngineView):
	""" Returns a QWebEngineView and loads the FrontendWebPage """
	def __init__(self, parent, cp750bridge, args):
		if args.debug:
			# Enable remote debugger / "inspector"
			# Must be set before the parent constructor is called
			LOGGER.warn("QTWEBENGINE_REMOTE_DEBUGGING enabled on port http://localhost:%s/. This may be a security issue. Remove '-d/--debug' for production environments." % (QTWEBENGINE_REMOTE_DEBUGGING_PORT))
			os.environ['QTWEBENGINE_REMOTE_DEBUGGING'] = QTWEBENGINE_REMOTE_DEBUGGING_PORT;
		QWebEngineView.__init__(self, parent)
		self.setPage(FrontendWebPage(self, cp750bridge, args))

class FrontendWebPage(QWebEnginePage):
	""" Override QWebPage to redirect JavaScript console output
	to logger (level 'info'). If the output starts with 'debug',
	'warn', 'error' or 'exception' the appropirate level is
	choosen instead.
	"""
	def __init__(self, parent, cp750bridge, args):
		QWebEnginePage.__init__(self, parent)
		self.args = args
		channel = QWebChannel(self);
		self.setWebChannel(channel);
		channel.registerObject("cp750bridge", cp750bridge);

	def javaScriptConsoleMessage(self, level, msg, line, source):
		if msg.startswith('debug'):
			LOGGER.debug('%s line %d: %s' % (source, line, msg))
		elif msg.startswith('warn'):
			LOGGER.warn('%s line %d: %s' % (source, line, msg))
		elif msg.startswith('error') or msg.startswith('exception'):
			LOGGER.error('%s line %d: %s' % (source, line, msg))
		else:
			LOGGER.info('%s line %d: %s' % (source, line, msg))

#  vim: set fenc=utf-8 ts=4 sw=4 noet :

