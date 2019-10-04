'''
Simple script to poll WR-LEN endpoints by hostname and
write stats to redis
'''
def main():
    import socket
    import argparse
    import redis
    from hera_wr_cm.wr_len import WrLen

    parser = argparse.ArgumentParser(description='VUART shell for WR-LEN')
    parser.add_argument('hosts', metavar='hosts', type=str, nargs='*',
                    help='WR hosts to poll. Default: heraNode{0..32}wr')
    parser.add_argument('-t', dest='polltime', type=float, default=30,
                    help='Minimum time between polling cycles in seconds. Default: 30s')
    r = redis.Redis('redishost')

    args = parser.parse_args()
    
    if len(args.hosts) == 0:
        hosts = ['heraNode%dwr' % x for x in range(32)]
    else:
        hosts = args.hosts

    print('Begging WR-LEN status polling. Hosts are:')
    print(hosts)
    while(True):
        start_time = time.time()
        for host in hosts:
            try:
                ip = socket.gethostbyname(host)
            except socket.gaierror:
                continue
            wr = WrLen(host)
            stats = wr.process_stats()
            r.hmset('status:wr:%s' % wr.host, stats)
        extra_wait = args.polltime - (time.time() - start_time)
        if extra_wait > 0:
            time.sleep(extra_wait)

if __name__ == '__main__':
    main()
