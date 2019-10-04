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
    parser.add_argument('hosts', metavar='hosts', type=str, nargs='+',
                    help='WR hosts to poll')
    r = redis.Redis('redishost')

    args = parser.parse_args()

    for host in args.hosts:
        print('Getting stats for %s' % host)
        try:
            ip = socket.gethostbyname(host)
        except socket.gaierror:
            print('Unknown host. Skipping')
            continue
        wr = WrLen(host)
        stats = wr.process_stats()
        r.hmset('status:wr:%s' % wr.host, stats)


if __name__ == '__main__':
    main()
