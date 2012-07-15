#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2012 Mats Ekberg
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
The purpose of this tool is to provide a simple example on how to
independently verify the contents of a Boar repository by taking
advantage of manifest files.
"""

import commands
import json
import re
import sys

def run_command(cmd):
    """Execute a shell command and return the output. Raises an
    exception if the command failed for any reason."""
    status, output = commands.getstatusoutput(cmd)
    if status:
        print output
        raise Exception("Command '%s' failed with error %s" % 
                        (cmd, status))
    return output

def verify_blob(repourl, expected_md5):
    line = run_command("boar --repo='%s' cat --blob %s | md5sum -" % 
                       (repourl, expected_md5))
    calculated_md5 = line[0:32]
    assert calculated_md5 == expected_md5

def verify_manifest(repourl, session_name, manifest_path):
    print "Verifying manifest", session_name, manifest_path
    manifest_contents = run_command("boar --repo='%s' cat '%s/%s'" % 
                                    (repourl, session_name, manifest_path))
    for line in manifest_contents.splitlines():
        md5, filename = line[0:32], line[34:]
        verify_blob(repourl, md5)
        print filename, "OK"

def is_manifest(filename):
    """Returns True if a filename looks like a manifest file that this
    program will understand."""
    m = re.match("(^|.*/)(manifest-md5\.txt|manifest-([a-z0-9]{32})\.md5)", 
                 filename, flags=re.IGNORECASE)
    return m != None

def main():
    args = sys.argv[1:]
    if len(args) != 1:
        print "Usage: verify-manifests-simple.py <repository>"
        return
    repourl = args.pop(0)
    session_names = json.loads(run_command("boar sessions --json"))
    for session_name in session_names:
        session_contents = json.loads(run_command("boar --repo='%s' contents '%s'" % 
                                                  (repourl, session_name)))
        for fileinfo in session_contents['files']:
            if is_manifest(fileinfo['filename']):
                verify_manifest(repourl, session_name, fileinfo['filename'])

main()