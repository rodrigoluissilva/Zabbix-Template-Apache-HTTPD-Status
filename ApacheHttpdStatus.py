#!/usr/bin/env python
"""Collect Apache statistics using mod_status"""

__author__ = "Rodrigo Silva"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Rodrigo Silva"
__email__ = "rsilva.14@gmail.com"
__status__ = "Production"

import os
import time
import json
import urllib2
import argparse
import tempfile
from hashlib import sha1


class ZabbixApacheCheck(object):

    def __init__(self, url, cache_ttl=60, timeout=5):
        self.url = url + "?auto"
        self.cache_ttl = cache_ttl
        self.timeout = timeout
        self.metrics = {}
        self.error = ""
        self.metrics_cache_file = os.path.join(tempfile.gettempdir(),
                                               "zabbix_" + os.path.basename(__file__)
                                               + "-" + sha1(args.url).hexdigest() + "-tmp.json"
                                              )

    def get_metrics(self):
        """Wrapper to get metrics from the correct source."""
        if self.is_valid_cache():
            return self.get_metrics_from_cache()
        else:
            return self.get_metrics_from_url()

    def is_valid_cache(self):
        """Check if the cache file is fresh."""
        return os.path.exists(self.metrics_cache_file) and \
               time.time() - os.path.getmtime(self.metrics_cache_file) < self.cache_ttl

    def get_metrics_from_cache(self):
        """Load metrics from the temporary json file."""
        try:
            with open(self.metrics_cache_file, "r") as metrics_file:
                self.metrics = json.load(metrics_file)
            return True
        except Exception as exc:
            self.error = str(exc)
            return self.get_metrics_from_url()

    def get_metrics_from_url(self):
        """Get metrics online."""

        try:
            status_page = urllib2.urlopen(self.url, timeout=self.timeout)
        except Exception as exc:
            self.error = str(exc)
            return False

        self.metrics = dict(map(str.strip, line.split(':', 1)) for line in status_page if line.count(':') > 0)

        if 'Scoreboard' in self.metrics:
            scoreboard = self.metrics.pop('Scoreboard')
            self.metrics['WaitingForConnection'] = scoreboard.count('_')
            self.metrics['StartingUp'] = scoreboard.count('S')
            self.metrics['ReadingRequest'] = scoreboard.count('R')
            self.metrics['SendingReply'] = scoreboard.count('W')
            self.metrics['KeepAlive'] = scoreboard.count('K')
            self.metrics['DNSLookup'] = scoreboard.count('D')
            self.metrics['ClosingConnection'] = scoreboard.count('C')
            self.metrics['Logging'] = scoreboard.count('L')
            self.metrics['GracefullyFinishing'] = scoreboard.count('G')
            self.metrics['IdleCleanupOfWorker'] = scoreboard.count('I')
            self.metrics['OpenSlotWithNoCurrentProcess'] = scoreboard.count('.')
            self.metrics['TotalWorkers'] = len(scoreboard)

        self.store_metrics()

        return True

    def store_metrics(self):
        """Store the result in a temporary json file."""
        try:
            with open(self.metrics_cache_file, 'w') as metrics_data_file:
                json.dump(self.metrics, metrics_data_file)
        except Exception as exc:
            self.error = str(exc)
            return False
        else:
            return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='ZabbixApacheCheck',
        description='This script collect statistics from Apache status page',
        epilog='License: GPL',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        fromfile_prefix_chars='@'
    )

    req_group = parser.add_argument_group('required arguments')

    req_group.add_argument('metric',
                           help='Metric name')
    req_group.add_argument('url',
                           help='Define a custom URL to use.[http://localhost:80/server-status]')

    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0.0',
                        help='Show version and exit')
    parser.add_argument('-t', '--timeout', nargs='?', action='store', type=int, const=5, default=5,
                        help='Set the connection timeout.')
    parser.add_argument('--cache-ttl', nargs='?', action='store', type=int, const=60, default=60,
                        help='Define the TTL for the cache file')
    parser.add_argument('--show-errors', action='store_true', default=False,
                        help='Show error message')

    args = parser.parse_args()

    apache = ZabbixApacheCheck(url=args.url, cache_ttl=args.cache_ttl, timeout=args.timeout)
    apache.get_metrics()
    print(apache.metrics.get(args.metric, "ZBX_NOTSUPPORTED"))
    print(apache.error) if args.show_errors else ''

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
