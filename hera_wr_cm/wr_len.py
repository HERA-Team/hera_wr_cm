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

    def process_ver(self):
        rv = {}
        rv['board_info_str'] = self.vuart.sendCommand('ver').decode('iso-8859-1') #OMG, actually using more than ascii!!
        for line in [x.strip() for x in rv['board_info_str'].split('\n')]:
            if line.startswith('WR Core build'):
                rv['wr_build'] = line.split(':')[-1]
            elif line.startswith('Build on'):
                rv['wr_build_date'] = line.split(':')[-1]
            elif line.startswith('WR Core build'):
                rv['wr_rom_id'] = line.split(':')[-1]
            elif line.startswith('FRU') or line.startswith('GW'):
                name, val = line.split(':', 1)
                name = name.strip().replace(' ', '_').lower()
                val = val.strip()
                rv['wr_%s' % name] = val
        rv['sw_build_date'] = self.ver_date
        return rv

    def process_stats(self):
        rv = {}
        stats = self.vuart.sendCommand('stat').decode().split('\n')
        for line in stats:
            if line.startswith('WR mode'):
                rv['mode'] = line.split(':')[-1].strip()
            elif line.startswith('wr0'):
                for var in line.lstrip('wr0 -> ').split(' '):
                    try:
                        key, val = var.split(':')
                        key = key.strip()
                        val = val.strip()
                        try:
                            #rv['wr0'][key] = int(val)
                            rv['wr0_%s' % key] = int(val)
                        except ValueError:
                            #rv['wr0'][key] = val
                            rv['wr0_%s' % key] = val
                    except ValueError:
                        pass
            elif line.startswith('wr1'):
                for var in line.lstrip('wr1 -> ').split(' '):
                    try:
                        key, val = var.split(':')
                        key = key.strip()
                        val = val.strip()
                        try:
                            rv['wr1:%s' % key] = int(val)
                        except ValueError:
                            rv['wr1:%s' % key] = val
                    except ValueError:
                        pass
            elif line.startswith('temp'):
                rv['temp'] = line.split(' ')[1]
        return rv

    def gather_keys(self):
        rv = {}
        rv.update(self.process_ver())
        rv.update(self.process_stats())
        rv['ip'] = self.ip
        rv['timestamp'] = datetime.datetime.now().isoformat()
        return rv
