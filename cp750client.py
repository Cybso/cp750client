#!/usr/bin/env python3
"""
CP750 Volume Controller

Nutzt PyQt5 mit Webengine, um den Dolby CP750
per Ethernet-Schnittstelel (Port 61408) zu steuern.

Die Python-Implementierung ist minimal gehalten und
letztendlich nur ein Wrapper zwischen grafischer HTML5-
Oberfläche und Socket. Die eigentliche Steuerungslogik
ist komplett im JavaScript-Teil der Oberläche implementiert.

Abhängigkeiten:
- Python 3.4 oder höher
- PyQt5 mit QtWebengine (python3-pyqt5.qtwebengine unter Debian)

Author: Roland Tapken <roland@bitarbeiter.net>
License: MIT
"""

import os
import sys
import argparse
import signal
import logging
from importlib import util

# Check dependencies
# Requires at least Python 3.4
if sys.version_info < (3,4):
	sys.stderr.write("This program requires at least Python 3.4, found version %d.%d.%d%s" % (
	    sys.version_info[0], sys.version_info[1], sys.version_info[2], os.linesep
	))
	sys.exit(1)

# Check for PyQt5 before loading it to create a nice error message if this is missing
if util.find_spec("PyQt5") is None:
	sys.stderr.write("Module PyQt5 not found. Maybe you need to install 'python3-pyqt5'.%s" % os.linesep)
	sys.exit(1)

if util.find_spec("PyQt5.QtWebEngineWidgets") is None:
	sys.stderr.write("Neither module 'PyQt5.QtWebKit' nor 'PyQt5.QtWebEngineWidgets' found. Maybe you need to install 'python3-pyqt5.qtwebkit'.%s" % os.linesep)
	sys.exit(1)

from PyQt5.Qt import Qt
from PyQt5.QtCore import QDir, QStandardPaths
from PyQt5.QtWidgets import QApplication

# Automatically convert between python strings and QString
import sip
sip.setapi('QString', 2)

def main():
	basepath=QDir.fromNativeSeparators(os.path.dirname(os.path.abspath(__file__))) + '/ui/'

	# Define and parse program arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("destination", metavar="DESTINATION", help="Hostname or IP adress of CP750 cinema processor")
	parser.add_argument("-p", "--port", metavar="PORT", type=int, default=61408, required=False, help="Port of CP750 cinema processor")
	parser.add_argument("-f", "--fullscreen", help="start in fullscreen mode", action="store_true")
	parser.add_argument("-s", "--stayontop", help="stay on top (while not running any apps)", action="store_true")
	parser.add_argument("-r", "--docroot", help="Document root of UI files (default: %s)" % (basepath), default=basepath)
	parser.add_argument("-v", "--verbose", help="be verbose", action="store_true")
	parser.add_argument("-d", "--debug", help="be even verboser", action="store_true")
	args = parser.parse_args()

	# Ensure that the given document root ends with /
	# Ensure that the given document root ends with /
	args.docroot = os.path.abspath(args.docroot) + os.sep
	if not os.path.exists(args.docroot):
		sys.stderr.write("Document root not found: '%s'%s" % (args.docroot, os.linesep))
		sys.exit(1)

	# This must be configured before any logger is initialized
	if args.debug:
		logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
	elif args.verbose:
		logging.basicConfig(stream=sys.stdout, level=logging.INFO)
	else:
		logging.basicConfig(stream=sys.stdout, level=logging.WARN)
	
	LOGGER = logging.getLogger(__name__)

	# This must be imported AFTER logging has been configured!
	from cp750 import Client
	from cp750 import Frontend

	# Start application (and ensure it can be killed with CTRL-C)
	signal.signal(signal.SIGINT, signal.SIG_DFL)
	app = QApplication(sys.argv)
	app.setApplicationName("CP750 Volume Client")
	#app.setWindowIcon(QIcon(args.docroot + "img" + os.sep + "icon.svg"))

	client = Client(args)
	frontend = Frontend(args, client)

	if args.stayontop:
		LOGGER.info("Enable WindowStayOnTop")
		frontend.setWindowFlags(int(frontend.windowFlags()) | Qt.WindowStaysOnTopHint)

	if args.fullscreen:
		LOGGER.info("Fullscreen mode")
		frontend.showFullScreen()
	else:
		frontend.show()

	sys.exit(app.exec_())

if __name__ == "__main__":
	main()

#  vim: set fenc=utf-8 ts=4 sw=4 noet :
