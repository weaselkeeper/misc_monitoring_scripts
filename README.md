misc_monitoring_scripts
=======================

A few small monitoring related scripts.
URL: https://github.com/weaselkeeper/misc_monitoring_scripts

==============================================================================

puppetFailures.py
=====================

Monitor a puppet dashboard instance for puppet failures, and stuff them into 
a zabbix backend database for alerting/tracking


==============================================================================

svncheck
===========

Wrote this a while ago to test a remote svn repo mirror when the expensive svn
mirroring package we had paid too much for couldn't handle the high latency
connection to the remote DC overseas.

We've since dumped svn, and this is no longer needed.  But left it here in case
it might be useful to someone else if only as example code.

No docs, read the code :P

Not likely to make any changes to it.


=============================================================================

check_unmonitored
===========

Description: Track systems in zabbix that are in unmonitored state.
Author: Jim Richardson
Email: weaselkeeper@gmail.com
Long-Description:
  It is sometimes neccessary to temporarily disable monitoring on a given host
in Zabbix. But it's possible to forget to re-enable monitoring after the need
to disable it has passed.  While maintenance periods can be set, they are
sometimes not flexible enough. So, to alert us if a host is left in unmonitored
state too long, we present forgetmentnot.

The scope is simple, check zabbix for unmonitored hosts that don't belong to a
whitelist of host hostgroups. (in our case, decommissioned, and spare servers)
Alerting if any unmonitored hosts not in the whitelist groups remain in
unmonitored state for longer than a configurable amount (set to 24 hrs by
default)

=============================================================================

webapp-health-mon
=================

This is a standalone monitor written in python, for webapps that can return 
json data. It is meant to be simple, and to have low impact on the webserver,
(although that is mostly a matter of how the webapp handles the request).

Right now, it's pretty basic, all the checks are in the code, will be moving
that to a config file (optional) in the future.

Usage:  Simply run the monitor script, after changing MAILTO, MAILFROM and
MONTITOR_URL, as well as configuring the checks in the checks() function.

If one of the checks is triggered, an email will be sent via local mailserver
to the specified MAILTO. 

=============================================================================

cereberus.py
==================

A tool used to send alerts via pushover <https://pushover.net>

Unlike SMS and email, you know if the message was received or not.


=============================================================================

dnscompare.py
==================

Compare host lookups across two different resolvers.  Useful to check sync of
resolvers, as well as check against dns hijaking and cache poisoning.

