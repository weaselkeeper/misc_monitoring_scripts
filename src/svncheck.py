#!/usr/bin/env    python
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

""" Check that the svn repo sync is working.  """
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


def test_checkout(_client, _repo, _local_test_dir):
    """ checkout our test tree """
    try:
        _client.checkout(_repo, _local_test_dir)
    except pysvn._pysvn.ClientError, error:
        print error
        sys.exit()


def show_info(_client, _local_testfile):
    """ shows the data"""
    try:
        entry = _client.info(_local_testfile)
        print 'Url:', entry.url
        #file_content = client.cat(local_testfile)
        #print file_content
    except pysvn._pysvn.ClientError, error:
        print error
        sys.exit()


def cleanup(_local_test_dir):
    """ remove the test dir, no need to have it cluttering things up """
    try:
        shutil.rmtree(_local_test_dir)
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
