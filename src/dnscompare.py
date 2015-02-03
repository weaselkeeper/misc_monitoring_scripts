#!/usr/bin/env python
# vun/l set exoabdtab:
# Copyright (c) 2014, Jim Richardson <weaselkeeper@gmail.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

"""
Simple dns resolver comparison script. Compare the result of a query between
two different resolvers, finding errors in replication, etc.

License: GPL V2 See LICENSE file
Author: Jim Richardson
email: weaselkeeper@gmail.com
"""

PROJECTNAME = 'dnscompare'


import sys
import logging
from random import shuffle

try:
    import dns.resolver
    import dns.zone
    import dns.query
except ImportError:
    print """

    please ensure availability of python-dnspython module
    Thank you.

    """
    sys.exit(1)

# Setup logging
logging.basicConfig(level=logging.WARN,
                    format='%(asctime)s %(levelname)s - %(message)s',
                    datefmt='%y.%m.%d %H:%M:%S')

# Setup logging to console.
console = logging.StreamHandler(sys.stderr)
console.setLevel(logging.WARN)
logging.getLogger(PROJECTNAME).addHandler(console)
log = logging.getLogger(PROJECTNAME)


def get_config(config):
    """ Read and parse config file"""
    log.debug("Getting config file")
    import ConfigParser
    parser = ConfigParser.SafeConfigParser()
    parser.read(config)
    args.resolver1 = parser.get('dnscompare', 'resolver1')
    args.resolver2 = parser.get('dnscompare', 'resolver2')
    args.host = parser.get('dnscompare', 'hosts').split('\n')
    args.query = parser.get('dnscompare', 'query')
    return


def get_zonelist(nameserver, domain):
    """ Query nameserver for list of records for domain, uses AXFR which must
    be enabled on nameserver for your querying host"""
    zones = dns.zone.from_xfr(dns.query.xfr(nameserver, domain))
    names = zones.nodes.keys()
    names.sort()
    for name in names:
        print zones[name].to_text(name)
    sys.exit(0)


def get_options():
    """ Parse the command line options"""
    import argparse

    parser = argparse.ArgumentParser(
        description='compare results from two dns resolvers')
    parser.add_argument('-c', '--config', action='store',
                        help='use config in file')
    parser.add_argument('-H', '--host', action='store',
                        help='host to query for')
    parser.add_argument('-n', '--dry-run', action='store_true',
                        help='Dry run, do not actually perform action',
                        default=False)
    parser.add_argument('-v', '--verbose', action='count',
                        help='Verbose output, move v means more verbose',
                        default=None)
    parser.add_argument('-f', '--resolver1', action='store',
                        help='First resolver')
    parser.add_argument('-s', '--resolver2', action='store',
                        help='Second resolver')
    parser.add_argument('-Q', '--query', action='store',
                        help='Record type to query for', default='A')
    parser.add_argument('-Z', '--zoneXfer', action='store_true',
                        help='list domains, requires -f resolver and -H domain')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='do not print results, output return code')
    parser.add_argument('-L', '--hostlist', action='store',
                        help='hostlist file to query for')
    parser.add_argument('-r', '--random', action='store_true',
                        help='Randomise query from list')

    _args = parser.parse_args()
    _args.usage = PROJECTNAME + ".py [options]"

    return _args


def get_IP(nameserver, queryhost, querytype="A"):
    """ return all the requested records for queryhost, defaults to A record"""
    log.debug("in get_IP")
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [nameserver]
    try:
        log.debug("Looking for %s from %s about %s",
                  querytype, nameserver, queryhost)
        answers = resolver.query(queryhost, querytype)
        log.debug("Got %s from %s for %s", answers, nameserver, queryhost)
    except (dns.resolver.NXDOMAIN, dns.resolver.Timeout, dns.resolver.NoAnswer) as err:
        log.debug("Can not find domain %s", err)
        answers = [None]
        log.debug("Got Nothing from %s for %s", nameserver, queryhost)
    if args.verbose:
        print nameserver, queryhost, resolver.nameservers
    IPs = []
    for rdata in answers:
        IPs.append(rdata)
    IPs.sort()
    log.debug("Leaving get_IP")
    return IPs


def answers_compare(host, answer1, answer2):
    """ compare the two answeres, bitch if they don't match"""
    if answer1 == answer2:
        if not args.quiet:
            print host, 'all good'
    else:
        if not args.quiet:
            print host, 'something not right'


def run_query(host):
    """ query for the host against both resolvers"""
    try:
        answer1 = get_IP(args.resolver1, host, args.query)
    except dns.resolver.NoAnswer:
        print "%s No answer from %s"% (host, args.resolver1)
        answer1 = None
    try:
        answer2 = get_IP(args.resolver2, host, args.query)
    except dns.resolver.NoAnswer:
        print "%s  No answer from %s" % (host, args.resolver2)
        answer2 = None
    if args.verbose:
        print answer1
        print answer2
    return answer1, answer2


def run():
    """ Being doing stuff """
    if args.hostlist:
        _list = open(args.hostlist)
        hostlist = _list.readlines()
        if args.verbose:
            print hostlist
        if args.random:
            shuffle(hostlist)

    elif type(args.host) != list:
        hostlist = [args.host, ]
    else:
        hostlist = args.host
    for host in hostlist:
        host = host.strip()
        answer1, answer2 = run_query(host)
        answers_compare(host, answer1, answer2)


# Here we start if called directly (the usual case.)
if __name__ == "__main__":
    # This is where we will begin when called from CLI. No need for argparse
    # unless being called interactively, so import it here
    args = get_options()
    if args.zoneXfer:
        get_zonelist(args.resolver1, args.host)
    if args.config:
        get_config(args.config)
    # and now we can do, whatever it is, we do.
    if args.verbose >= 2:
    # Enable debug level logging
        log.setLevel(logging.DEBUG)
        print args
    else:
        log.setLevel(logging.WARN)
    if not args.host and not args.hostlist:
        print """need a domain/host to query for e.g www.google.com
        something like:
        dnscompare.py -f 8.8.8.8 -s 8.8.4.4 -H www.google.com"""
        sys.exit(1)

    run()
