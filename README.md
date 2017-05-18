# README
<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table Contents**

- [#misc_monitoring_scripts](#misc_monitoring_scripts)
- [#puppetFailures.py](#puppetfailurespy)
- [#svncheck](#svncheck)
- [#check_unmonitored](#check_unmonitored)
- [#webapp_monitor.py](#webapp_monitorpy)
- [#cereberus.py](#cereberuspy)
- [#dnscompare.py](#dnscomparepy)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->
# misc_monitoring_scripts

A few small monitoring related scripts.
URL: https://github.com/weaselkeeper/misc_monitoring_scripts


# puppetFailures.py

Monitor a puppet dashboard instance for puppet failures, and stuff them into 
a zabbix backend database for alerting/tracking



# svncheck

Wrote this a while ago to test a remote svn repo mirror when the expensive svn
mirroring package we had paid too much for couldn't handle the high latency
connection to the remote DC overseas.

We've since dumped svn, and this is no longer needed.  But left it here in case
it might be useful to someone else if only as example code.

No docs, read the code :P

Not likely to make any changes to it.


```
Usage: svncheck.py [options]

Options:
  -h, --help            show this help message and exit
  -c, --clutter         leave checked out testdir alone.
  -v, --verbose         Extra info about stuff
  -d, --debug           Set logging level to debug
  -s SERVER, --server=SERVER
                        SVN server
  -u URI, --uri=URI     Test target file path
```

=============================================================================

#check_unmonitored
===========

Description: Track systems in zabbix that are in unmonitored state.

  It is sometimes neccessary to temporarily disable monitoring on a given host
in Zabbix. But it's possible to forget to re-enable monitoring after the need
to disable it has passed.  While maintenance periods can be set, they are
sometimes not flexible enough. So, to alert us if a host is left in unmonitored
state too long, we present forgetmenot.

The scope is simple, check zabbix for unmonitored hosts that don't belong to a
whitelist of host hostgroups. (in our case, decommissioned, and spare servers)
Re-enabling monitoring  if any unmonitored hosts not in the whitelist groups
remain in unmonitored state for longer than a configurable amount (set to 24
hrs by default)

```
usage: check_unmonitored.py [-h] [-n] [-d] [-c CONFIG]

Pass cli options to script

optional arguments:
  -h, --help            show this help message and exit
  -n, --dryrun          Dry run will report what it would do, but makes no
                        changes to the DB
  -d, --debug
  -c CONFIG, --config CONFIG
```

=============================================================================

#webapp_monitor.py
=================

This is a standalone monitor written in python, for webapps that can return 
json data. It is meant to be simple, and to have low impact on the webserver,
(although that is mostly a matter of how the webapp handles the request).

Right now, it's pretty basic, all the checks are in the code, will be moving
that to a config file (optional) in the future.

Usage:  Simply run the monitor script, after changing MAILTO, MAILFROM and
MONITOR_URL, as well as configuring the checks in the checks() function.

If one of the checks is triggered, an email will be sent via local mailserver
to the specified MAILTO. 

```

usage: webapp_monitor.py [-h] [-n] [-d]

Pass cli options to script

optional arguments:
  -h, --help      show this help message and exit
  -n, --noreport  run the check, but do not trigger a report
  -d, --debug

```

=============================================================================

#cereberus.py
==================

A tool used to send alerts via pushover <https://pushover.net>

Unlike SMS and email, you know if the message was received or not.


```
usage: cerberus.py [-h] [-n] [-d] [-r] [-c CONFIG] [-u USER] [-t TOKEN]
                   [-m MSG] [-p]

Cerberus alerts you

optional arguments:
  -h, --help            show this help message and exit
  -n, --dry-run         Dry run, do not actually perform action
  -d, --debug           Enable debugging during execution.
  -r, --readable        Display output in human readable formant.
  -c CONFIG, --config CONFIG
                        Specify a path to an alternate config file
  -u USER, --user USER  user key
  -t TOKEN, --token TOKEN
                        application token
  -m MSG, --msg MSG     Text of message
  -p, --pri             Set high Priority
```

=============================================================================

#dnscompare.py
==================

Compare host lookups across two different resolvers.  Useful to check sync of
resolvers, as well as check against dns hijacking and cache poisoning.

compare results from two dns resolvers

```
optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        use config in file
  -H HOST, --host HOST  host to query for
  -n, --dry-run         Dry run, do not actually perform action
  -v, --verbose         Verbose output, move v means more verbose
  -f RESOLVER1, --resolver1 RESOLVER1 (IP only, does not lookup DNS entry)
                        First resolver
  -s RESOLVER2, --resolver2 RESOLVER2 (IP only, does not lookup DNS entry) 
                        Second resolver
  -Q QUERY, --query QUERY
                        Record type to query for
  -Z, --zoneXfer        list domains, requires -f resolver and -H domain Also,
                        zone xfer must be enabled on resolver
  -q, --quiet           do not print results, output return code
  -L HOSTLIST, --hostlist HOSTLIST
                        hostlist file to query for
  -r, --random          Randomise query from list
  -d DELAY, --delay DELAY
                        Insert a delay in ms between each request
  --nofollow            Do not follow cnames when resolving, just return info
                        for the cname, do not get info for A record.
```
