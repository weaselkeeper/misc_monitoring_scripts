#!/usr/bin/env python
# vim: set expandtab:
###
# Copyright (c) 2012, Jim Richardson <weaselkeeper@gmail.com>
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

License: GPL V2 See LICENSE file
Author: Jim Richardson
email: weaselkeeper@gmail.com

"""
PROJECTNAME = 'cerberus'
import os
import sys
import ConfigParser
import logging
import httplib
import urllib


# Setup logging
logging.basicConfig(level=logging.WARN,
                    format='%(asctime)s %(levelname)s - %(message)s',
                    datefmt='%y.%m.%d %H:%M:%S')

# Setup logging to console.
console = logging.StreamHandler(sys.stderr)
console.setLevel(logging.WARN)
logging.getLogger(PROJECTNAME).addHandler(console)
log = logging.getLogger(PROJECTNAME)

class cerberus(object):
    """ Instantiates a cerberus object,us it to send notifications """
    log.debug('In class Cerberus')


    def __init__(self):
        host, port = 'api.pushover.net', 443

    def run(self, _args):
        """ Do, whatever it is, we do. """
        # parse config
        conn = httplib.HTTPSConnection('api.pushover.net:443')
        conn.request("POST", "/1/messages.json",
            urllib.urlencode({
                "token": _args.token,
                "user": _args.user,
                "message": _args.msg
            }), {"Content-type": "application/x-www-form-urlencoded"})
        conn.getresponse()
        log.debug((_args))
        return


def get_options():
    """ Parse the command line options"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Cerberus alerts you')
    parser.add_argument('-n', '--dry-run', action='store_true',
                        help='Dry run, do not actually perform action',
                        default=False)
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Enable debugging during execution.',
                        default=None)
    parser.add_argument('-r', '--readable', action='store_true', default=False,
                        help='Display output in human readable formant.')
    parser.add_argument('-c', '--config', action='store', default=None,
                        help='Specify a path to an alternate config file')
    parser.add_argument('-u', '--user', action='store', default=None,
                        help='user key')
    parser.add_argument('-t', '--token', action='store', default=None,
                        help='application token')
    parser.add_argument('-m', '--msg', action='store', default='Alert!',
                        help='Text of message')

    _args = parser.parse_args()
    _args.usage = PROJECTNAME + ".py [options]"

    return _args

if __name__ == "__main__":
    # This is where we will begin when called from CLI. No need for argparse
    # unless being called interactively, so import it here
    args = get_options()

    if args.debug:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.WARN)

        # and now we can do, whatever it is, we do.
    barkingDog = cerberus()
    barkingDog.run(args)
