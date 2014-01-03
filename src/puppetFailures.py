#!/usr/bin/python
# vim: set expandtab:

"""

License: GPL V2 See LICENSE file
Author: Jim Richardson
email: weaselkeeper@gmail.com

"""
PROJECTNAME = 'puppetfailures'

import MySQLdb
import tempfile
import os
import subprocess
import time

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
