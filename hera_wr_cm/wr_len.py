import sys
import socket
import time, datetime

from py7slib.core.vuart import VUART_shell

class WrLen(VUART_shell):
    def __init__(self, host):
        self.host = host
        try:
            self.ip = socket.gethostbyname(self.host)
            VUART_shell.__init__(self, self.ip)
        except socket.gaierror:
            print("hostname %s not known!" % host)

    def process_stats(self):
        rv = {}
        stats = self.vuart.sendCommand('stat').decode().split('\n')
        for line in stats:
            if line.startswith('WR mode'):
                rv['mode'] = line.split(':')[-1]
            elif line.startswith('wr0'):
                #rv['wr0'] = {}
                for var in line.lstrip('wr0 -> ').split(' '):
                    try:
                        key, val = var.split(':')
                        try:
                            #rv['wr0'][key] = int(val)
                            rv['wr0:%s' % key] = int(val)
                        except ValueError:
                            #rv['wr0'][key] = val
                            rv['wr0:%s' % key] = val
                    except ValueError:
                        pass
            elif line.startswith('wr1'):
                #rv['wr1'] = {}
                for var in line.lstrip('wr1 -> ').split(' '):
                    try:
                        key, val = var.split(':')
                        try:
                            rv['wr1:%s' % key] = int(val)
                        except ValueError:
                            rv['wr1:%s' % key] = val
                    except ValueError:
                        pass
            elif line.startswith('temp'):
                rv['temp'] = line.split(' ')[1]
        rv['board_info'] = self.vuart.sendCommand('ver').decode('iso-8859-1') #OMG, actually using more than ascii!!
        rv['sw_build_date'] = self.ver_date
        rv['ip'] = self.ip
        rv['timestamp'] = datetime.datetime.now().isoformat()
        return rv
