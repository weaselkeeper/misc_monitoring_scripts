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
Simple webcheck script. Checks for connection, and return of expected data

License: GPL V2 See LICENSE file
Author: Jim Richardson
email: weaselkeeper@gmail.com
"""

PROJECTNAME = 'webcheck'


import ConfigParser
import sys
import os
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


class webcheck(object):
    """ Basic webcheck class """
    def __init__(sel):
        """ Initialize the object"""
        log.debug('initialize')

    def run(self):
        """ Main loop, called via .run method, or via __main__ section """
        log.debug('In run()')
        parsed_config = get_config(self.args)
        session = get_session(parsed_config)

        # call webcheck here
        results = self.webcheck(session)
        log.debug('leaving run()')
        return results


    def webcheck(self, ession):
        """ Do the webcheck """
        #Do something
        result = session
        return result


def get_session(_args):
    """ Build a session and return, so we can make multiple queries if asked
    """
    log.debug('Getting session')
    _session = requests.Session()
    user, passwd = _args.username, _args.password
    _session.auth = (user, passwd)
    _session.verify = False
    log.debug('leaving get_session')
    return _session


def get_options():
    """ Parse the command line options"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Someproject does something')
    parser.add_argument('-n', '--dry-run', action='store_true',
                        help='Dry run, do not actually perform action',
                        default=False)
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Enable debugging during execution.',
                        default=None)
    parser.add_argument('-c', '--config', action='store', default=None,
                        help='Specify a path to an alternate config file')

    _args = parser.parse_args()
    _args.usage = PROJECTNAME + ".py [options]"

    return _args


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

    if _args.SOMEOPTION:
        configuration['SOMEOPTION'] = _args.SOMEOPTION
    else:
        configuration['SOMEOPTION'] = parser.get('CONFIGSECTION', 'SOMEOPTION')
    log.debug('Doing things with %s', configuration['SOMEOPTION'])
    log.debug('leaving get_config')
    return configuration


def get_args():
    """ we only run if called from main """
    _args = get_options()

    if _args.debug:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.WARN)
    return _args


# Here we start if called directly (the usual case.)
if __name__ == "__main__":
    # This is where we will begin when called from CLI. No need for argparse
    # unless being called interactively, so import it here
    args = get_args()
    # and now we can do, whatever it is, we do.
    sys.exit(run(args))