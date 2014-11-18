"""
mbed SDK
Copyright (c) 2011-2013 ARM Limited

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import re
import json
import optparse
import subprocess
from prettytable import PrettyTable

from lmtools_base import LmToolsBase


class LmToolsUbuntu(LmToolsBase):
    """ LmToolsUbuntu supports mbed enabled platforms detection across Debian/Ubuntu OS family
    """

    def __init__(self):
        LmToolsBase.__init__()
        self.os_supported.append('Ubuntu')
        self.hex_uuid_pattern = "usb-[0-9a-zA-Z_-]*_([0-9a-zA-Z]*)-.*"
        self.name_link_pattern = "(usb-[0-9a-zA-Z_-]*_[0-9a-zA-Z]*-.*$)"
        self.mount_media_pattern = "^/[a-zA-Z0-9/]* on (/[a-zA-Z0-9/]*) "

    def get_dev_by_id(subdir):
        """ 'ls -oA /dev/disk/by-id/'
        """
        result = []
        cmd = 'ls -oA /dev/' + subdir + '/by-id/'
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in p.stdout.readlines():
            # print line,
            result.append(line)
        retval = p.wait()
        return result

    def get_mounts():
        """ Executes mount point
        """
        result = []
        cmd = 'mount | grep vfat'
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in p.stdout.readlines():
            result.append(line)
        retval = p.wait()
        return result
