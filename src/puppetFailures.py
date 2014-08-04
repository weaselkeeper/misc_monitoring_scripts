#!/usr/bin/python
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
PROJECTNAME = 'puppetfailures'

import MySQLdb
import tempfile
import os
import sys
import subprocess
import time

from ConfigParser import SafeConfigParser
import logging

# Setup logging
logging.basicConfig(level=logging.WARN,
                    format='%(asctime)s %(levelname)s - %(message)s',
                    datefmt='%y.%m.%d %H:%M:%S')

# Setup logging to console.
console = logging.StreamHandler(sys.stderr)
console.setLevel(logging.WARN)
logging.getLogger(PROJECTNAME).addHandler(console)
log = logging.getLogger(PROJECTNAME)


def get_config(args):
    """ if a config file exists, read and parse it.
    Override with the get_options function, and any relevant environment
    variables.
    Config file is in ConfigParser format

    Configfile has the following sections
    [puppetdb]
    Z_SEND_BIN = Location of zabbix_sender on host
    Z_SEND_OPTIONS = any extra options
    Z_SEND_CONFIG  = location of zabbix_agentd.conf
    DBHOST = DB hostname
    DBPORT = port mysql is listening on
    DBUSER = username
    DBPASS = password
    DBNAME = database name, probably puppet_dashboard
    """

    def do_fail(err):
        """ do something with a caught error """
        log.debug('in get_config().do_fail(%s)', err)
        if args.debug:
            log.debug(err)
        else:
            log.warn(err)

    parser = SafeConfigParser()
    configuration = {}
    if os.path.isfile(CONFIGFILE):
        config = CONFIGFILE
    else:
        log.warn('No config file found at %s Aborting', CONFIGFILE)
        sys.exit(1)
    parser.read(config)
    try:
        configuration['server'] = parser.get('puppetdb', 'DBHOST')
        configuration['user'] = parser.get('puppetdb', 'DBUSER')
        configuration['db'] = parser.get('puppetdb', 'DBNAME')
        configuration['pass'] = parser.get('puppetdb', 'DBPASS')
        configuration['port'] = parser.get('puppetdb', 'DBPORT')
        configuration['zs_bin'] = parser.get('puppetdb', 'Z_SEND_BIN')
        configuration['zs_options'] = parser.get('puppetdb', 'Z_SEND_OPTIONS')
        configuration['zs_config'] = parser.get('puppetdb', 'Z_SEND_CONFIG')

        log.debug('config file parsed')
    except NoOptionError, e:
        do_fail(e)
    except NoSectionError, e:
        do_fail(e)
        log.warn('something wrong with the config file? ')
        sys.exit(1)
    return configuration



# create a tempfile using tempfile module, stuff the data into that, and then
# we use zabbix_sender to push items into zabbix. one big push please, we have
# almost 1000 hosts in each main environment.

zabbix_send = '/usr/bin/zabbix_sender'
zabbix_send_options = ''
zabbix_send_config = '/etc/zabbix/zabbix_agentd.conf'
zabbix_send_datafile = tempfile.mkstemp(prefix='puppetrun-', text=True)

puppet_dashboard_host = "DASHBOARDHOST"
port = 3306
user = 'user'
passwd = 'passwd'
database = 'puppet_dashboard'
time_now = int(time.time())
# Returns UTC date

DB = MySQLdb.connect(puppet_dashboard_host, user, passwd, database, port)
CONSOLE = DB.cursor()
# set the session timezone to UTC, so we don't munge the UNIX_TIMESTAMP.
CONSOLE.execute("""SET time_zone = '+00:00'""")

CONSOLE.execute("""SELECT name, UNIX_TIMESTAMP(reported_at) AS reported_at_UT
                ,status FROM nodes """)
ROWS = CONSOLE.fetchall()

print "%s rows returned." % len(ROWS)

for line in ROWS:
    secSinceRun = int(time_now - line[1])
    if secSinceRun < 0:
        # negative number implies the run is from the future, i.e. something is
        # wrong with the clock either here, or in the DB.  Puppet can't handle
        # a signed int, so set to zero.
        secSinceRun = 0
    runage = "%s puppetLastRun %i " % (line[0], secSinceRun)
    runstatus = "%s puppet_run_status  %s" % (line[0], line[2])
    os.write(zabbix_send_datafile[0], runage+'\n')
    os.write(zabbix_send_datafile[0], runstatus+'\n')

subprocess.Popen([zabbix_send, '-c', zabbix_send_config, zabbix_send_options,
                 '-i', zabbix_send_datafile[1]])
