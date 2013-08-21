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
import zabbix_api
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


def pull_data(cur,whitelist):
    whitelist_groups = [] # start with an empty list
    for group in whitelist:
        sql_whitelist_group = ("SELECT groupid from groups where groups.name = \'%s\';") % group
        whitelist_groups.append(query_db(sql_whitelist_group,cur)[0])
        log.debug(sql_whitelist_group)

   # get list of unmonitored hosts
    sql_unmonitored = """ SELECT hosts.hostid,hosts.host FROM hosts WHERE hosts.status=1; """
    check_hostlist = []
    unmonitored_hosts = query_db(sql_unmonitored,cur)
    for host in unmonitored_hosts:
        is_whitelisted = 0
        # Check if host is in whitelisted groups, if not, add it to the list
        # of bad hosts.
        # Check unmonitored hosts !-> whitelist
        check_groups = "SELECT groupid from hosts_groups where hostid=\'%s\';" % host[0]
        log.debug(check_groups)
        groups = query_db(check_groups,cur)
        for group in groups:
            if group in whitelist_groups:
                is_whitelisted = 1
        if not is_whitelisted:
            check_hostlist.append(host)
    log.debug('whitelist group consists of %s ' % str(whitelist_groups))
    log.debug('unmonitored hosts not in whitelist %s ' %  str(check_hostlist))
    return check_hostlist

def zabbix_push(host):
    # Having found a host that is unmonitored, but not in a whitelisted group,
    # Push that into zabbix for it to deal with.
    log.warn("Host %s has escaped monitoring, without appropriate group membership" % host[1])
    # Now turn monitoring on via api in zabbix, for this host.

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
    unmonitored_hosts_no_whitelist = pull_data(get_db(_config),_config['whitelist'])
    log.debug(unmonitored_hosts_no_whitelist)
    for host in unmonitored_hosts_no_whitelist:
        zabbix_push(host)
