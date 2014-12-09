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


# Setup a couple variables.
pushover_host = 'api.pushover.net'
pushover_port = 443

class Cerberus(object):
    """ Instantiates a Cerberus object, use it to send notifications """
    log.debug('In class Cerberus')

    def __init__(self):
        self.host, self.port = pushover_host, pushover_port

    def run(self, _options):
        """ Do, whatever it is, we do. """
        # parse config
        conn = httplib.HTTPSConnection(self.host, self.port)
        conn.request("POST", "/1/messages.json",
                     urllib.urlencode(_options),
                     {"Content-type": "application/x-www-form-urlencoded"})
        result = conn.getresponse()
        if args.debug:
            print result
        log.debug('leaving run in Cerberus class')
        return result


def get_config(_args):
    """ Now parse the config file.  Get any and all info from config file."""
    log.debug('Now in get_config')
    parser = ConfigParser.SafeConfigParser()
    configuration = {}
    configfile = os.path.join('/etc', PROJECTNAME, PROJECTNAME + '.conf')
    if _args.config:
        _config = _args.config
    else:
        if os.path.isfile(configfile):
            _config = configfile
        else:
            log.warn('No config file found at %s', configfile)
            sys.exit(1)

    parser.read(_config)

    configuration = {}
    configuration['token'] = parser.get('pushover', 'APP_TOKEN')
    configuration['user'] = parser.get('pushover', 'USER')
    configuration['message'] = parser.get('pushover', 'message')
    configuration['priority'] = parser.get('pushover', 'PRI')

    if args.token:
        configuration['token'] = args.token
    if args.user:
        configuration['user'] = args.user
    if args.msg:
        configuration['message'] = args.msg
    if args.pri:
        configuration['priority'] = args.pri

    log.debug(configuration['message'])
    log.debug('leaving get_config')
    return configuration


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
    parser.add_argument('-m', '--msg', action='store', default=None,
                        help='Text of message')
    parser.add_argument('-p', '--pri', action='store_true',
                        help='Set high Priority')

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

    barkingDog = Cerberus()

    options = get_config(args)

    results = barkingDog.run(options)
