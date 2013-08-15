#!/usr/bin/env python

__docstring__ ="""
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
import json,urllib

MAILTO = '<EMAIL-ADDRESS>'
MAILFROM = 'monitor@somewhere.com'
MONITOR_URL='http://localhost:8081/metrics'; 
    # Sample monitor url. Set
    # appropriately

# Setting DEBUG will stop emails from being sent.  Prevents being inundated
# with annoying mails during test and dev
# DEBUG enabled by default for now.
DEBUG=1

def mail_alerts(msg):
    server = smtplib.SMTP('localhost')
    server.set_debuglevel(1)
    try:
        if DEBUG == 0:
            server.sendmail(MAILFROM, MAILTO, msg)
        else:
            print "test Message %s" % msg
    except:
        print 'failure, we should do something about this.'
    server.quit()

# Monitors.  Edit this to add new or change old.
#
def checks(webdata):
    checks = {}
    alert_vals = {}
    checks['daemon_thread_count'] = webdata['jvm']['daemon_thread_count']
    alert_vals['daemon_thread_count'] = 1

    checks['p999'] = webdata['de.leibert.ExampleResource']['sayHello']['duration']['p999']
    alert_vals['p999'] = 5

    checks['percent_4xx_15m'] = webdata['org.eclipse.jetty.servlet.ServletContextHandler']['percent-4xx-15m']['value']
    alert_vals['percent_4xx_15m'] = 0.4


    for key in checks.keys():
        if checks[key] > alert_vals[key]:
            msg = "error condition with %s currently at %d" % (key, alert_vals[key])
            mail_alerts(msg)
        else:
            print 'all\'s well with %s' % key


def main():
    try:
        data = urllib.urlopen(MONITOR_URL).read()
    except IOError:
        msg = "something went wrong.  It's likely the server process you are trying to monitor is offline"
        mail_alerts(msg)
        sys.exit(1)
    webdata = json.loads(data)
    checks(webdata)



if __name__ == '__main__':
    main()

