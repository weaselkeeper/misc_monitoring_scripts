#!/usr/bin/env    python

import pysvn
import optparse
import sys
import shutil
import logging


def get_options():
    """ command-line options """
    usage = "usage: %prog [options]"
    optionparser = optparse.OptionParser
    parser = optionparser(usage)

    parser.add_option("-c", "--clutter", action="store_true",
        help="leave checked out testdir alone.")
    parser.add_option("-v", "--verbose", action="store_true",
        help="Extra info about stuff")
    parser.add_option("-d", "--debug", action="store_true",
        help="Set logging level to debug")
    parser.add_option("-s", "--server", action="store", type="string",
        help="SVN server")
    parser.add_option("-u", "--uri", action="store", type="string",
        help="Test target file path")
    calling_options, calling_args = parser.parse_args()

    if not calling_options.server:
        calling_options.server = "default fqdn SERVERNAME here"
    if not calling_options.uri:
        calling_options.uri = "default svn-object here"
    if calling_options.debug:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.WARN)

    return calling_options, calling_args


def test_checkout(client, repo, local_test_dir):
    """ checkout our test tree """
    try:
        client.checkout(repo, local_test_dir)
    except pysvn._pysvn.ClientError, e:
        print e
        sys.exit()


def test_commit(client, commit):
    """ commit our test file, which contains a timestamp, and no more """
    # file is located somewhere in temp, find it, touch it, and commit it.


def show_info(client, local_testfile):
    try:
        entry = client.info(local_testfile)
        print 'Url:', entry.url
        #file_content = client.cat(local_testfile)
        #print file_content
    except pysvn._pysvn.ClientError, e:
        print e
        sys.exit()


def cleanup(local_test_dir):
    """ remove the test dir, no need to have it cluttering things up """
    try:
        shutil.rmtree(local_test_dir)
    except IOError:
        logging.getLogger(" An error occured trying to cleanup test dir ")
        sys.exit(1)

if  __name__ == "__main__":
    default_log_format = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s")
    default_log_handler = logging.StreamHandler(sys.stderr)
    default_log_handler.setFormatter(default_log_format)

    log = logging.getLogger("svncheck")
    log.addHandler(default_log_handler)
    log.debug("Starting logging")

    options, args = get_options()
    client = pysvn.Client()
    repo = "https://" + options.server + options.uri
    local_test_dir = './testing'
    local_testfile = local_test_dir + '/RandomStringGen.java'
    test_checkout(client, repo, local_test_dir)
    if options.verbose:
        show_info(client, local_testfile)

    if not options.clutter:
        cleanup(local_test_dir)
