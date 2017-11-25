#!/usr/bin/env python3
"""
Dolby CP750 Client Simulation

Simulates some commands implemented by a Dolby CP750 client.

Author: Roland Tapken <roland@bitarbeiter.net>
License: MIT
"""

import socket
import sys

IFACE="127.0.0.1"
PORT=61408

def safe_int(val, fallback=None):
    try:
        return int(val)
    except ValueError:
        return fallback

class CP750:
    def __init__(self):
        self.fader = 35
        self.mute = 0
        self.input_mode = 'dig_1'

    def handle_sys_input_mode(self, dev):
        """ Values: analog | dig_1 | dig_2 | dig_3 | dig_4 | last | mic | non_sync """
        if dev in ['analog', 'dig_1', 'dig_2', 'dig_3', 'dig_4', 'last', 'mic', 'non_sync']:
            self.input_mode = dev
        return 'cp750.sys.input_mode ' + self.input_mode

    def handle_sys_fader(self, val):
        """ Expacts value between 0 and 100 """
        val=safe_int(val, -1)
        if val >= 0 and val <= 100:
            self.fader = val
        return 'cp750.sys.fader ' + str(self.fader)

    def handle_ctrl_fader_delta(self, val):
        """ Expects value between -100 and 100 """
        val=safe_int(val, 0)
        if val >= -100 and val <= 100:
            self.fader += val
            if self.fader < 0:
                val = val - self.fader
                self.fader = 0
            if self.fader > 100:
                val = val + 100 - self.fader
                self.fader = 100
        return 'cp750.ctrl.fader_delta ' + str(val)

    def handle_sys_mute(self, val):
        val = safe_int(val, -1)
        if val == 0 or val == 1:
            self.mute=val
        return 'cp750.sys.mute ' + str(self.mute)

    def handle(self, cmd, args):
        if len(args) == 0:
            if cmd == 'exit':
                return ''
            if cmd == 'help':
                return 'not implemented'
            if cmd == 'status':
                return 'not implemented'
        if len(args) == 1:
            if cmd == 'cp750.sys.input_mode':
                return self.handle_sys_input_mode(*args)
            if cmd == 'cp750.ctrl.fader_delta':
                return self.handle_ctrl_fader_delta(*args)
            if cmd == 'cp750.sys.fader':
                return self.handle_sys_fader(*args)
            if cmd == 'cp750.sys.mute':
                return self.handle_sys_mute(*args)
        return ''

cp750=CP750()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server_address = (IFACE, PORT)
    print('starting up on %s port %s' % server_address)
    server.bind(server_address)
    server.listen(1)

    while True:
        # Wait for a connection
        print('waiting for a connection')
        sock, client_address = server.accept()
        try:
            print('connection from', client_address)
            with sock.makefile('rwb', 0) as f:
                for line in f:
                    line = line.decode('UTF-8').strip()
                    print('>>>', line)
                    if line:
                        (cmd, *args) = line.split()
                        f.write(line.encode('UTF-8') + b'\r\n')
                        resp = cp750.handle(cmd, args)
                        print('<<<', resp)
                        f.write(resp.encode('UTF-8') + b'\r\n\r\n')
        finally:
            # Clean up the connection
            sock.close()
