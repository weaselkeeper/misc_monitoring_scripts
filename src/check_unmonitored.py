#!/bin/env python
"""
It is sometimes neccessary to temporarily disable monitoring on a given host
in Zabbix. But it's possible to forget to re-enable monitoring after the need
to disable it has passed.  While maintenance periods can be set, they are
sometimes not flexible enough. So, to alert us if a host is left in unmonitored
state too long, we present forgetmentnot.

The scope is simple, check zabbix for unmonitored hosts that don't belong to a
whitelist of host hostgroups. (in our case, decommissioned, and spare_servers)
When the script is run, simply re-enable any hosts that are not in the 
whitelisted groups, and are unmonitored

author 'Jim Richardson <weaselkeeper@gmail.com>'

"""


# Imports

# Stock imports
from ConfigParser import SafeConfigParser, NoSectionError, NoOptionError
import logging
import argparse

# script specific imports.
import os
import sys

# Setup logging

logging.basicConfig(level = logging.WARN,
                    formate='%(asctime)s %(levelname)s - %(message)s',
                    datefmt='%y.%m.%d %H:%M:%S'
                    )
console = logging.StreamHandler(sys.stderr)
console.setLevel(logging.WARN)
logging.getLogger('check_unmonitored').addHandler(console)
log = logging.getLogger('check_unmonitored')

try:
    import MySQLdb as db
except ImportError:
    log.warn('Unable to load MySQLdb')

if os.environ.get('ZABBIX_CHECKS_CONFIG'):
    CONFIGFILE = os.environ.get('ZABBIX_CHECKS_CONFIG')
else:
    CONFIGFILE = '/etc/zabbix/check_unmonitored.conf'


def get_options():
    """ command-line options """
    parser = argparse.ArgumentParser(description='Pass cli options to \
        script')

    parser.add_argument('-n', '--dryrun', action="store_true",
                        default=False, help='Dry run will report what it \
                        would do, but makes no changes to the DB')

    parser.add_argument('-d', '--debug', action="store_true", default=False)

    parser.add_argument('-c', '--config', action='store')

    _args = parser.parse_args()
    _args.usage = "check_unmonitored.py [options]"
    return _args




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
    WHITELIST = comma seperated list of whitelist groups
    """

    def do_fail(err):
        """ do something with a caught error """
        log.debug('in get_config().do_fail(%s)' % err)
        if args.debug:
            log.debug(err)
        else:
            log.warn(err)

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
        log.debug('config file parsed')
    except NoOptionError, e:
        do_fail(e)
    except NoSectionError, e:
        do_fail(e)
        log.warn('something wrong with the config file? ')
        sys.exit(1)
    return configuration


def get_db(configuration):
    """ Try connecting to relevant database on host, with user/pass
    Error out if something bad happens, return DB object if successful"""
    log.debug('entering get_db()')
    try:
        _con = db.connect(host = configuration['server'],
                         db   = configuration['db'],
                         user = configuration['user'],
                         passwd = configuration['pass']
            )
        log.debug('db connection made')
    except:
        log.warn("cannot connect to database")
        log.debug('erroring out of get_db()')
        sys.exit(1)
    log.debug('leaving get_db()')
    return _con


def query_db(sql, _con):
    """  make the query, return the result
     passing con and opening a cursor each time is not efficient """
    log.debug('entering query_db()')
    try:
        cur = _con.cursor()
        cur.execute(sql)
        log.debug(sql)
        query_result = cur.fetchall()
    except:
        log.warn("something went wrong with the database query")
        sys.exit(1)
        _con.rollback()
    _con.commit()
    cur.close()
    log.debug('leaving query_db()')
    return query_result


def pull_data(_con, whitelist):
    log.debug('entering pull_data()')
    whitelist_groups = [] # start with an empty list
    for group in whitelist:
        sql_whitelist_group = ("SELECT groupid from groups where groups.name = \'%s\';") % group
        whitelist_groups.append(query_db(sql_whitelist_group, con)[0])

   # get list of unmonitored hosts
    sql_unmonitored = """ SELECT hosts.hostid, hosts.host FROM hosts WHERE hosts.status=1; """
    check_hostlist = []
    unmonitored_hosts = query_db(sql_unmonitored, con)
    for _host in unmonitored_hosts:
        is_whitelisted = 0
        # Check if host is in whitelisted groups, if not, add it to the list
        # of bad hosts.
        # Check unmonitored hosts !-> whitelist
        check_groups = "SELECT groupid from hosts_groups where hostid=\'%s\';" % _host[0]
        groups = query_db(check_groups, _con)
        for group in groups:
            if group in whitelist_groups:
                is_whitelisted = 1
        if not is_whitelisted:
            check_hostlist.append(_host)
    log.debug('whitelist group consists of %s ' % str(whitelist_groups))
    log.debug('unmonitored hosts not in whitelist %s ' %  str(check_hostlist))
    log.debug('leaving pull_data()')
    return check_hostlist


def zabbix_push(_host, _con):
    """ Having found a host that is unmonitored, but not in a whitelisted group,
     Push that into zabbix for it to deal with."""
    log.debug('entering zabbix_push')
    log.debug("Host %s has escaped monitoring, without appropriate group membership" % _host[1])
    # Now turn monitoring on via mysql connection, in zabbix, for this host.
    # FIXME  move this functionality to zabbix api
    Enable_Monitoring = "UPDATE hosts SET status=0 where hosts.hostid=\'%s\';" % _host[0]
    query_db(Enable_Monitoring, _con)
    log.debug(Enable_Monitoring)
    log.debug('leaving zabbix_push()')

if __name__ == '__main__':
    args = get_options()
    if args.debug:
        log.setLevel(logging.DEBUG)


    _config = get_config()
    con = get_db(_config)
    cur = con.cursor()
    unmonitored_hosts_no_whitelist = pull_data(con, _config['whitelist'])
    log.debug(unmonitored_hosts_no_whitelist)
    for host in unmonitored_hosts_no_whitelist:
        zabbix_push(host, con)

