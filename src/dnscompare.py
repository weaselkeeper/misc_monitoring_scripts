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
try:
    import dns.resolver
except ImportError:
    print """

    please ensure availability of python-dns module
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


def get_options():
    """ Parse the command line options"""
    import argparse

    parser = argparse.ArgumentParser(
        description='compare results from two dns resolvers')
    parser.add_argument('-H', '--host', action='store',
                        help='host to query for')
    parser.add_argument('-n', '--dry-run', action='store_true',
                        help='Dry run, do not actually perform action',
                        default=False)
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Enable debugging during execution.',
                        default=None)
    parser.add_argument('-f', '--resolver1', action='store',
                        help='First resolver')
    parser.add_argument('-s', '--resolver2', action='store',
                        help='Second resolver')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='do not print results, simply exit w/rc')


    _args = parser.parse_args()
    _args.usage = PROJECTNAME + ".py [options]"

    return _args


def get_IP(nameserver, queryhost):
    """ return all the A records for queryhost, from nameserver"""
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [nameserver]
    answers = resolver.query(queryhost, 'A')
    if args.debug:
        print nameserver, queryhost, resolver.nameservers
    IPs = []
    for rdata in answers:
        IPs.append(rdata)
    IPs.sort()
    return IPs


def answers_compare(answer1, answer2):
    if answer1 == answer2:
        if not args.quiet:
            print 'all good'
        sys.exit(0)
    else:
        if not args.quiet:
            print 'something not right'
        sys.exit(1)

# Here we start if called directly (the usual case.)
if __name__ == "__main__":
    # This is where we will begin when called from CLI. No need for argparse
    # unless being called interactively, so import it here
    args = get_options()
    # and now we can do, whatever it is, we do.
    if args.debug:
        log.setLevel(logging.DEBUG)
        print args
    else:
        log.setLevel(logging.WARN)
    if not args.host:
        print """need a domain/host to query for e.g www.google.com
        something like:
        dnscompare.py -f 8.8.8.8 -s 8.8.4.4 -H www.google.com"""
        sys.exit(1)
    answer1 = get_IP(args.resolver1, args.host)
    answer2 = get_IP(args.resolver2, args.host)
    if args.debug:
        print answer1
        print answer2
    answers_compare(answer1, answer2)

