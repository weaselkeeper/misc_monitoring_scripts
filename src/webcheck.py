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
Simple Webcheck script. Checks for connection, and return of expected data

License: GPL V2 See LICENSE file
Author: Jim Richardson
email: weaselkeeper@gmail.com
"""

PROJECTNAME = 'webcheck'


import sys
import logging

try:
    import requests
except ImportError:
    print """

    please ensure availability of python-requests module
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


def get_url(url, status_code):
    """ get the status code for a get request on url"""
    status_code = int(status_code)
    result = requests.get(url)
    RC = result.status_code
    if RC == status_code:
        print "All's well"
    else:
        print "Status code %s incorrect, expected %s" % (RC, status_code)
        sys.exit(1)


def get_options():
    """ Parse the command line options"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Someproject does something')
    parser.add_argument('-U', '--url', action='store',
                        help='full URL to check')
    parser.add_argument('-n', '--dry-run', action='store_true',
                        help='Dry run, do not actually perform action',
                        default=False)
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Enable debugging during execution.',
                        default=None)
    parser.add_argument('-u', '--username', action='store',
                        help='username for auth')
    parser.add_argument('-p', '--pass', action='store',
                        help='passwd for auth')
    parser.add_argument('-s', '--sc', action='store', default=200,
                        help='Expected http status code eg 404, 200')

    _args = parser.parse_args()
    _args.usage = PROJECTNAME + ".py [options]"

    return _args


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
    if not args.url:
        print 'need a url to query'
        sys.exit(1)
    URL, sc = args.url, args.sc
    get_url(URL, sc)
