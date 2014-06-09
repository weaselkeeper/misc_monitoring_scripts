#!/usr/bin/env python
###
# Copyright (c) 2013, Jim Richardson <weaselkeeper@gmail.com>
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
Very basic monitoring script for a small scala app.

To add more monitors, edit the "monitors" section, it should be pretty self
explanatory.  But you may need to grab the metrics page to figure out what the
item you want to monitor is called.  With a bit more time, could easily make a
config file to parse for this.

Run this via cron every (n) minutes.  Ensure the MAILTO variable is set in cron
to "" lest you be inundated with a swarm of "all's well" messages.

"""
import smtplib
import sys
import json
import urllib
import logging


logging.basicConfig(level=logging.WARN,
                    format='%(asctime)s %(levelname)s - %(message)s',
                    datefmt='%y.%m.%d %H:%M:%S'
                    )
console = logging.StreamHandler(sys.stderr)
console.setLevel(logging.WARN)
logging.getLogger("webcheck").addHandler(console)
log = logging.getLogger("webcheck")

MAILTO = '<EMAIL-ADDRESS>'
MAILFROM = 'monitor@somewhere.com'
MONITOR_URL = 'http://localhost:8081/metrics'
    # Sample monitor url. Set
    # appropriately

# Setting NOREPORT will stop emails from being sent.  Prevents being inundated
# with annoying mails during test and dev
# NOREPORT enabled by default for now.
# Can also be set at invocation with the nopreport option
NOREPORT = 1

def mail_alerts(msg):
    """ if to send, who to send to and how """
    server = smtplib.SMTP('localhost')
    server.set_debuglevel(1)
    try:
        if NOREPORT == 0:
            server.sendmail(MAILFROM, MAILTO, msg)
        else:
            log.warn("test Message %s", msg)
    except NameError:
        log.warn('failure, we should do something about this.')
    server.quit()

# Monitors.  Edit this to add new or change old.
#
def checks(webdata):
    """ perform the relevant check """
    _checks = {}
    alert_vals = {}
    _checks['daemon_thread_count'] = webdata['jvm']['daemon_thread_count']
    alert_vals['daemon_thread_count'] = 1

    _checks['p999'] = webdata['de.leibert.ExampleResource']['sayHello']['duration']['p999']
    alert_vals['p999'] = 5

    _checks['percent_4xx_15m'] = webdata['org.eclipse.jetty.servlet.ServletContextHandler']['percent-4xx-15m']['value']
    alert_vals['percent_4xx_15m'] = 0.4


    for key in _checks.keys():
        if _checks[key] > alert_vals[key]:
            msg = "Error: %s currently at %d" % (key, alert_vals[key])
            mail_alerts(msg)
        else:
            print 'all\'s well with %s' % key


def run():
    """ Start here """
    try:
        data = urllib.urlopen(MONITOR_URL).read()
    except IOError:
        msg = "Error: Server unresponsive"
        mail_alerts(msg)
        sys.exit(1)
    webdata = json.loads(data)
    checks(webdata)


def get_options():
    """ command-line options """
    parser = argparse.ArgumentParser(description='Pass cli options to \
        script')

    parser.add_argument('-n', '--noreport', action="store_true",
                        default=False, help='run the check, but do not trigger\
                         a report')

    parser.add_argument('-d', '--debug', action="store_true", default=False)

    _args = parser.parse_args()
    _args.usage = "clone_repo.py [options]"
    return _args



if __name__ == '__main__':

    import argparse
    args = get_options()

    if args.debug:
        log.setLevel(logging.DEBUG)

    if args.noreport:
        log.info(args)
        log.warn('do not report')
        NOREPORT = 1

    sys.exit(run())

