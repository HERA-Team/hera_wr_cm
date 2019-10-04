'''
Simple script to poll WR-LEN endpoints by hostname and
write stats to redis
'''

def main():
    import socket
    import argparse
    import redis
    import time
    import datetime
    import os
    from hera_wr_cm.wr_len import WrLen
    from hera_wr_cm import __version__

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
    script_redis_key = "status:script:%s" % __file__
    while(True):
        r.set(script_redis_key, "alive", ex=max(180, args.polltime* 2))
        r.hmset("version:%s:%s" % (__package__, os.path.basename(__file__)), {"version":__version__, "timestamp":datetime.datetime.now().isoformat()})
        start_time = time.time()
        for host in hosts:
            hash_key = 'status:wr:%s' % host
            try:
                ip = socket.gethostbyname(host)
            except socket.gaierror:
                continue
            wr = WrLen(host)
            stats = wr.gather_keys()
            r.hmset(hash_key, stats)
            # Delete old keys in case there is some weird stale stuff
            old_keys = [k for k in r.hkeys(hash_key) if k not in stats.keys()]
            r.hdel(hash_key, *old_keys)
        extra_wait = args.polltime - (time.time() - start_time)
        if extra_wait > 0:
            time.sleep(extra_wait)

if __name__ == '__main__':
    main()
