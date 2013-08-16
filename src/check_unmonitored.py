#!/bin/env python
"""
It is sometimes neccessary to temporarily disable monitoring on a given host
in Zabbix. But it's possible to forget to re-enable monitoring after the need
to disable it has passed.  While maintenance periods can be set, they are
sometimes not flexible enough. So, to alert us if a host is left in unmonitored
state too long, we present forgetmentnot.

The scope is simple, check zabbix for unmonitored hosts that don't belong to a
whitelist of host hostgroups. (in our case, decommissioned, and spare_servers)
Alerting if any unmonitored hosts not in the whitelist groups remain in
unmonitored state for longer than a configurable amount (set to 24 hrs by
default)
"""
author = 'Jim Richardson <weaselkeeper@gmail.com>'



# Imports

# Stock imports
from ConfigParser import SafeConfigParser
import logging

# script specific imports.
import time
import os
import sys
import tempfile
import MySQLdb as db

CONFIGFILE = '/tmp/config'

def get_config():
    """ if a config file exists, read and parse it.
    Override with the get_options function, and any relevant environment
    variables.
    Config file is in ConfigParser format

    Configfile has the following sections
    [ZabbixDB]
    DBHOST = fqdn
    DBNAME = name of database
    DBUSER = username
    DBPASS = password

    """

    parser = SafeConfigParser()
    configuration = {}
    if os.path.isfile(CONFIGFILE):
        config = CONFIGFILE
    else:
        log.warn('No config file found at %s Aborting' % CONFIGFILE)
        sys.exit(1)
    parser.read(config)
    try:
        configuration['server'] = parser.get('ZabbixDB', 'DBHOST')
        configuration['user']   = parser.get('ZabbixDB', 'DBUSER')
        configuration['db']     = parser.get('ZabbixDB', 'DBNAME')
        configuration['pass']   = parser.get('ZabbixDB', 'DBPASS')
        configuration['whitelist'] = parser.get('ZabbixDB', 'WHITELIST').split(',')
    except:
        log.warn('something wrong with the config file? ')
        sys.exit(1)
    return configuration


def get_db(configuration):
    """ Try connecting to relevant database on host, with user/pass
    Error out if something bad happens, return DB object if successful"""
    try:
        con = db.connect(host = configuration['server'],
                         db   = configuration['db'],
                         user = configuration['user'],
                         passwd = configuration['pass']
            )
        cur = con.cursor()
    except:
            log.warn("cannot connect to database")
            sys.exit(1)
    return cur


def query_db(sql,cur):
    # make the query, return the result
    try:
        cur.execute(sql)
        query_result = cur.fetchall()
    except:
        log.warn("something went wrong with the database query")
        sys.exit(1)
    return query_result


def pull_data(cur,whitelist=['Decommisioned','VA - spare-servers']):
    whitelist_groups =[] # start with an empty list
    for group in whitelist:
        sql_whitelist_group = ("SELECT groupid from groups where groups.name = \'%s\';") % group
        log.debug(sql_whitelist_group)
        whitelist_groups.append(query_db(sql_whitelist_group,cur))

   # get list of unmonitored hosts
    sql_unmonitored = """ SELECT hosts.hostid FROM hosts WHERE hosts.status=1; """
    unmonitored_hosts = query_db(sql_unmonitored,cur)
    for host in unmonitored_hosts:
        # Check if host is in whitelisted groups, if not, add it to the list
        # of bad hosts.
        # Check unmonitored hosts !-> whitelist
        """Some sql that takes hostid, and ensures that the host is not in groups in whitelist"""

    log.debug('whitelist group consists of %s ' % str(whitelist_groups))

def zabbix_push(hostid):
    # Having found a host that is unmonitored, but not in a whitelisted group,
    # Push that into zabbix for it to deal with.
    log.debug("Host %s has escaped monitoring, without appropriate group membership" % hostid)

if __name__ == '__main__':
    logging.basicConfig(level = logging.WARN,
                        formate='%(asctime)s %(levelname)s - %(message)s',
                        datefmt='%y.%m.%d %H:%M:%S'
                        )
    console = logging.StreamHandler(sys.stderr)
    console.setLevel(logging.WARN)
    logging.getLogger('check_unmonitored').addHandler(console)
    log = logging.getLogger('check_unmonitored')

    _config = get_config()
    db = pull_data(get_db(_config))
